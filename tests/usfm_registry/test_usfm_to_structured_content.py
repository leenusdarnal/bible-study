"""Synthetic regression tests for USFM-to-structured-content conversion."""
import sys
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from usfm_to_structured_content import (  # noqa: E402
    USXConverter,
    load_registry,
    validate_output,
)

REGISTRY = load_registry(ROOT / "data/usfm/marker-registry.json")
SOURCE_HASH = "a" * 64


def convert(xml: str):
    return USXConverter(
        registry=REGISTRY,
        edition_id="WEBP",
        source_id="engwebp",
        source_member="GEN.usfm",
        source_sha256=SOURCE_HASH,
        parser={
            "package": "fixture",
            "version": "1",
            "compatibility_profile": "synthetic-usx",
        },
    ).convert(ET.fromstring(xml))


FIXTURE = """\
<usx version="2.5">
  <book code="GEN" style="id">Genesis</book>
  <chapter number="1" style="c" />
  <para style="s1">Creation</para>
  <para style="p"><verse number="1" style="v" />In the <char style="bd">beginning</char> God created
    <note style="f" caller="+"><char style="fr">1:1 </char><char style="ft">Private note body.</char></note>
    the heavens and the earth.<verse number="2" style="v" />The earth was formless.</para>
  <para style="p"><verse number="3" style="v" /><note style="f" caller="+"><char style="ft">Only a note.</char></note></para>
  <para style="p"><verse number="4" style="v" /><char style="zunknown" custom="x">Unknown styled words.</char></para>
</usx>
"""


class USFMToStructuredContentTests(unittest.TestCase):
    def test_converts_book_chapter_blocks_and_verse_projections(self):
        result = convert(FIXTURE)
        self.assertEqual(result["book"], {"code": "GEN", "name": "Genesis"})
        self.assertEqual(result["document_events"][1]["kind"], "chapter_boundary")
        self.assertEqual(
            [block["block_type"] for block in result["content_blocks"]],
            ["section_heading", "paragraph", "paragraph", "paragraph"],
        )
        refs = [(x["chapter_label"], x["verse_label"]) for x in result["verse_projections"]]
        self.assertEqual(refs, [("1", "1"), ("1", "2"), ("1", "3"), ("1", "4")])

    def test_verse_text_includes_character_spans_but_excludes_note_bodies(self):
        result = convert(FIXTURE)
        verse_1 = result["verse_projections"][0]
        self.assertIn("In the beginning", verse_1["text"])
        self.assertIn("the heavens and the earth.", verse_1["text"])
        self.assertNotIn("Private note body.", verse_1["text"])
        self.assertEqual(verse_1["content_state"], "text")
        self.assertEqual(verse_1["annotation_count"], 1)

    def test_annotation_only_source_unit_is_preserved(self):
        result = convert(FIXTURE)
        verse_3 = result["verse_projections"][2]
        self.assertEqual(verse_3["text"], "")
        self.assertEqual(verse_3["content_state"], "annotation_only")
        self.assertEqual(verse_3["annotation_count"], 1)

    def test_unknown_inline_marker_and_attributes_are_preserved(self):
        result = convert(FIXTURE)
        verse_4 = result["verse_projections"][3]
        self.assertIn("Unknown styled words.", verse_4["text"])
        self.assertTrue(verse_4["review_required"])
        self.assertIn("zunknown", result["unresolved_markers"])
        unknown = next(
            node
            for block in result["content_blocks"]
            for node in block["nodes"]
            if node["node_type"] == "unknown_marker"
        )
        self.assertEqual(unknown["source_marker"], "zunknown")
        self.assertEqual(unknown["attributes"]["source"]["custom"], "x")

    def test_flat_node_rows_retain_parent_and_order_relationships(self):
        result = convert(FIXTURE)
        nodes = result["content_blocks"][1]["nodes"]
        ids = {node["id"] for node in nodes}
        self.assertTrue(all(
            node["parent_node_id"] is None or node["parent_node_id"] in ids
            for node in nodes
        ))
        self.assertEqual(
            [node["source_order"] for node in nodes],
            sorted(node["source_order"] for node in nodes),
        )
        self.assertEqual(len({node["node_order_path"] for node in nodes}), len(nodes))
        self.assertTrue(any(node["node_type"] == "footnote" for node in nodes))
        self.assertTrue(any(node["node_type"] == "span" for node in nodes))

    def test_conversion_is_deterministic(self):
        first = convert(FIXTURE)
        second = convert(FIXTURE)
        self.assertEqual(first["content_blocks"], second["content_blocks"])
        self.assertEqual(first["verse_projections"], second["verse_projections"])

    def test_output_passes_structural_validation_but_remains_review_required(self):
        result = convert(FIXTURE)
        self.assertEqual(validate_output(result), [])
        self.assertEqual(result["readiness"], "review_required")

    def test_malformed_document_without_book_is_rejected(self):
        converter = USXConverter(
            registry=REGISTRY,
            edition_id="WEBP",
            source_id="engwebp",
            source_member="bad.usfm",
            source_sha256=SOURCE_HASH,
            parser={"package": "fixture", "version": "1", "compatibility_profile": "test"},
        )
        with self.assertRaises(ValueError):
            converter.convert(ET.fromstring('<usx version="2.5"><para style="p">x</para></usx>'))


if __name__ == "__main__":
    unittest.main()
