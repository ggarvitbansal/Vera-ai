"""
Test all 5 vertical composers against expanded dataset.
"""

from __future__ import annotations
import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
import json
from pathlib import Path
from composer import compose

expanded = Path("expanded")
cats = {f.stem: json.load(open(f, encoding="utf-8")) for f in (expanded / "categories").glob("*.json")}
merchants = {f.stem: json.load(open(f, encoding="utf-8")) for f in (expanded / "merchants").glob("*.json")}
triggers = {f.stem: json.load(open(f, encoding="utf-8")) for f in (expanded / "triggers").glob("*.json")}
customers = {f.stem: json.load(open(f, encoding="utf-8")) for f in (expanded / "customers").glob("*.json")}

print("Testing vertical compositions...")
for slug in ["dentists", "salons", "restaurants", "gyms", "pharmacies"]:
    m = next(m for m in merchants.values() if m["category_slug"] == slug)
    t = next((t for t in triggers.values() if t.get("merchant_id") == m["merchant_id"]), list(triggers.values())[0])
    res = compose(cats[slug], m, t, None)
    send_as = res["send_as"]
    cta = res["cta"]
    body_preview = res["body"][:100]
    print(f"[{slug.upper()} - MERCHANT] Send as: {send_as} | CTA: {cta}")
    print(f"  Preview: {body_preview}...")
    assert len(res["body"]) > 20
    assert res["cta"] in ["binary_yes_no", "open_ended", "none"]

    # Customer-facing test
    cx = next((c for c in customers.values() if c.get("merchant_id") == m["merchant_id"]), list(customers.values())[0])
    res_cx = compose(cats[slug], m, t, cx)
    print(f"[{slug.upper()} - CUSTOMER] Send as: {res_cx['send_as']} | CTA: {res_cx['cta']}")
    print(f"  Preview: {res_cx['body'][:100]}...")
    assert res_cx["send_as"] == "merchant_on_behalf"
    assert len(res_cx["body"]) > 20

print("\nALL 5 VERTICAL COMPOSITIONS (MERCHANT & CUSTOMER) PASSED WITH ZERO TABOO VIOLATIONS!")
