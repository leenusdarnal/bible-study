"""Tests for metadata-only USX element and marker-style inventory."""

from __future__ import annotations

import sys
import types
import unittest
import xml.etree.ElementTree as ET

# The summary helper does not need the parser runtime; provide a tiny import stub
# so this unit test can run in the standard-library test phase before pip install.
sys.modules.setdefault("usfmtc", types.SimpleNamespace(version="test-stub"))
from tools.usfm_semantic_audit import summarise  # noqa: E402


class FakeDocument:
    def __init__(self, root: ET.Element) -> None:
        self.root = root

    def getroot(self) -> ET.Element:
        return self.root


class SemanticAuditSummaryTests(unittest.TestCase):
    def test_summary_counts_usx_elements_and_marker_styles_without_text(self) -> None:
        root = ET.fromstring(
            '<usx version="3.0"><book code="GEN" style="id"/><chapter number="1" style="c"/>'
            '<para style="p"><verse number="1" style="v"/><char style="add">Synthetic wording</char>'
            '<note style="f"><char style="ft">Synthetic note</char></note></para></usx>'
        )
        result = summarise(FakeDocument(root))
        self.assertEqual(result["book_codes"], ["GEN"])
        self.assertEqual(result["element_counts"]["para"], 1)
        self.assertEqual(result["element_counts"]["char"], 2)
        self.assertEqual(result["style_counts"]["add"], 1)
        self.assertEqual(result["style_counts"]["ft"], 1)
        self.assertNotIn("Synthetic wording", str(result))
        self.assertNotIn("Synthetic note", str(result))


if __name__ == "__main__":
    unittest.main()
