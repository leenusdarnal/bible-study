#!/usr/bin/env python3
"""Metadata-only USFMTC semantic parse and USFM round-trip audit.

The tool tests the source files against candidate USFM 2.5 and 3.1 parser
profiles because the official source members do not declare a \\usfm version.
It writes hashes and structural counts only; Scripture wording stays in memory.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path
from typing import Any

import usfmtc

PARSER_VERSION = getattr(usfmtc, "version", "unknown")
CANDIDATE_PROFILES = ("2.5", "3.1")
USFM_SUFFIXES = {".usfm", ".sfm"}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def xml_shape(element: ET.Element) -> tuple[Any, ...]:
    """Fingerprint full canonical XML, including text, without exposing it."""
    return (
        element.tag,
        tuple(sorted(element.attrib.items())),
        element.text or "",
        element.tail or "",
        tuple(xml_shape(child) for child in list(element)),
    )


def summarise(doc: Any) -> dict[str, Any]:
    root = doc.getroot()
    counts: Counter[str] = Counter()
    style_counts: Counter[str] = Counter()
    book_codes: list[str] = []
    for element in root.iter():
        counts[element.tag] += 1
        style = element.attrib.get("style")
        if style:
            style_counts[style] += 1
        if element.tag == "book":
            code = element.attrib.get("code")
            if code:
                book_codes.append(code)
    return {
        "book_codes": book_codes,
        "element_counts": dict(sorted(counts.items())),
        "style_counts": dict(sorted(style_counts.items())),
        "chapter_nodes": counts.get("chapter", 0),
        "verse_nodes": counts.get("verse", 0),
    }


def audit_profile(path: Path, version: str) -> dict[str, Any]:
    try:
        doc = usfmtc.readFile(str(path), informat="usfm", version=version, strict=True)
        if doc is None or doc.getroot() is None:
            return {"profile": version, "status": "review_required", "parse_error_count": 1}
        parse_errors = len(doc.errors or [])
        if parse_errors:
            return {
                "profile": version,
                "status": "review_required",
                "parse_error_count": parse_errors,
            }

        doc.canonicalise()
        original = summarise(doc)
        original_fingerprint = sha256(
            json.dumps(xml_shape(doc.getroot()), ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        )
        regenerated = doc.outUsfm(version=version)
        if not isinstance(regenerated, str) or not regenerated:
            return {
                "profile": version,
                "status": "review_required",
                "parse_error_count": 0,
                "serialization_succeeded": False,
                "original_structure": original,
            }

        reparsed = usfmtc.USX.fromUsfm(regenerated, version=version, strict=True)
        if reparsed is None or reparsed.getroot() is None:
            return {
                "profile": version,
                "status": "review_required",
                "parse_error_count": 0,
                "serialization_succeeded": True,
                "roundtrip_parse_error_count": 1,
                "original_structure": original,
            }
        roundtrip_errors = len(reparsed.errors or [])
        if roundtrip_errors:
            return {
                "profile": version,
                "status": "review_required",
                "parse_error_count": 0,
                "serialization_succeeded": True,
                "roundtrip_parse_error_count": roundtrip_errors,
                "original_structure": original,
            }

        reparsed.canonicalise()
        roundtrip = summarise(reparsed)
        roundtrip_fingerprint = sha256(
            json.dumps(xml_shape(reparsed.getroot()), ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        )
        matches = original_fingerprint == roundtrip_fingerprint
        return {
            "profile": version,
            "status": "passed" if matches else "review_required",
            "parse_error_count": 0,
            "roundtrip_parse_error_count": 0,
            "serialization_succeeded": True,
            "roundtrip_matches": matches,
            "original_structure": original,
            "roundtrip_structure": roundtrip,
        }
    except Exception as exc:
        # Parser exception messages may contain source wording; never write them to reports.
        return {
            "profile": version,
            "status": "review_required",
            "exception_type": type(exc).__name__,
        }


def audit_directory(source_dir: Path) -> dict[str, Any]:
    files: list[dict[str, Any]] = []
    summary_by_source: dict[str, Any] = {}
    for source_id in ("engwebp", "eng-kjv"):
        root = source_dir / source_id
        source_files = sorted(
            p for p in root.rglob("*")
            if p.is_file() and p.suffix.lower() in USFM_SUFFIXES
        ) if root.exists() else []
        source_results = []
        for path in source_files:
            raw = path.read_bytes()
            profiles = []
            for version in CANDIDATE_PROFILES:
                profile_result = audit_profile(path, version)
                profiles.append(profile_result)
                if profile_result["status"] == "passed":
                    break
            passed = [x for x in profiles if x["status"] == "passed"]
            result = {
                "source_id": source_id,
                "member_name": path.relative_to(root).as_posix(),
                "source_byte_size": len(raw),
                "source_sha256": sha256(raw),
                "status": "passed" if passed else "review_required",
                "passing_profiles": [x["profile"] for x in passed],
                "attempted_profiles": [x["profile"] for x in profiles],
                "profile_results": profiles,
            }
            source_results.append(result)
            files.append(result)

        aggregate_elements: Counter[str] = Counter()
        aggregate_styles: Counter[str] = Counter()
        for file_result in source_results:
            passing_profile = next(
                (profile for profile in file_result["profile_results"] if profile["status"] == "passed"),
                None,
            )
            if passing_profile:
                structure = passing_profile.get("original_structure", {})
                aggregate_elements.update(structure.get("element_counts", {}))
                aggregate_styles.update(structure.get("style_counts", {}))

        summary_by_source[source_id] = {
            "source_id": source_id,
            "member_count": len(source_results),
            "passed_count": sum(x["status"] == "passed" for x in source_results),
            "review_required_count": sum(x["status"] != "passed" for x in source_results),
            "fallback_profile_count": sum("3.1" in [p["profile"] for p in x["profile_results"]] for x in source_results),
            "aggregate_element_counts": dict(sorted(aggregate_elements.items())),
            "aggregate_style_counts": dict(sorted(aggregate_styles.items())),
        }

    failures = sum(x["status"] != "passed" for x in files)
    return {
        "schema_version": 2,
        "parser": {
            "package": "usfmtc",
            "version": PARSER_VERSION,
            "publisher": "USFM Technical Committee",
            "candidate_profiles_in_order": list(CANDIDATE_PROFILES),
            "profile_strategy": "Try 2.5 first; try 3.1 only when 2.5 does not pass.",
        },
        "description": "Metadata-only semantic parse and full canonical XML round-trip fingerprints. No Scripture wording is included.",
        "summary_by_source": summary_by_source,
        "total_files": len(files),
        "passed_files": len(files) - failures,
        "review_required_files": failures,
        "files": files,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = audit_directory(args.source_dir)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    for source_id, summary in report["summary_by_source"].items():
        print(json.dumps(summary))
    print(json.dumps({
        "parser": report["parser"],
        "total_files": report["total_files"],
        "passed_files": report["passed_files"],
        "review_required_files": report["review_required_files"],
        "report_file": str(args.output),
    }))
    if report["total_files"] == 0 or report["review_required_files"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
