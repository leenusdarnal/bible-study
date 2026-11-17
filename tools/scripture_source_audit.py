#!/usr/bin/env python3
"""Audit official eBible.org WEBP and KJV USFM archives.

The tool records archive hashes and metadata, checks ZIP integrity and safe paths,
and inventories USFM book IDs, chapter/verse markers, versions and marker counts.
It does not publish, transform or retain parsed Scripture text in its reports.
Only Python's standard library is required.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import stat
import sys
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any

EXPECTED_CORE_BOOKS = set("""
GEN EXO LEV NUM DEU JOS JDG RUT 1SA 2SA 1KI 2KI 1CH 2CH EZR NEH EST JOB
PSA PRO ECC SNG ISA JER LAM EZK DAN HOS JOL AMO OBA JON MIC NAM HAB ZEP
HAG ZEC MAL MAT MRK LUK JHN ACT ROM 1CO 2CO GAL EPH PHP COL 1TH 2TH 1TI
2TI TIT PHM HEB JAS 1PE 2PE 1JN 2JN 3JN JUD REV
""".split())

SOURCES = {
    "engwebp": {
        "name": "World English Bible Protestant Edition",
        "url": "https://ebible.org/Scriptures/engwebp_usfm.zip",
        "expected_directory_size_bytes": 2_908_410,
        "directory_last_modified": "2026-11-17 01:18:23",
        "expected_core_books": 66,
    },
    "eng-kjv": {
        "name": "King James Version, 1769 standardised text (with Apocrypha/Deuterocanon)",
        "url": "https://ebible.org/Scriptures/eng-kjv_usfm.zip",
        "expected_directory_size_bytes": 2_771_068,
        "directory_last_modified": "2026-11-15 09:36:58",
        "expected_core_books": 66,
    },
}

MAX_ARCHIVE_BYTES = 30 * 1024 * 1024
MAX_MEMBER_BYTES = 20 * 1024 * 1024
MAX_TOTAL_UNCOMPRESSED_BYTES = 200 * 1024 * 1024
MAX_MEMBERS = 2_000
USFM_FILE_SUFFIXES = {".usfm", ".sfm"}
MARKER_RE = re.compile(r"\\([A-Za-z0-9+]+)(\*)?")
ID_RE = re.compile(r"^\s*\\id\s+([A-Za-z0-9]{3})\b", re.IGNORECASE)
USFM_VERSION_RE = re.compile(r"^\s*\\usfm\s+([0-9]+(?:\.[0-9]+)*)\b")
CHAPTER_RE = re.compile(r"^\s*\\c\s+(\S+)")
VERSE_RE = re.compile(r"^\s*\\v\s+(\S+)")


class AuditError(RuntimeError):
    """Raised when a source archive cannot be safely or reliably audited."""


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def parse_usfm_text(text: str, member_name: str = "") -> dict[str, Any]:
    """Parse structural USFM markers only; never return verse wording."""
    versions: set[str] = set()
    markers: Counter[str] = Counter()
    books: dict[str, dict[str, Any]] = {}
    current_book: str | None = None
    current_chapter: str | None = None
    file_ids: list[str] = []

    for line in text.splitlines():
        version_match = USFM_VERSION_RE.match(line)
        if version_match:
            versions.add(version_match.group(1))

        for marker_match in MARKER_RE.finditer(line):
            markers[marker_match.group(1)] += 1

        id_match = ID_RE.match(line)
        if id_match:
            current_book = id_match.group(1).upper()
            current_chapter = None
            file_ids.append(current_book)
            books.setdefault(current_book, {
                "chapters": set(),
                "verse_labels": set(),
                "verse_address_occurrences": [],
                "verse_marker_count": 0,
                "verse_range_marker_count": 0,
                "member_names": set(),
            })
            books[current_book]["member_names"].add(member_name)
            continue

        if not current_book:
            continue

        chapter_match = CHAPTER_RE.match(line)
        if chapter_match:
            current_chapter = chapter_match.group(1)
            books[current_book]["chapters"].add(current_chapter)
            continue

        verse_match = VERSE_RE.match(line)
        if verse_match:
            label = verse_match.group(1)
            books[current_book]["verse_marker_count"] += 1
            books[current_book]["verse_labels"].add((current_chapter or "", label))
            books[current_book]["verse_address_occurrences"].append((current_chapter or "", label))
            if "-" in label:
                books[current_book]["verse_range_marker_count"] += 1

    return {
        "usfm_versions": sorted(versions),
        "book_ids_in_member": file_ids,
        "books": books,
        "marker_counts": markers,
    }


def _validate_member_path(info: zipfile.ZipInfo) -> None:
    raw_name = info.filename.replace("\\", "/")
    path = PurePosixPath(raw_name)
    if path.is_absolute() or any(part in {"..", ""} for part in path.parts):
        raise AuditError(f"Unsafe ZIP member path: {info.filename!r}")
    unix_mode = (info.external_attr >> 16) & 0xFFFF
    if stat.S_ISLNK(unix_mode):
        raise AuditError(f"Symbolic links are not allowed in the source ZIP: {info.filename!r}")
    if info.file_size > MAX_MEMBER_BYTES:
        raise AuditError(f"ZIP member exceeds size limit: {info.filename!r}")
    if info.compress_size and info.file_size / info.compress_size > 1_000:
        raise AuditError(f"Suspicious compression ratio in ZIP member: {info.filename!r}")


def inspect_archive_bytes(
    archive_bytes: bytes,
    source_id: str,
    *,
    final_url: str | None = None,
    response_headers: dict[str, str] | None = None,
    retrieved_at_utc: str | None = None,
) -> dict[str, Any]:
    if source_id not in SOURCES:
        raise AuditError(f"Unknown source ID: {source_id}")
    if not archive_bytes:
        raise AuditError("The archive response is empty.")
    if len(archive_bytes) > MAX_ARCHIVE_BYTES:
        raise AuditError(f"Archive exceeds the {MAX_ARCHIVE_BYTES}-byte safety limit.")

    source = SOURCES[source_id]
    try:
        zip_file = zipfile.ZipFile(io.BytesIO(archive_bytes))
    except zipfile.BadZipFile as exc:
        raise AuditError("Downloaded file is not a valid ZIP archive.") from exc

    with zip_file:
        infos = zip_file.infolist()
        if len(infos) > MAX_MEMBERS:
            raise AuditError(f"ZIP contains more than {MAX_MEMBERS} members.")

        member_names: set[str] = set()
        total_uncompressed = 0
        for info in infos:
            _validate_member_path(info)
            if info.is_dir():
                continue
            if info.filename in member_names:
                raise AuditError(f"Duplicate ZIP member name: {info.filename!r}")
            member_names.add(info.filename)
            total_uncompressed += info.file_size
            if total_uncompressed > MAX_TOTAL_UNCOMPRESSED_BYTES:
                raise AuditError("ZIP total uncompressed size exceeds the safety limit.")

        bad_member = zip_file.testzip()
        if bad_member:
            raise AuditError(f"ZIP CRC validation failed for member {bad_member!r}")
        member_names.clear()
        total_uncompressed = 0
        inventory: list[dict[str, Any]] = []
        marker_counts: Counter[str] = Counter()
        versions: set[str] = set()
        book_data: dict[str, dict[str, Any]] = {}
        usfm_member_count = 0
        usfm_members_without_id: list[str] = []

        for info in infos:
            _validate_member_path(info)
            if info.is_dir():
                continue
            if info.filename in member_names:
                raise AuditError(f"Duplicate ZIP member name: {info.filename!r}")
            member_names.add(info.filename)
            total_uncompressed += info.file_size
            if total_uncompressed > MAX_TOTAL_UNCOMPRESSED_BYTES:
                raise AuditError("ZIP total uncompressed size exceeds the safety limit.")

            suffix = PurePosixPath(info.filename.lower()).suffix
            member_record: dict[str, Any] = {
                "name": info.filename,
                "compressed_size_bytes": info.compress_size,
                "uncompressed_size_bytes": info.file_size,
                "crc32": f"{info.CRC:08x}",
            }

            if suffix in USFM_FILE_SUFFIXES:
                usfm_member_count += 1
                raw = zip_file.read(info)
                member_record["sha256_uncompressed"] = sha256_hex(raw)
                try:
                    text = raw.decode("utf-8-sig")
                except UnicodeDecodeError as exc:
                    raise AuditError(f"USFM member is not UTF-8: {info.filename!r}") from exc
                parsed = parse_usfm_text(text, info.filename)
                member_record["book_ids"] = parsed["book_ids_in_member"]
                member_record["usfm_versions"] = parsed["usfm_versions"]
                if not parsed["book_ids_in_member"]:
                    usfm_members_without_id.append(info.filename)
                versions.update(parsed["usfm_versions"])
                marker_counts.update(parsed["marker_counts"])

                for book_id, parsed_book in parsed["books"].items():
                    target = book_data.setdefault(book_id, {
                        "chapters": set(),
                        "verse_labels": set(),
                        "verse_address_occurrences": [],
                        "verse_marker_count": 0,
                        "verse_range_marker_count": 0,
                        "members": set(),
                    })
                    target["chapters"].update(parsed_book["chapters"])
                    target["verse_labels"].update(parsed_book["verse_labels"])
                    target["verse_address_occurrences"].extend(parsed_book["verse_address_occurrences"])
                    target["verse_marker_count"] += parsed_book["verse_marker_count"]
                    target["verse_range_marker_count"] += parsed_book["verse_range_marker_count"]
                    target["members"].update(parsed_book["member_names"])

            inventory.append(member_record)

        if usfm_member_count == 0:
            raise AuditError("No .usfm or .sfm files were found in the ZIP archive.")

    book_inventory = []
    for book_id in sorted(book_data):
        item = book_data[book_id]
        book_inventory.append({
            "book_id": book_id,
            "chapter_count": len(item["chapters"]),
            "verse_marker_count": item["verse_marker_count"],
            "distinct_chapter_verse_labels": len(item["verse_labels"]),
            "duplicate_chapter_verse_labels": len(item["verse_address_occurrences"]) - len(item["verse_labels"]),
            "verse_range_marker_count": item["verse_range_marker_count"],
            "members": sorted(item["members"]),
        })

    actual_core = set(book_data) & EXPECTED_CORE_BOOKS
    missing_core = sorted(EXPECTED_CORE_BOOKS - actual_core)
    extra_books = sorted(set(book_data) - EXPECTED_CORE_BOOKS)
    total_chapters = sum(row["chapter_count"] for row in book_inventory)
    total_verse_markers = sum(row["verse_marker_count"] for row in book_inventory)
    total_ranges = sum(row["verse_range_marker_count"] for row in book_inventory)
    verse_address_inventory = [
        {
            "book_id": book_id,
            "chapter_label": chapter_label,
            "verse_label": verse_label,
        }
        for book_id, item in sorted(book_data.items())
        for chapter_label, verse_label in item["verse_address_occurrences"]
    ]

    return {
        "schema_version": 1,
        "status": "review_required" if missing_core else "core_66_present",
        "source_id": source_id,
        "source_name": source["name"],
        "source_url": source["url"],
        "final_url": final_url or source["url"],
        "retrieved_at_utc": retrieved_at_utc or utc_now(),
        "response_headers": response_headers or {},
        "official_directory_baseline_observed_2026_11_18": {
            "listed_size_bytes": source["expected_directory_size_bytes"],
            "listed_last_modified": source["directory_last_modified"],
            "download_size_matches_listed_size": len(archive_bytes) == source["expected_directory_size_bytes"],
            "note": "A mismatch may mean the official source archive changed after the directory snapshot; verify before import.",
        },
        "archive": {
            "filename": f"{source_id}_usfm.zip",
            "size_bytes": len(archive_bytes),
            "sha256": sha256_hex(archive_bytes),
            "zip_crc_test": "passed",
            "member_count": len(inventory),
            "usfm_member_count": usfm_member_count,
            "total_uncompressed_bytes": total_uncompressed,
        },
        "parse_summary": {
            "detected_usfm_versions": sorted(versions),
            "book_id_count": len(book_data),
            "core_66_book_ids_found": len(actual_core),
            "missing_core_book_ids": missing_core,
            "additional_book_ids": extra_books,
            "total_chapter_count": total_chapters,
            "total_verse_marker_count": total_verse_markers,
            "distinct_verse_address_count": sum(len(item["verse_labels"]) for item in book_data.values()),
            "duplicate_verse_address_occurrence_count": sum(
                len(item["verse_address_occurrences"]) - len(item["verse_labels"])
                for item in book_data.values()
            ),
            "total_verse_range_marker_count": total_ranges,
            "usfm_members_without_id": usfm_members_without_id,
            "marker_counts": dict(sorted(marker_counts.items())),
        },
        "member_inventory": inventory,
        "book_inventory": book_inventory,
        "verse_address_inventory": verse_address_inventory,
        "warnings": (
            ["One or more of the 66 Protestant-canon book IDs were not found; do not approve this package for first-release import."]
            if missing_core else []
        ),
    }


def download_archive(source_id: str, cache_dir: Path) -> tuple[bytes, str, dict[str, str]]:
    source = SOURCES[source_id]
    request = urllib.request.Request(
        source["url"],
        headers={
            "User-Agent": "BibleStudyRepo-SourceAudit/1.0",
            "Accept": "application/zip, application/octet-stream;q=0.9, */*;q=0.1",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=90) as response:
            status = getattr(response, "status", 200)
            if status != 200:
                raise AuditError(f"Unexpected HTTP status {status} for {source['url']}")
            final_url = response.geturl()
            if urllib.parse.urlparse(final_url).hostname not in {"ebible.org", "www.ebible.org"}:
                raise AuditError(f"Download redirected to an unexpected host: {final_url}")
            headers = {key.lower(): value for key, value in response.headers.items()}
            content_type = headers.get("content-type", "")
            declared_length = headers.get("content-length")
            if declared_length and int(declared_length) > MAX_ARCHIVE_BYTES:
                raise AuditError("HTTP Content-Length exceeds the archive safety limit.")
            chunks: list[bytes] = []
            total = 0
            while True:
                chunk = response.read(1024 * 1024)
                if not chunk:
                    break
                total += len(chunk)
                if total > MAX_ARCHIVE_BYTES:
                    raise AuditError("Downloaded archive exceeds the archive safety limit.")
                chunks.append(chunk)
            data = b"".join(chunks)
    except urllib.error.HTTPError as exc:
        raise AuditError(f"HTTP error {exc.code} downloading {source['url']}") from exc
    except urllib.error.URLError as exc:
        raise AuditError(f"Network error downloading {source['url']}: {exc.reason}") from exc

    if not data.startswith(b"PK"):
        preview = data[:100].decode("utf-8", errors="replace")
        raise AuditError(f"Response does not look like a ZIP file (content-type={content_type!r}, preview={preview!r}).")

    cache_dir.mkdir(parents=True, exist_ok=True)
    archive_hash = sha256_hex(data)
    archive_path = cache_dir / f"{source_id}-{archive_hash}.zip"
    archive_path.write_bytes(data)
    headers["x-local-cache-file"] = str(archive_path)
    return data, final_url, headers


def inspect_local_archive(path: Path, source_id: str) -> dict[str, Any]:
    data = path.read_bytes()
    return inspect_archive_bytes(data, source_id, final_url=str(path), retrieved_at_utc=utc_now())


def write_outputs(reports: list[dict[str, Any]], output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    report_by_source = {report["source_id"]: report for report in reports}
    comparison: dict[str, Any] | None = None
    webp = report_by_source.get("engwebp")
    kjv = report_by_source.get("eng-kjv")
    if webp and kjv:
        webp_addresses = {
            (row["book_id"], row["chapter_label"], row["verse_label"])
            for row in webp["verse_address_inventory"]
            if row["book_id"] in EXPECTED_CORE_BOOKS
        }
        kjv_addresses = {
            (row["book_id"], row["chapter_label"], row["verse_label"])
            for row in kjv["verse_address_inventory"]
            if row["book_id"] in EXPECTED_CORE_BOOKS
        }
        webp_only = sorted(webp_addresses - kjv_addresses)
        kjv_only = sorted(kjv_addresses - webp_addresses)
        comparison = {
            "scope": "66 Protestant-canon book IDs only; compares primary c/v labels, not verse wording or semantic equivalence",
            "webp_distinct_addresses": len(webp_addresses),
            "kjv_distinct_addresses": len(kjv_addresses),
            "common_addresses": len(webp_addresses & kjv_addresses),
            "webp_only_count": len(webp_only),
            "kjv_only_count": len(kjv_only),
            "webp_only": [
                {"book_id": b, "chapter_label": c, "verse_label": v}
                for b, c, v in webp_only
            ],
            "kjv_only": [
                {"book_id": b, "chapter_label": c, "verse_label": v}
                for b, c, v in kjv_only
            ],
        }

    manifest = {
        "generated_at_utc": utc_now(),
        "description": "Metadata-only audit. No Scripture wording is written to this report.",
        "sources": reports,
        "primary_versification_address_comparison": comparison,
    }
    (output_dir / "audit-manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\\n", encoding="utf-8"
    )

    with (output_dir / "member-inventory.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=[
            "source_id", "name", "compressed_size_bytes", "uncompressed_size_bytes",
            "crc32", "sha256_uncompressed", "book_ids", "usfm_versions",
        ])
        writer.writeheader()
        for report in reports:
            for member in report["member_inventory"]:
                writer.writerow({
                    "source_id": report["source_id"],
                    **member,
                    "book_ids": ";".join(member.get("book_ids", [])),
                    "usfm_versions": ";".join(member.get("usfm_versions", [])),
                })

    with (output_dir / "book-inventory.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=[
            "source_id", "book_id", "chapter_count", "verse_marker_count",
            "distinct_chapter_verse_labels", "duplicate_chapter_verse_labels",
            "verse_range_marker_count", "members",
        ])
        writer.writeheader()
        for report in reports:
            for book in report["book_inventory"]:
                writer.writerow({
                    "source_id": report["source_id"],
                    **book,
                    "members": ";".join(book["members"]),
                })

    with (output_dir / "marker-inventory.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["source_id", "marker", "occurrences"])
        writer.writeheader()
        for report in reports:
            for marker, count in report["parse_summary"]["marker_counts"].items():
                writer.writerow({"source_id": report["source_id"], "marker": marker, "occurrences": count})

    with (output_dir / "verse-addresses.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["source_id", "book_id", "chapter_label", "verse_label"])
        writer.writeheader()
        for report in reports:
            for address in report["verse_address_inventory"]:
                writer.writerow({"source_id": report["source_id"], **address})

    if comparison is not None:
        with (output_dir / "verse-address-differences.csv").open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=[
                "book_id", "chapter_label", "verse_label", "present_in_webp", "present_in_kjv",
            ])
            writer.writeheader()
            for key in comparison["webp_only"]:
                writer.writerow({**key, "present_in_webp": True, "present_in_kjv": False})
            for key in comparison["kjv_only"]:
                writer.writerow({**key, "present_in_webp": False, "present_in_kjv": True})


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--download", action="store_true", help="Download the official archives from eBible.org.")
    parser.add_argument("--source-dir", type=Path, default=Path("source-archives"), help="Directory containing local ZIPs when not downloading.")
    parser.add_argument("--cache-dir", type=Path, default=Path(".source-audit-cache"), help="Local directory for downloaded source ZIPs.")
    parser.add_argument("--output-dir", type=Path, default=Path("source-audit-output"), help="Directory for JSON and CSV audit reports.")
    args = parser.parse_args()

    reports: list[dict[str, Any]] = []
    failures: list[str] = []
    for source_id in SOURCES:
        try:
            if args.download:
                data, final_url, headers = download_archive(source_id, args.cache_dir)
                report = inspect_archive_bytes(
                    data,
                    source_id,
                    final_url=final_url,
                    response_headers=headers,
                    retrieved_at_utc=utc_now(),
                )
            else:
                archive_path = args.source_dir / f"{source_id}_usfm.zip"
                if not archive_path.is_file():
                    raise AuditError(f"Local archive not found: {archive_path}")
                report = inspect_local_archive(archive_path, source_id)
            reports.append(report)
            print(json.dumps({
                "source_id": report["source_id"],
                "status": report["status"],
                "archive_sha256": report["archive"]["sha256"],
                "archive_size_bytes": report["archive"]["size_bytes"],
                "usfm_member_count": report["archive"]["usfm_member_count"],
                "book_id_count": report["parse_summary"]["book_id_count"],
                "core_66_found": report["parse_summary"]["core_66_book_ids_found"],
                "missing_core": report["parse_summary"]["missing_core_book_ids"],
                "usfm_versions": report["parse_summary"]["detected_usfm_versions"],
                "chapters": report["parse_summary"]["total_chapter_count"],
                "verse_markers": report["parse_summary"]["total_verse_marker_count"],
            }, ensure_ascii=False))
        except (AuditError, OSError, zipfile.BadZipFile) as exc:
            failures.append(f"{source_id}: {exc}")
            print(f"ERROR: {source_id}: {exc}", file=sys.stderr)

    if reports:
        write_outputs(reports, args.output_dir)
        print(f"Audit reports written to {args.output_dir.resolve()}")

    if failures:
        print("\n".join(failures), file=sys.stderr)
        return 1
    if any(report["status"] != "core_66_present" for report in reports):
        return 2
    if len(reports) != len(SOURCES):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
