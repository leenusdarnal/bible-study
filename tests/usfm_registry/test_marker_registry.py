"""Regression tests for the USFM marker registry and unknown-marker preservation."""
import json, sys, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"tools"))
from validate_usfm_marker_registry import resolve_marker, validate_registry

REGISTRY=json.loads((ROOT/"data/usfm/marker-registry.json").read_text(encoding="utf-8"))

class MarkerRegistryTests(unittest.TestCase):
    def test_registry_is_valid_and_marker_ids_are_unique(self):
        self.assertEqual(validate_registry(REGISTRY),[])
    def test_known_marker_resolves_to_structured_node(self):
        node=resolve_marker(REGISTRY,"s1",attributes={"level":1},text="Heading",source_order=7)
        self.assertEqual(node["node_type"],"section_heading")
        self.assertEqual(node["source_marker"],"s1")
        self.assertEqual(node["source_order"],7)
    def test_unknown_marker_is_retained_without_being_rendered_as_scripture(self):
        attrs={"custom":"value","sid":"GEN.1.1"}
        children=[{"node_type":"text","text":"retained"}]
        node=resolve_marker(REGISTRY,"zcustom",attributes=attrs,text="raw",children=children,source_order=12)
        self.assertEqual(node["node_type"],"unknown_marker")
        self.assertEqual(node["source_marker"],"zcustom")
        self.assertEqual(node["attributes"],attrs)
        self.assertEqual(node["text"],"raw")
        self.assertEqual(node["children"],children)
        self.assertEqual(node["source_order"],12)
        self.assertEqual(node["review_status"],"pending_review")
    def test_duplicate_markers_are_rejected(self):
        data={**REGISTRY,"markers":REGISTRY["markers"]+[REGISTRY["markers"][0]]}
        self.assertTrue(any("duplicate marker" in x for x in validate_registry(data)))
    def test_lossy_unknown_policy_is_rejected(self):
        data={**REGISTRY,"unknown_marker_policy":{**REGISTRY["unknown_marker_policy"],"preserve_text":False}}
        self.assertTrue(any("unknown_marker_policy" in x for x in validate_registry(data)))
    def test_complete_coverage_requires_editorial_review(self):
        data={**REGISTRY,"coverage":{"status":"complete","review_status":"pending_editorial_review"}}
        self.assertTrue(any("complete coverage" in x for x in validate_registry(data)))

if __name__=="__main__": unittest.main()
