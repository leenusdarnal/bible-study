#!/usr/bin/env python3
"""Validate the conservative USFM marker registry and resolve markers losslessly."""
from __future__ import annotations
import argparse, json
from pathlib import Path
from typing import Any

CATEGORIES={"document","reference","metadata","heading","paragraph","poetry","list","annotation","character","break","peripheral"}
NODE_TYPES={"book_intro","chapter_heading","section_heading","paragraph","poetry_line_group","list","colophon","peripheral","other","span","footnote","cross_reference","milestone","unknown_marker","attribute","break","text"}

def validate_registry(data: Any) -> list[str]:
    errors=[]
    if not isinstance(data,dict) or data.get("schema_version") != 1:
        return ["registry must be an object with schema_version 1"]
    if not isinstance(data.get("markers"),list) or not data["markers"]:
        return ["markers must be a non-empty array"]
    seen=set()
    for i,item in enumerate(data["markers"]):
        prefix=f"markers[{i}]"
        if not isinstance(item,dict):
            errors.append(f"{prefix} must be an object"); continue
        for key in ("marker","category","semantic","node_type","review_status"):
            if not isinstance(item.get(key),str) or not item[key].strip():
                errors.append(f"{prefix}.{key} must be a non-empty string")
        marker=item.get("marker")
        if isinstance(marker,str):
            if marker in seen: errors.append(f"duplicate marker: {marker}")
            seen.add(marker)
        if item.get("category") not in CATEGORIES: errors.append(f"{prefix}.category is unsupported")
        if item.get("node_type") not in NODE_TYPES: errors.append(f"{prefix}.node_type is unsupported")
        if item.get("review_status") not in {"pending_review","reviewed"}: errors.append(f"{prefix}.review_status is unsupported")
    policy=data.get("unknown_marker_policy")
    required={"node_type":"unknown_marker","preserve_original_marker":True,"preserve_all_attributes":True,
              "preserve_text":True,"preserve_children":True,"preserve_source_order":True,
              "render_as_scripture_text":False,"requires_review":True}
    if not isinstance(policy,dict) or any(policy.get(k)!=v for k,v in required.items()):
        errors.append("unknown_marker_policy must preserve marker, attributes, text, children and order without rendering as Scripture text")
    coverage=data.get("coverage")
    if not isinstance(coverage,dict) or coverage.get("status") not in {"initial_partial","complete"}:
        errors.append("coverage.status must be initial_partial or complete")
    if coverage and coverage.get("status")=="complete" and coverage.get("review_status")!="reviewed":
        errors.append("complete coverage requires editorial review")
    return errors

def resolve_marker(registry: dict[str,Any], marker: str, *, attributes: dict[str,Any]|None=None,
                   text: str|None=None, children: list[Any]|None=None, source_order: int|None=None) -> dict[str,Any]:
    found=next((x for x in registry["markers"] if x["marker"]==marker),None)
    if found:
        return {"node_type":found["node_type"],"source_marker":marker,"semantic":found["semantic"],
                "attributes":attributes or {},"text":text,"children":children or [],
                "source_order":source_order,"review_status":found["review_status"]}
    return {"node_type":"unknown_marker","source_marker":marker,"semantic":None,
            "attributes":attributes or {},"text":text,"children":children or [],
            "source_order":source_order,"review_status":"pending_review"}

def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("registry",type=Path)
    args=parser.parse_args()
    try: data=json.loads(args.registry.read_text(encoding="utf-8"))
    except (OSError,json.JSONDecodeError) as exc:
        print(json.dumps({"valid":False,"errors":[str(exc)]},indent=2)); return 2
    errors=validate_registry(data)
    print(json.dumps({"valid":not errors,"marker_count":len(data.get("markers",[])) if isinstance(data,dict) else 0,"errors":errors},indent=2))
    return 0 if not errors else 1
if __name__=="__main__": raise SystemExit(main())
