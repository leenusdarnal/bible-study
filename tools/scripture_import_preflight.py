#!/usr/bin/env python3
"""Fail-closed preflight validation for a Scripture import run.

The tool reads private converter JSON artefacts but writes a metadata-only report.
Never upload converter outputs or Bible wording to public CI artifacts.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path, PurePosixPath
from typing import Any

SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
CORE_66 = set("""
GEN EXO LEV NUM DEU JOS JDG RUT 1SA 2SA 1KI 2KI 1CH 2CH EZR NEH EST JOB
PSA PRO ECC SNG ISA JER LAM EZK DAN HOS JOL AMO OBA JON MIC NAM HAB ZEP
HAG ZEC MAL MAT MRK LUK JHN ACT ROM 1CO 2CO GAL EPH PHP COL 1TH 2TH 1TI
2TI TIT PHM HEB JAS 1PE 2PE 1JN 2JN 3JN JUD REV
""".split())
EXPECTED_PARSER = {"package": "usfmtc", "version": "0.4.10"}
EXPECTED_CONVERTER = {
    "name": "bible-study-usfm-structured-converter",
    "version": "0.1.0",
}
EXPECTED_SOURCE_IDS = {"WEBP": "engwebp", "KJV": "eng-kjv"}
EXPECTED_ARCHIVE_URLS = {
    "engwebp": "https://ebible.org/Scriptures/engwebp_usfm.zip",
    "eng-kjv": "https://ebible.org/Scriptures/eng-kjv_usfm.zip",
}


class PreflightInputError(ValueError):
    """Raised when a preflight input document cannot be interpreted."""


def load_json(path: Path, label: str) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise PreflightInputError(f"Could not read {label}: {type(exc).__name__}") from exc


def safe_relative_path(value: Any) -> bool:
    if not isinstance(value, str) or not value.strip():
        return False
    path = PurePosixPath(value.replace("\\", "/"))
    return not path.is_absolute() and all(part not in {"", ".", ".."} for part in path.parts)


def sha_is_valid(value: Any) -> bool:
    return isinstance(value, str) and bool(SHA256_RE.fullmatch(value))


def _rights_record(register: Any, edition_id: str) -> dict[str, Any] | None:
    if not isinstance(register, dict) or register.get("schema_version") != 1:
        return None
    editions = register.get("editions")
    if not isinstance(editions, list):
        return None
    matches = [
        item for item in editions
        if isinstance(item, dict) and item.get("edition_id") == edition_id
    ]
    return matches[0] if len(matches) == 1 else None


def _source_archive_evidence_matches(record: dict[str, Any], archive_sha: str) -> bool:
    evidence = record.get("evidence")
    if not isinstance(evidence, list):
        return False
    return any(
        isinstance(item, dict)
        and item.get("kind") == "source_archive"
        and item.get("sha256") == archive_sha
        for item in evidence
    )


def _marker_index(registry: Any) -> dict[str, dict[str, Any]]:
    if not isinstance(registry, dict):
        return {}
    markers = registry.get("markers")
    if not isinstance(markers, list):
        return {}
    result: dict[str, dict[str, Any]] = {}
    for item in markers:
        if isinstance(item, dict) and isinstance(item.get("marker"), str):
            result[item["marker"]] = item
    return result


def _read_proposals(proposals_dir: Path | None, findings: list[dict[str, str]]) -> list[dict[str, Any]]:
    if proposals_dir is None:
        return []
    if not proposals_dir.exists():
        return []
    proposals: list[dict[str, Any]] = []
    for path in sorted(proposals_dir.rglob("*.json")):
        try:
            data = load_json(path, "versification proposal")
        except PreflightInputError as exc:
            findings.append({
                "code": "VERSIFICATION_PROPOSAL_UNREADABLE",
                "severity": "blocking",
                "message": str(exc),
            })
            continue
        if isinstance(data, dict):
            data["_preflight_path"] = path.as_posix()
            proposals.append(data)
        else:
            findings.append({
                "code": "VERSIFICATION_PROPOSAL_INVALID",
                "severity": "blocking",
                "message": "A versification proposal is not a JSON object.",
            })
    return proposals


def _matching_proposals(
    proposals: list[dict[str, Any]], source_id: str, archive_sha: str
) -> list[dict[str, Any]]:
    matches = []
    for proposal in proposals:
        for side in ("from_edition", "to_edition"):
            edition = proposal.get(side)
            if (
                isinstance(edition, dict)
                and edition.get("source_id") == source_id
                and edition.get("archive_sha256") == archive_sha
            ):
                matches.append(proposal)
                break
    return matches


def _validate_projection_rows(
    converted: dict[str, Any],
    expected_book_ids: set[str],
    member_name: str,
    findings: list[dict[str, str]],
) -> int:
    projections = converted.get("verse_projections")
    if not isinstance(projections, list):
        findings.append({
            "code": "VERSE_PROJECTIONS_MISSING",
            "severity": "blocking",
            "message": f"{member_name}: converted output has no verse projection list.",
        })
        return 0

    seen: set[tuple[str, str, str]] = set()
    for index, row in enumerate(projections):
        prefix = f"{member_name}: verse projection {index + 1}"
        if not isinstance(row, dict):
            findings.append({
                "code": "VERSE_PROJECTION_INVALID",
                "severity": "blocking",
                "message": f"{prefix} is not an object.",
            })
            continue

        book = row.get("source_book_id")
        chapter = row.get("chapter_label")
        verse = row.get("verse_label")
        if not isinstance(book, str) or book not in expected_book_ids:
            findings.append({
                "code": "VERSE_BOOK_MISMATCH",
                "severity": "blocking",
                "message": f"{prefix} has a book ID inconsistent with its source member.",
            })
            continue
        if not isinstance(chapter, str) or not chapter.strip() or not isinstance(verse, str) or not verse.strip():
            findings.append({
                "code": "VERSE_REFERENCE_MALFORMED",
                "severity": "blocking",
                "message": f"{prefix} is missing a source-native chapter or verse label.",
            })
            continue

        address = (book, chapter, verse)
        if address in seen:
            findings.append({
                "code": "DUPLICATE_SOURCE_REFERENCE",
                "severity": "blocking",
                "message": f"{member_name}: duplicate source reference {book}.{chapter}.{verse}.",
            })
        seen.add(address)

        text_value = row.get("text")
        content_state = row.get("content_state")
        annotations = row.get("annotation_count")
        if not isinstance(text_value, str) or not isinstance(annotations, int) or annotations < 0:
            findings.append({
                "code": "CONTENT_STATE_INVALID",
                "severity": "blocking",
                "message": f"{prefix} has invalid text or annotation metadata.",
            })
            continue
        if content_state == "text" and not text_value.strip():
            findings.append({
                "code": "CONTENT_STATE_INVALID",
                "severity": "blocking",
                "message": f"{prefix} is labelled text but has no text content.",
            })
        elif content_state == "annotation_only" and (text_value.strip() or annotations < 1):
            findings.append({
                "code": "CONTENT_STATE_INVALID",
                "severity": "blocking",
                "message": f"{prefix} has an inconsistent annotation-only state.",
            })
        elif content_state == "empty_marker" and (text_value.strip() or annotations != 0):
            findings.append({
                "code": "CONTENT_STATE_INVALID",
                "severity": "blocking",
                "message": f"{prefix} has an inconsistent empty-marker state.",
            })
        elif content_state not in {"text", "annotation_only", "empty_marker"}:
            findings.append({
                "code": "CONTENT_STATE_INVALID",
                "severity": "blocking",
                "message": f"{prefix} uses an unsupported content state.",
            })
        if row.get("review_required") is True:
            findings.append({
                "code": "VERSE_REVIEW_REQUIRED",
                "severity": "blocking",
                "message": f"{prefix} is flagged for editorial review.",
            })
    return len(projections)


def _validate_nodes(
    converted: dict[str, Any],
    member_name: str,
    findings: list[dict[str, str]],
) -> None:
    blocks = converted.get("content_blocks")
    if not isinstance(blocks, list) or not blocks:
        findings.append({
            "code": "CONTENT_BLOCKS_MISSING",
            "severity": "blocking",
            "message": f"{member_name}: converted output has no content blocks.",
        })
        return

    block_ids: set[str] = set()
    for block_index, block in enumerate(blocks):
        prefix = f"{member_name}: block {block_index + 1}"
        if not isinstance(block, dict) or block.get("block_type") not in {
            "book_intro", "chapter_heading", "section_heading", "paragraph",
            "poetry_line_group", "list", "colophon", "peripheral", "other",
        }:
            findings.append({
                "code": "CONTENT_BLOCK_INVALID",
                "severity": "blocking",
                "message": f"{prefix} has an invalid block structure or type.",
            })
            continue
        block_id = block.get("id")
        if not isinstance(block_id, str) or not block_id or block_id in block_ids:
            findings.append({
                "code": "CONTENT_BLOCK_ID_INVALID",
                "severity": "blocking",
                "message": f"{prefix} has a missing or duplicate block identifier.",
            })
        block_ids.add(block_id if isinstance(block_id, str) else "")
        nodes = block.get("nodes")
        if not isinstance(nodes, list):
            findings.append({
                "code": "CONTENT_NODES_MISSING",
                "severity": "blocking",
                "message": f"{prefix} has no node row list.",
            })
            continue
        node_ids: set[str] = set()
        previous_order = 0
        paths: set[str] = set()
        for node_index, node in enumerate(nodes):
            node_prefix = f"{prefix}, node {node_index + 1}"
            if not isinstance(node, dict) or node.get("node_type") not in {
                "text", "span", "footnote", "cross_reference", "milestone",
                "unknown_marker", "attribute", "break",
            }:
                findings.append({
                    "code": "CONTENT_NODE_INVALID",
                    "severity": "blocking",
                    "message": f"{node_prefix} has an invalid node structure or type.",
                })
                continue
            node_id = node.get("id")
            parent_id = node.get("parent_node_id")
            order = node.get("source_order")
            order_path = node.get("node_order_path")
            if not isinstance(node_id, str) or not node_id or node_id in node_ids:
                findings.append({
                    "code": "CONTENT_NODE_ID_INVALID",
                    "severity": "blocking",
                    "message": f"{node_prefix} has a missing or duplicate node identifier.",
                })
            if parent_id is not None and (
                not isinstance(parent_id, str) or parent_id not in node_ids
            ):
                findings.append({
                    "code": "CONTENT_NODE_PARENT_INVALID",
                    "severity": "blocking",
                    "message": f"{node_prefix} refers to a parent that does not precede it.",
                })
            if not isinstance(order, int) or order <= previous_order:
                findings.append({
                    "code": "CONTENT_NODE_ORDER_INVALID",
                    "severity": "blocking",
                    "message": f"{node_prefix} does not have strictly increasing source order.",
                })
            else:
                previous_order = order
            if not isinstance(order_path, str) or not order_path or order_path in paths:
                findings.append({
                    "code": "CONTENT_NODE_PATH_INVALID",
                    "severity": "blocking",
                    "message": f"{node_prefix} has a missing or duplicate order path.",
                })
            node_ids.add(node_id if isinstance(node_id, str) else "")
            paths.add(order_path if isinstance(order_path, str) else "")


def run_preflight(
    manifest: Any,
    rights_register: Any,
    marker_registry: Any,
    *,
    base_dir: Path,
    proposals_dir: Path | None = None,
) -> dict[str, Any]:
    findings: list[dict[str, str]] = []

    def add(code: str, severity: str, message: str) -> None:
        findings.append({"code": code, "severity": severity, "message": message})

    if not isinstance(manifest, dict) or manifest.get("schema_version") != 1:
        return {
            "schema_version": 1,
            "status": "blocked",
            "ready_for_import": False,
            "findings": [{
                "code": "MANIFEST_INVALID",
                "severity": "blocking",
                "message": "Preflight manifest must be a JSON object with schema_version 1.",
            }],
            "summary": {},
        }

    edition_id = manifest.get("edition_id")
    source_id = manifest.get("source_id")
    territory = manifest.get("territory")
    archive = manifest.get("source_archive")
    parser = manifest.get("parser")
    converter_meta = manifest.get("converter")
    expected = manifest.get("expected")
    versification = manifest.get("versification")
    storage = manifest.get("storage")

    expected_source_id = EXPECTED_SOURCE_IDS.get(edition_id) if isinstance(edition_id, str) else None
    if expected_source_id is None or source_id != expected_source_id:
        add("EDITION_SOURCE_MISMATCH", "blocking", "Edition ID and source package ID are not a supported matching pair.")
    if not isinstance(territory, str) or not re.fullmatch(r"[A-Z]{2}", territory):
        add("TERRITORY_INVALID", "blocking", "A two-letter uppercase publication territory is required.")

    if not isinstance(archive, dict):
        archive = {}
        add("SOURCE_ARCHIVE_MISSING", "blocking", "Source archive metadata is missing.")
    archive_sha = archive.get("sha256")
    if not sha_is_valid(archive_sha):
        add("ARCHIVE_HASH_INVALID", "blocking", "Source archive SHA-256 is missing or malformed.")
    if (
        not isinstance(archive.get("url"), str)
        or not isinstance(source_id, str)
        or archive.get("url") != EXPECTED_ARCHIVE_URLS.get(source_id)
    ):
        add("ARCHIVE_URL_INVALID", "blocking", "Source archive URL does not match the pinned official source URL.")
    if not isinstance(archive.get("size_bytes"), int) or archive["size_bytes"] <= 0:
        add("ARCHIVE_SIZE_INVALID", "blocking", "Source archive size must be a positive integer.")
    if archive.get("zip_integrity_status") != "passed":
        add("ARCHIVE_INTEGRITY_UNVERIFIED", "blocking", "ZIP integrity audit has not passed.")

    signature = archive.get("signature_verification")
    if not isinstance(signature, dict):
        signature = {}
    signature_status = signature.get("status")
    if signature_status == "verified":
        pass
    elif (
        signature_status == "waived"
        and isinstance(signature.get("reviewer"), str) and signature["reviewer"].strip()
        and isinstance(signature.get("decision_reference"), str) and signature["decision_reference"].strip()
    ):
        add("ARCHIVE_SIGNATURE_WAIVED", "warning", "Detached archive signature verification has an explicit documented waiver.")
    else:
        add("ARCHIVE_SIGNATURE_UNVERIFIED", "blocking", "Detached archive signature is neither verified nor covered by an approved waiver.")

    if not isinstance(parser, dict) or any(parser.get(k) != v for k, v in EXPECTED_PARSER.items()):
        add("PARSER_IDENTITY_INVALID", "blocking", "Parser must match the pinned USFMTC package and version.")
    if not isinstance(parser, dict) or parser.get("compatibility_profile") not in {"2.5", "3.1"}:
        add("PARSER_PROFILE_INVALID", "blocking", "Parser compatibility profile must be recorded as 2.5 or 3.1.")
    if isinstance(parser, dict) and parser.get("publisher_declared_version") not in (None, ""):
        add("PUBLISHER_VERSION_INFERRED", "blocking", "Do not treat a parser compatibility profile as a publisher-declared USFM version.")

    if not isinstance(converter_meta, dict) or any(converter_meta.get(k) != v for k, v in EXPECTED_CONVERTER.items()):
        add("CONVERTER_IDENTITY_INVALID", "blocking", "Converter identity or version does not match the pinned project implementation.")

    if not isinstance(expected, dict):
        expected = {}
    member_count = expected.get("member_count")
    if not isinstance(member_count, int) or member_count < 1:
        add("EXPECTED_MEMBER_COUNT_INVALID", "blocking", "Expected USFM member count must be a positive integer.")

    members = manifest.get("archive_members")
    if not isinstance(members, list) or not members:
        members = []
        add("ARCHIVE_INVENTORY_MISSING", "blocking", "Complete archive USFM member inventory is required.")
    if isinstance(member_count, int) and member_count != len(members):
        add("ARCHIVE_MEMBER_COUNT_MISMATCH", "blocking", "Archive USFM member count does not match the declared expected count.")

    registry_index = _marker_index(marker_registry)
    registry_coverage = marker_registry.get("coverage", {}) if isinstance(marker_registry, dict) else {}
    if not isinstance(registry_coverage, dict):
        registry_coverage = {}
    registry_version = marker_registry.get("registry_version") if isinstance(marker_registry, dict) else None
    if not isinstance(marker_registry, dict) or marker_registry.get("schema_version") != 1 or not registry_index:
        add("MARKER_REGISTRY_INVALID", "blocking", "A valid marker registry is required.")
    else:
        if registry_coverage.get("status") != "complete" or registry_coverage.get("review_status") != "reviewed":
            add("MARKER_REGISTRY_NOT_APPROVED", "blocking", "Marker registry coverage is incomplete or awaiting editorial approval.")
        if any(item.get("review_status") != "reviewed" for item in registry_index.values()):
            add("MARKER_MAPPINGS_PENDING", "blocking", "One or more marker mappings remain unreviewed.")

    rights = _rights_record(rights_register, edition_id if isinstance(edition_id, str) else "")
    if rights is None:
        add("RIGHTS_RECORD_MISSING", "blocking", "A unique rights record for the selected edition is required.")
    else:
        if rights.get("rights_status") != "approved":
            add("RIGHTS_NOT_APPROVED", "blocking", "Translation rights are not approved for publication.")
        territories = rights.get("territories")
        if not isinstance(territories, list) or territory not in territories:
            add("RIGHTS_TERRITORY_NOT_APPROVED", "blocking", "The selected publication territory is not explicitly approved.")
        permissions = rights.get("permissions")
        if not isinstance(permissions, dict) or permissions.get("display") is not True or permissions.get("cache") is not True:
            add("RIGHTS_DISPLAY_CACHE_NOT_APPROVED", "blocking", "Display and cache permissions must both be explicitly approved.")
        review = rights.get("review")
        if not isinstance(rights.get("evidence"), list) or not rights["evidence"]:
            add("RIGHTS_EVIDENCE_MISSING", "blocking", "Translation rights approval must include supporting evidence.")
        if not isinstance(review, dict) or not all(
            isinstance(review.get(key), str) and review[key].strip()
            for key in ("reviewer", "reviewed_at", "decision_reference")
        ):
            add("RIGHTS_REVIEW_MISSING", "blocking", "Rights approval requires a named reviewer, date and decision reference.")
        if not _source_archive_evidence_matches(rights, archive_sha if isinstance(archive_sha, str) else ""):
            add("RIGHTS_ARCHIVE_EVIDENCE_MISMATCH", "blocking", "Rights evidence does not identify the exact source archive checksum.")

    if not isinstance(versification, dict):
        versification = {}
        add("VERSIFICATION_METADATA_MISSING", "blocking", "Source-specific versification decision metadata is required.")
    if not isinstance(versification.get("scheme_code"), str) or not versification["scheme_code"].strip():
        add("VERSIFICATION_SCHEME_MISSING", "blocking", "A source-specific versification scheme code is required.")
    if versification.get("status") != "approved":
        add("VERSIFICATION_NOT_APPROVED", "blocking", "The source-specific versification profile is not approved.")
    approval = versification.get("approval")
    if not isinstance(approval, dict) or not all(
        isinstance(approval.get(key), str) and approval[key].strip()
        for key in ("reviewer", "reviewed_at", "decision_reference")
    ):
        add("VERSIFICATION_REVIEW_MISSING", "blocking", "Versification approval requires a named reviewer, date and decision reference.")
    mode = versification.get("mode")
    if not isinstance(mode, str) or mode not in {"native_source_only", "cross_edition"}:
        add("VERSIFICATION_MODE_INVALID", "blocking", "Versification mode must be native_source_only or cross_edition.")

    if not isinstance(storage, dict):
        storage = {}
    if storage.get("private_bucket") is not True:
        add("STORAGE_NOT_PRIVATE", "blocking", "Source archive and canonical USX storage must use private object storage.")
    if storage.get("archive_object_status") != "verified":
        add("ARCHIVE_OBJECT_NOT_VERIFIED", "blocking", "The immutable source archive object has not been verified in restricted storage.")
    if storage.get("canonical_usx_objects_status") != "verified":
        add("CANONICAL_USX_OBJECTS_NOT_VERIFIED", "blocking", "Canonical USX objects have not all been checksum-verified in restricted storage.")

    proposals = _read_proposals(proposals_dir, findings)
    matching = _matching_proposals(
        proposals,
        source_id if isinstance(source_id, str) else "",
        archive_sha if isinstance(archive_sha, str) else "",
    )
    excluded_ids = versification.get("excluded_pending_proposal_ids", [])
    if not isinstance(excluded_ids, list):
        excluded_ids = []
        add("VERSIFICATION_EXCLUSIONS_INVALID", "blocking", "Excluded pending proposal IDs must be an array.")
    for proposal in matching:
        proposal_id = proposal.get("proposal_id")
        approved = proposal.get("status") == "approved" and (
            isinstance(proposal.get("review"), dict)
            and proposal["review"].get("review_status") == "approved"
        )
        if approved:
            continue
        if mode == "cross_edition":
            add("PENDING_MAPPING_APPLICABLE", "blocking", f"Cross-edition import is blocked by unapproved mapping proposal {proposal_id}.")
        elif mode == "native_source_only" and proposal_id not in excluded_ids:
            add("PENDING_MAPPING_NOT_EXPLICITLY_EXCLUDED", "blocking", f"Pending mapping proposal {proposal_id} must be explicitly excluded from a native-source-only import.")

    seen_members: set[str] = set()
    seen_books: set[str] = set()
    file_count = 0
    unit_count = 0
    distinct_markers: set[str] = set()
    all_addresses: set[tuple[str, str, str]] = set()

    for index, member in enumerate(members):
        prefix = f"archive member {index + 1}"
        if not isinstance(member, dict):
            add("ARCHIVE_MEMBER_INVALID", "blocking", f"{prefix} is not an object.")
            continue
        name = member.get("member_name")
        if not safe_relative_path(name) or not str(name).lower().endswith((".usfm", ".sfm")):
            add("ARCHIVE_MEMBER_PATH_INVALID", "blocking", f"{prefix} has an unsafe or non-USFM member path.")
            continue
        if name in seen_members:
            add("ARCHIVE_MEMBER_DUPLICATE", "blocking", f"Archive inventory contains duplicate member {name}.")
            continue
        seen_members.add(name)
        digest = member.get("sha256")
        if not sha_is_valid(digest):
            add("MEMBER_HASH_INVALID", "blocking", f"{name}: source member SHA-256 is missing or malformed.")
        canonical_key = member.get("canonical_usx_object_key")
        if not safe_relative_path(canonical_key):
            add("CANONICAL_USX_KEY_INVALID", "blocking", f"{name}: canonical USX object key is missing or unsafe.")
        if not sha_is_valid(member.get("canonical_usx_sha256")):
            add("CANONICAL_USX_HASH_INVALID", "blocking", f"{name}: canonical USX SHA-256 is missing or malformed.")
        if member.get("canonical_usx_object_status") != "verified":
            add("CANONICAL_USX_MEMBER_UNVERIFIED", "blocking", f"{name}: canonical USX object is not checksum-verified.")
        book_ids = member.get("book_ids")
        if not isinstance(book_ids, list) or not book_ids or any(
            not isinstance(code, str) or len(code) != 3 or not code.isalnum()
            for code in book_ids
        ):
            add("MEMBER_BOOK_ID_INVALID", "blocking", f"{name}: source member has no valid book ID inventory.")
            book_ids = []
        seen_books.update(book_ids)
        if member.get("parse_status") != "passed":
            add("SOURCE_PARSE_FAILED", "blocking", f"{name}: semantic USFM parsing did not pass.")
        if member.get("roundtrip_matches") is not True:
            add("SOURCE_ROUNDTRIP_FAILED", "blocking", f"{name}: canonical USX round-trip did not match.")
        if member.get("compatibility_profile") != (parser.get("compatibility_profile") if isinstance(parser, dict) else None):
            add("MEMBER_PROFILE_MISMATCH", "blocking", f"{name}: parser compatibility profile is inconsistent.")
        conversion_path = member.get("conversion_output")
        if not safe_relative_path(conversion_path):
            add("CONVERSION_OUTPUT_PATH_INVALID", "blocking", f"{name}: conversion output path must be a safe relative path.")
            continue
        output_file = (base_dir / Path(*PurePosixPath(conversion_path).parts)).resolve()
        if not output_file.is_relative_to(base_dir.resolve()) or not output_file.is_file():
            add("CONVERSION_OUTPUT_MISSING", "blocking", f"{name}: converted structured output is not available.")
            continue
        try:
            converted = load_json(output_file, "structured conversion output")
        except PreflightInputError as exc:
            add("CONVERSION_OUTPUT_INVALID", "blocking", f"{name}: {exc}")
            continue
        file_count += 1
        source = converted.get("source") if isinstance(converted, dict) else None
        book = converted.get("book") if isinstance(converted, dict) else None
        if not isinstance(source, dict) or source.get("edition_id") != edition_id or source.get("source_id") != source_id:
            add("CONVERSION_PROVENANCE_MISMATCH", "blocking", f"{name}: converted edition/source provenance does not match the preflight manifest.")
            continue
        if source.get("source_member") != name or source.get("source_sha256") != digest:
            add("CONVERSION_SOURCE_MISMATCH", "blocking", f"{name}: converted member path or source checksum does not match the archive inventory.")
        output_parser = source.get("parser")
        if not isinstance(output_parser, dict):
            output_parser = {}
            add("CONVERSION_PARSER_MISMATCH", "blocking", f"{name}: converter output parser metadata is missing.")
        if output_parser.get("package") != (parser.get("package") if isinstance(parser, dict) else None):
            add("CONVERSION_PARSER_MISMATCH", "blocking", f"{name}: converter output parser package does not match the manifest.")
        if output_parser.get("version") != (parser.get("version") if isinstance(parser, dict) else None):
            add("CONVERSION_PARSER_MISMATCH", "blocking", f"{name}: converter output parser version does not match the manifest.")
        if output_parser.get("compatibility_profile") != (parser.get("compatibility_profile") if isinstance(parser, dict) else None):
            add("CONVERSION_PARSER_MISMATCH", "blocking", f"{name}: converter output parser profile does not match the manifest.")
        if not isinstance(book, dict) or book.get("code") not in book_ids:
            add("CONVERSION_BOOK_MISMATCH", "blocking", f"{name}: converted book identity does not match the source archive inventory.")
            converted_book_ids: set[str] = set()
        else:
            converted_book_ids = {book["code"]}
        if converted.get("converter") != EXPECTED_CONVERTER:
            add("CONVERSION_TOOL_MISMATCH", "blocking", f"{name}: converted output was produced by an unexpected converter version.")
        marker_meta = converted.get("marker_registry")
        if not isinstance(marker_meta, dict) or marker_meta.get("registry_version") != registry_version:
            add("CONVERSION_REGISTRY_MISMATCH", "blocking", f"{name}: converter output used a different marker registry version.")
        if converted.get("readiness") != "ready_for_editorial_validation":
            add("CONVERSION_NOT_REVIEWED", "blocking", f"{name}: converter output is flagged for marker/editorial review.")
        unresolved = converted.get("unresolved_markers")
        pending = converted.get("pending_marker_reviews")
        if not isinstance(unresolved, list) or unresolved:
            add("CONVERTER_UNRESOLVED_MARKERS", "blocking", f"{name}: unknown or unresolved markers remain.")
        if not isinstance(pending, list) or pending:
            add("CONVERTER_MARKER_REVIEW_PENDING", "blocking", f"{name}: marker mapping reviews remain pending.")

        marker_counts = converted.get("marker_counts")
        if not isinstance(marker_counts, dict):
            add("CONVERTER_MARKER_COUNTS_MISSING", "blocking", f"{name}: marker counts are missing.")
        else:
            for marker_name, count in marker_counts.items():
                distinct_markers.add(marker_name)
                entry = registry_index.get(marker_name)
                if entry is None:
                    add("MARKER_NOT_REGISTERED", "blocking", f"{name}: encountered marker {marker_name} is not registered.")
                elif entry.get("review_status") != "reviewed":
                    add("MARKER_REVIEW_PENDING", "blocking", f"{name}: marker {marker_name} remains unreviewed.")
                if not isinstance(count, int) or count < 0:
                    add("MARKER_COUNT_INVALID", "blocking", f"{name}: invalid count for marker {marker_name}.")

        if converted_book_ids:
            projected = _validate_projection_rows(converted, converted_book_ids, name, findings)
            unit_count += projected
            _validate_nodes(converted, name, findings)
            for row in converted.get("verse_projections", []):
                if isinstance(row, dict):
                    key = (row.get("source_book_id"), row.get("chapter_label"), row.get("verse_label"))
                    if all(isinstance(value, str) for value in key):
                        if key in all_addresses:
                            add("DUPLICATE_ARCHIVE_SOURCE_REFERENCE", "blocking", f"Duplicate source address {'.'.join(key)} across archive members.")
                        all_addresses.add(key)

    if file_count != len(members):
        add("CONVERSION_COVERAGE_INCOMPLETE", "blocking", "Not every inventoried USFM member has a valid converted output.")
    if isinstance(member_count, int) and file_count != member_count:
        add("CONVERSION_MEMBER_COUNT_MISMATCH", "blocking", "Converted file count does not match the expected archive USFM member count.")
    missing_core = sorted(CORE_66 - seen_books)
    if missing_core:
        add("CORE_CANON_INCOMPLETE", "blocking", "Source inventory is missing one or more Protestant 66-book IDs: " + ", ".join(missing_core))
    if expected.get("require_all_protestant_66") is not True:
        add("CANON_SCOPE_NOT_CONFIRMED", "blocking", "Preflight manifest must explicitly require all 66 Protestant-canon book IDs.")

    blocking_count = sum(x["severity"] == "blocking" for x in findings)
    warning_count = sum(x["severity"] == "warning" for x in findings)
    return {
        "schema_version": 1,
        "status": "passed" if blocking_count == 0 else "blocked",
        "ready_for_import": blocking_count == 0,
        "edition_id": edition_id if isinstance(edition_id, str) else None,
        "source_id": source_id if isinstance(source_id, str) else None,
        "territory": territory if isinstance(territory, str) else None,
        "findings": findings,
        "summary": {
            "archive_member_count": len(members),
            "converted_member_count": file_count,
            "core_book_count": len(seen_books & CORE_66),
            "distinct_book_id_count": len(seen_books),
            "verse_projection_count": unit_count,
            "distinct_marker_count": len(distinct_markers),
            "blocking_finding_count": blocking_count,
            "warning_count": warning_count,
            "pending_versification_proposal_ids": [
                item.get("proposal_id") for item in matching
                if not (
                    item.get("status") == "approved"
                    and isinstance(item.get("review"), dict)
                    and item["review"].get("review_status") == "approved"
                )
            ],
        },
        "policy_note": "A passed preflight only authorises a later reviewed staging transition; it does not publish text or override separate approval controls.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--rights-register", type=Path, default=Path("data/rights/translation-rights-register.json"))
    parser.add_argument("--marker-registry", type=Path, default=Path("data/usfm/marker-registry.json"))
    parser.add_argument("--proposals-dir", type=Path, default=Path("data/versification/proposals"))
    parser.add_argument("--output", type=Path, required=True, help="Metadata-only report destination")
    args = parser.parse_args()

    try:
        manifest = load_json(args.manifest, "preflight manifest")
        rights = load_json(args.rights_register, "translation rights register")
        registry = load_json(args.marker_registry, "marker registry")
        report = run_preflight(
            manifest,
            rights,
            registry,
            base_dir=args.manifest.parent,
            proposals_dir=args.proposals_dir,
        )
    except PreflightInputError as exc:
        report = {
            "schema_version": 1,
            "status": "blocked",
            "ready_for_import": False,
            "findings": [{
                "code": "PREFLIGHT_INPUT_ERROR",
                "severity": "blocking",
                "message": str(exc),
            }],
            "summary": {"blocking_finding_count": 1},
        }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": report["status"],
        "ready_for_import": report["ready_for_import"],
        "blocking_finding_count": report["summary"].get("blocking_finding_count", 1),
        "warning_count": report["summary"].get("warning_count", 0),
        "report": str(args.output),
    }, indent=2))
    return 0 if report["ready_for_import"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
