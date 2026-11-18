#!/usr/bin/env python3
"""Convert one USFM member to deterministic, loss-preserving structured content JSON.

The output is a local staging artefact containing Scripture text. Keep it in a
private workspace; do not commit it or upload it as a public CI artefact.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import xml.etree.ElementTree as ET
from collections import Counter, OrderedDict
from pathlib import Path
from typing import Any

BLOCK_TYPES = {
    "book_intro", "chapter_heading", "section_heading", "paragraph",
    "poetry_line_group", "list", "colophon", "peripheral", "other",
}
NODE_TYPES = {
    "text", "span", "footnote", "cross_reference", "milestone",
    "unknown_marker", "attribute", "break",
}
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


class ConversionError(RuntimeError):
    """Raised when source input cannot be converted without guessing."""


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def local_name(tag: str) -> str:
    """Return the local XML name, including for a namespaced USX document."""
    return tag.rsplit("}", 1)[-1]


def stable_id(prefix: str, seed: str) -> str:
    return f"{prefix}_{hashlib.sha256(seed.encode('utf-8')).hexdigest()[:24]}"


def load_registry(path: Path) -> dict[str, Any]:
    try:
        registry = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ConversionError(f"Could not read marker registry: {type(exc).__name__}") from exc

    if not isinstance(registry, dict) or registry.get("schema_version") != 1:
        raise ConversionError("Unsupported marker registry schema.")
    if not isinstance(registry.get("markers"), list):
        raise ConversionError("Marker registry has no marker list.")
    entries: dict[str, dict[str, Any]] = {}
    for entry in registry["markers"]:
        if not isinstance(entry, dict) or not isinstance(entry.get("marker"), str):
            raise ConversionError("Marker registry contains an invalid entry.")
        marker = entry["marker"]
        if marker in entries:
            raise ConversionError(f"Duplicate marker in registry: {marker}")
        entries[marker] = entry
    return {**registry, "_index": entries}


def _attrs(element: ET.Element) -> dict[str, str]:
    return {str(k): str(v) for k, v in sorted(element.attrib.items())}


def _marker_for(element: ET.Element) -> str:
    name = local_name(element.tag)
    return element.attrib.get("style", name)


def _sid_reference(value: str) -> tuple[str | None, str | None]:
    """Extract chapter/verse from common BOOK.CHAPTER.VERSE milestone IDs."""
    parts = value.split(".")
    if len(parts) >= 3:
        return parts[-2], parts[-1]
    return None, None


class USXConverter:
    def __init__(
        self,
        *,
        registry: dict[str, Any],
        edition_id: str,
        source_id: str,
        source_member: str,
        source_sha256: str,
        parser: dict[str, str],
    ) -> None:
        self.registry = registry
        self.marker_index = registry["_index"]
        self.edition_id = edition_id
        self.source_id = source_id
        self.source_member = source_member
        self.source_sha256 = source_sha256
        self.parser = parser
        self.book_code: str | None = None
        self.book_name: str | None = None
        self.current_chapter: str | None = None
        self.current_verse_key: tuple[str, str, str] | None = None
        self.blocks: list[dict[str, Any]] = []
        self.events: list[dict[str, Any]] = []
        self.projections: OrderedDict[tuple[str, str, str], dict[str, Any]] = OrderedDict()
        self.marker_counts: Counter[str] = Counter()
        self.unresolved_markers: set[str] = set()
        self.pending_mappings: set[str] = set()
        self._node_counter = 0

    def _registry_entry(self, marker: str) -> dict[str, Any] | None:
        return self.marker_index.get(marker)

    def _record_marker(self, marker: str, entry: dict[str, Any] | None) -> None:
        self.marker_counts[marker] += 1
        if entry is None:
            self.unresolved_markers.add(marker)
        elif entry.get("review_status") != "reviewed":
            self.pending_mappings.add(marker)
        if marker not in {"c", "v"} and self.current_verse_key in self.projections:
            if entry is None or entry.get("review_status") != "reviewed":
                self.projections[self.current_verse_key]["review_required"] = True

    def _projection(self, chapter: str | None, verse: str | None) -> dict[str, Any] | None:
        if self.book_code is None or chapter is None or verse is None:
            return None
        key = (self.book_code, chapter, verse)
        if key not in self.projections:
            self.projections[key] = {
                "source_book_id": self.book_code,
                "chapter_label": chapter,
                "verse_label": verse,
                "text_parts": [],
                "annotation_count": 0,
                "review_required": False,
            }
        return self.projections[key]

    def _push_text(self, text: str | None, *, in_note: bool) -> None:
        if text is None or text == "":
            return
        if in_note or self.current_verse_key is None:
            return
        projection = self.projections.get(self.current_verse_key)
        if projection is not None:
            projection["text_parts"].append(text)

    def _new_node(
        self,
        *,
        marker: str,
        node_type: str,
        attributes: dict[str, Any],
        parent_id: str | None,
        parent_path: str,
        sibling_index: int,
        block_id: str,
        text_content: str | None = None,
        raw_value: str | None = None,
        semantic: str | None = None,
    ) -> dict[str, Any]:
        self._node_counter += 1
        source_order = self._node_counter
        segment = f"{sibling_index:06d}"
        node_path = f"{parent_path}.{segment}" if parent_path else segment
        seed = f"{self.edition_id}|{self.source_member}|{block_id}|{node_path}|{marker}"
        return {
            "id": stable_id("scn", seed),
            "block_id": block_id,
            "parent_node_id": parent_id,
            "node_order_path": node_path,
            "node_type": node_type,
            "source_marker": marker,
            "text_content": text_content,
            "attributes": ({**attributes, "_registry_semantic": semantic} if semantic else attributes),
            "raw_value": raw_value,
            "source_order": source_order,
            "children": [],
        }

    def _append_text_node(
        self,
        text: str | None,
        nodes: list[dict[str, Any]],
        *,
        parent_id: str | None,
        parent_path: str,
        block_id: str,
        in_note: bool,
    ) -> None:
        if text is None or text == "":
            return
        self._push_text(text, in_note=in_note)
        node = self._new_node(
            marker="text",
            node_type="text",
            attributes={},
            parent_id=parent_id,
            parent_path=parent_path,
            sibling_index=len(nodes) + 1,
            block_id=block_id,
            text_content=text,
        )
        nodes.append(node)

    def _visit_element(
        self,
        element: ET.Element,
        nodes: list[dict[str, Any]],
        *,
        parent_id: str | None,
        parent_path: str,
        block_id: str,
        in_note: bool,
    ) -> None:
        tag = local_name(element.tag)
        marker = _marker_for(element)
        entry = self._registry_entry(marker)
        attrs = _attrs(element)

        if tag in {"chapter", "verse"}:
            self._record_marker(marker, entry)
            is_end = "eid" in attrs and "number" not in attrs
            if tag == "chapter" and not is_end:
                number = attrs.get("number")
                if number:
                    self.current_chapter = number
                    self.current_verse_key = None
                elif attrs.get("sid"):
                    chapter_from_sid, _ = _sid_reference(attrs["sid"])
                    self.current_chapter = chapter_from_sid or self.current_chapter
                    self.current_verse_key = None
            elif tag == "verse" and not is_end:
                number = attrs.get("number")
                if not number and attrs.get("sid"):
                    _, number = _sid_reference(attrs["sid"])
                projection = self._projection(self.current_chapter, number)
                if projection is not None:
                    self.current_verse_key = (
                        self.book_code or "", self.current_chapter or "", number or ""
                    )
            node = self._new_node(
                marker=marker,
                node_type="milestone",
                attributes=attrs,
                parent_id=parent_id,
                parent_path=parent_path,
                sibling_index=len(nodes) + 1,
                block_id=block_id,
                semantic=("chapter_boundary" if tag == "chapter" else "verse_boundary"),
            )
            nodes.append(node)
            return

        if tag == "note":
            style = attrs.get("style", "")
            if style in {"f", "fe", "ef"}:
                node_type = "footnote"
                semantic = "footnote"
            elif style in {"x", "ex"}:
                node_type = "cross_reference"
                semantic = "cross_reference"
            else:
                node_type = "unknown_marker"
                semantic = None
            self.marker_counts[style or "note"] += 1
            self.pending_mappings.add(style or "note")
            projection = self.projections.get(self.current_verse_key) if self.current_verse_key else None
            if projection is not None:
                projection["annotation_count"] += 1
            node = self._new_node(
                marker=style or "note",
                node_type=node_type,
                attributes=attrs,
                parent_id=parent_id,
                parent_path=parent_path,
                sibling_index=len(nodes) + 1,
                block_id=block_id,
                semantic=semantic,
            )
            nodes.append(node)
            if node_type == "unknown_marker":
                self.unresolved_markers.add(style or "note")
            self._append_text_node(
                element.text, node["children"], parent_id=node["id"],
                parent_path=node["node_order_path"], block_id=block_id,
                in_note=True,
            )
            for child in list(element):
                self._visit_element(
                    child, node["children"], parent_id=node["id"],
                    parent_path=node["node_order_path"], block_id=block_id,
                    in_note=True,
                )
                self._append_text_node(
                    child.tail, node["children"], parent_id=node["id"],
                    parent_path=node["node_order_path"], block_id=block_id,
                    in_note=True,
                )
            return

        if tag == "char":
            category = entry.get("category") if entry else None
            if category == "character" or in_note:
                node_type = "span"
            else:
                node_type = "unknown_marker"
            self._record_marker(marker, entry)
            semantic = entry.get("semantic") if entry else None
        elif tag in {"optbreak", "br"}:
            node_type, semantic = "break", "optional_break"
            self._record_marker(marker, entry)
        elif tag in {"ms", "milestone"}:
            node_type, semantic = "milestone", "milestone"
            self._record_marker(marker, entry)
        else:
            node_type, semantic = "unknown_marker", None
            self._record_marker(marker, entry)

        stored_attrs: dict[str, Any] = {"source": attrs}
        if semantic:
            stored_attrs["registry_semantic"] = semantic
        node = self._new_node(
            marker=marker,
            node_type=node_type,
            attributes=stored_attrs,
            parent_id=parent_id,
            parent_path=parent_path,
            sibling_index=len(nodes) + 1,
            block_id=block_id,
            semantic=semantic,
        )
        nodes.append(node)
        self._append_text_node(
            element.text, node["children"], parent_id=node["id"],
            parent_path=node["node_order_path"], block_id=block_id,
            in_note=in_note,
        )
        for child in list(element):
            self._visit_element(
                child, node["children"], parent_id=node["id"],
                parent_path=node["node_order_path"], block_id=block_id,
                in_note=in_note,
            )
            self._append_text_node(
                child.tail, node["children"], parent_id=node["id"],
                parent_path=node["node_order_path"], block_id=block_id,
                in_note=in_note,
            )

    def _block_type(self, style: str) -> tuple[str, str | None]:
        entry = self._registry_entry(style)
        if entry is None:
            self._record_marker(style, None)
            return "other", None
        self._record_marker(style, entry)
        candidate = entry.get("node_type")
        if candidate in BLOCK_TYPES:
            return candidate, entry.get("semantic")
        return "other", entry.get("semantic")

    def _convert_block(
        self, element: ET.Element, source_order: int, block_order: int
    ) -> dict[str, Any]:
        style = element.attrib.get("style", "")
        tag = local_name(element.tag)
        block_type, semantic = self._block_type(style or tag)
        self._node_counter = 0
        block_id = stable_id(
            "scb", f"{self.edition_id}|{self.source_member}|{source_order}|{style or tag}"
        )
        nodes: list[dict[str, Any]] = []
        self._append_text_node(
            element.text, nodes, parent_id=None, parent_path="",
            block_id=block_id, in_note=False,
        )
        for child in list(element):
            self._visit_element(
                child, nodes, parent_id=None, parent_path="",
                block_id=block_id, in_note=False,
            )
            self._append_text_node(
                child.tail, nodes, parent_id=None, parent_path="",
                block_id=block_id, in_note=False,
            )
        flat_nodes: list[dict[str, Any]] = []

        def flatten(items: list[dict[str, Any]]) -> None:
            for item in items:
                children = item.get("children", [])
                flat_nodes.append({key: value for key, value in item.items() if key != "children"})
                flatten(children)

        flatten(nodes)
        return {
            "id": block_id,
            "edition_id": self.edition_id,
            "source_id": self.source_id,
            "source_member": self.source_member,
            "source_order": source_order,
            "block_order": block_order,
            "block_type": block_type,
            "source_marker": style or tag,
            "chapter_label": self.current_chapter,
            "anchor_source_unit": None,
            "metadata": {
                "source_tag": tag,
                "source_attributes": _attrs(element),
                "registry_semantic": semantic,
                "registry_review_status": (
                    self._registry_entry(style).get("review_status")
                    if style and self._registry_entry(style) else "pending_review"
                ),
            },
            "nodes": flat_nodes,
        }

    def convert(self, root: ET.Element) -> dict[str, Any]:
        if local_name(root.tag) != "usx":
            raise ConversionError("Expected a USX root element.")
        book = next((x for x in list(root) if local_name(x.tag) == "book"), None)
        if book is None:
            raise ConversionError("USX document has no book identity element.")
        self.book_code = book.attrib.get("code", "").upper() or None
        self.book_name = "".join(book.itertext()).strip() or None
        if not self.book_code or len(self.book_code) != 3:
            raise ConversionError("USX book identity must contain a three-character code.")

        block_order = 0
        for index, element in enumerate(list(root), start=1):
            tag = local_name(element.tag)
            if tag == "book":
                self.events.append({
                    "source_order": index,
                    "kind": "book_identity",
                    "book_code": self.book_code,
                    "book_name": self.book_name,
                    "attributes": _attrs(element),
                })
            elif tag == "chapter":
                attrs = _attrs(element)
                number = attrs.get("number")
                if number:
                    self.current_chapter = number
                    self.current_verse_key = None
                self.events.append({
                    "source_order": index,
                    "kind": "chapter_boundary",
                    "chapter_label": number,
                    "attributes": attrs,
                })
            elif tag == "para":
                block_order += 1
                self.blocks.append(self._convert_block(element, index, block_order))
            else:
                # Preserve non-paragraph source structures (e.g. tables, figures,
                # peripheral content) as an explicit generic content block.
                block_order += 1
                self.blocks.append(self._convert_block(element, index, block_order))

        verse_rows = []
        for (book_code, chapter, verse), item in self.projections.items():
            text_value = "".join(item["text_parts"])
            has_text = bool(text_value.strip())
            if has_text:
                content_state = "text"
            elif item["annotation_count"]:
                content_state = "annotation_only"
            else:
                content_state = "empty_marker"
            verse_rows.append({
                "source_book_id": book_code,
                "chapter_label": chapter,
                "verse_label": verse,
                "text": text_value,
                "content_state": content_state,
                "annotation_count": item["annotation_count"],
                "review_required": bool(item["review_required"]),
            })

        registry_coverage = self.registry.get("coverage", {})
        registry_reviewed = (
            registry_coverage.get("status") == "complete"
            and registry_coverage.get("review_status") == "reviewed"
            and all(x.get("review_status") == "reviewed" for x in self.registry["markers"])
        )
        readiness = "ready_for_editorial_validation" if registry_reviewed else "review_required"
        return {
            "schema_version": 1,
            "converter": {"name": "bible-study-usfm-structured-converter", "version": "0.1.0"},
            "source": {
                "source_id": self.source_id,
                "source_member": self.source_member,
                "source_sha256": self.source_sha256,
                "edition_id": self.edition_id,
                "parser": self.parser,
                "usx_version": root.attrib.get("version"),
            },
            "book": {"code": self.book_code, "name": self.book_name},
            "readiness": readiness,
            "marker_registry": {
                "registry_id": self.registry.get("registry_id"),
                "registry_version": self.registry.get("registry_version"),
                "coverage_status": registry_coverage.get("status"),
                "review_status": registry_coverage.get("review_status"),
            },
            "marker_counts": dict(sorted(self.marker_counts.items())),
            "unresolved_markers": sorted(self.unresolved_markers),
            "pending_marker_reviews": sorted(self.pending_mappings),
            "document_events": self.events,
            "content_blocks": self.blocks,
            "verse_projections": verse_rows,
            "projection_policy": {
                "include_character_text": True,
                "exclude_footnote_and_cross_reference_bodies": True,
                "preserve_unknown_marker_text": True,
                "unknown_marker_projection_requires_review": True,
            },
        }


def parse_input(path: Path, input_format: str, profile: str) -> tuple[ET.Element, dict[str, str]]:
    if input_format == "usx":
        try:
            root = ET.parse(path).getroot()
        except (OSError, ET.ParseError) as exc:
            raise ConversionError(f"Could not parse USX XML: {type(exc).__name__}") from exc
        return root, {"package": "ElementTree", "version": "stdlib", "compatibility_profile": "source_usx"}
    try:
        import usfmtc
    except ImportError as exc:
        raise ConversionError("Install the pinned parser first: pip install usfmtc==0.4.10") from exc
    try:
        document = usfmtc.readFile(str(path), informat="usfm", version=profile, strict=True)
        if document is None or document.getroot() is None:
            raise ConversionError("USFM parser returned no USX document.")
        errors = list(document.errors or [])
        if errors:
            raise ConversionError(f"USFM parser reported {len(errors)} error(s); source wording is omitted from diagnostics.")
        document.canonicalise()
        root = document.getroot()
    except ConversionError:
        raise
    except Exception as exc:
        raise ConversionError(f"USFM parsing failed: {type(exc).__name__}") from exc
    return root, {
        "package": "usfmtc",
        "version": str(getattr(usfmtc, "version", "unknown")),
        "compatibility_profile": profile,
        "publisher_declared_version": None,
    }


def validate_output(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if data.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    book = data.get("book", {})
    if not isinstance(book.get("code"), str) or len(book["code"]) != 3:
        errors.append("book.code must be a three-character identifier")
    source = data.get("source", {})
    if not SHA256_RE.fullmatch(str(source.get("source_sha256", ""))):
        errors.append("source.source_sha256 must be a lowercase SHA-256")
    block_ids: set[str] = set()
    for block in data.get("content_blocks", []):
        if block.get("block_type") not in BLOCK_TYPES:
            errors.append(f"unsupported block_type: {block.get('block_type')}")
        if block.get("id") in block_ids:
            errors.append(f"duplicate block id: {block.get('id')}")
        block_ids.add(block.get("id"))
        node_ids: set[str] = set()
        node_orders: set[int] = set()
        node_paths: set[str] = set()
        for node in block.get("nodes", []):
            if node.get("node_type") not in NODE_TYPES:
                errors.append(f"unsupported node_type: {node.get('node_type')}")
            if node.get("id") in node_ids:
                errors.append(f"duplicate node id: {node.get('id')}")
            if node.get("source_order") in node_orders:
                errors.append("duplicate node source_order within block")
            if node.get("node_order_path") in node_paths:
                errors.append("duplicate node_order_path within block")
            if node.get("parent_node_id") is not None and node["parent_node_id"] not in node_ids:
                errors.append("node parent must precede its child")
            node_ids.add(node.get("id"))
            node_orders.add(node.get("source_order"))
            node_paths.add(node.get("node_order_path"))
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="One .usfm/.sfm file or a canonical .usx XML file")
    parser.add_argument("--input-format", choices=("usfm", "usx"), default="usfm")
    parser.add_argument("--edition-id", required=True, help="Existing translation-edition identifier")
    parser.add_argument("--source-id", required=True, help="Source package identifier, e.g. engwebp or eng-kjv")
    parser.add_argument("--source-member", required=True, help="Original member path inside the source archive")
    parser.add_argument("--registry", type=Path, default=Path("data/usfm/marker-registry.json"))
    parser.add_argument("--output", type=Path, required=True, help="Private local JSON output path")
    parser.add_argument("--profile", choices=("2.5", "3.1"), default="2.5", help="USFMTC compatibility profile")
    parser.add_argument("--source-sha256", help="Optional expected SHA-256 of the input member bytes")
    parser.add_argument("--require-reviewed-registry", action="store_true")
    args = parser.parse_args()

    try:
        raw = args.input.read_bytes()
        digest = sha256(raw)
        if args.source_sha256 and args.source_sha256.lower() != digest:
            raise ConversionError("Input member SHA-256 does not match --source-sha256.")
        registry = load_registry(args.registry)
        coverage = registry.get("coverage", {})
        if args.require_reviewed_registry and not (
            coverage.get("status") == "complete"
            and coverage.get("review_status") == "reviewed"
            and all(x.get("review_status") == "reviewed" for x in registry["markers"])
        ):
            raise ConversionError("The marker registry is not complete and editorially reviewed.")
        root, parser_metadata = parse_input(args.input, args.input_format, args.profile)
        converted = USXConverter(
            registry=registry,
            edition_id=args.edition_id,
            source_id=args.source_id,
            source_member=args.source_member,
            source_sha256=digest,
            parser=parser_metadata,
        ).convert(root)
        errors = validate_output(converted)
        if errors:
            raise ConversionError("Converted structure failed validation: " + "; ".join(errors))
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(converted, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        summary = {
            "valid": True,
            "readiness": converted["readiness"],
            "book": converted["book"]["code"],
            "block_count": len(converted["content_blocks"]),
            "verse_projection_count": len(converted["verse_projections"]),
            "unresolved_marker_count": len(converted["unresolved_markers"]),
            "output": str(args.output),
            "note": "Output contains Scripture text; keep it in private staging storage.",
        }
        print(json.dumps(summary, indent=2))
        return 0
    except (OSError, ConversionError) as exc:
        print(json.dumps({"valid": False, "error": str(exc)}, indent=2), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
