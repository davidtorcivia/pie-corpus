#!/usr/bin/env python3
"""Before/after the page pass on the existing held-out review, no corpus writes.

Prints counts and coordinates only, never source running text. Development
positives include earlier fixes; held-out positives remain the complete w2 spans.
"""
import importlib.util
import json
from pathlib import Path
from pie import material_units as material

ROOT=Path(__file__).resolve().parents[1]


def audit():
    spec=importlib.util.spec_from_file_location('byliny_audit_w5',ROOT/'tests/byliny_material_audit.py')
    base=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(base)
    page=material.byliny_page_material
    results={}
    try:
        for label,fn in [('before',lambda lines:{}),('after',page)]:
            material.byliny_page_material=fn
            result=base.audit()
            result.pop('spot_check')
            result.pop('spot_check_seed')
            result['scores']['development']=result['scores'].pop('calibration')
            results[label]=result
    finally:
        material.byliny_page_material=page
    results['note']='Held-out set unchanged: 14 reviewed removals and 50 clear verse negatives; not population precision. No thresholds tuned on held-out results.'
    return results


if __name__=='__main__':
    print(json.dumps(audit(),ensure_ascii=False,indent=2))
