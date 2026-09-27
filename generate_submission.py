"""
Generate submission.jsonl covering the 30 canonical test pairs in expanded/test_pairs.json.
Format matches challenge-brief.md §7.2:
{"test_id": "T01", "body": "...", "cta": "...", "send_as": "...", "suppression_key": "...", "rationale": "..."}
"""

from __future__ import annotations
import json
from pathlib import Path
from composer import compose

def main():
    root = Path(__file__).parent
    expanded = root / "expanded"
    pairs_file = expanded / "test_pairs.json"
    
    if not pairs_file.exists():
        print(f"Error: {pairs_file} not found. Run dataset generation first.")
        return

    with open(pairs_file, "r", encoding="utf-8") as f:
        pairs_data = json.load(f)

    test_pairs = pairs_data.get("pairs", [])
    print(f"Loaded {len(test_pairs)} canonical test pairs.")

    # Load categories cache
    categories = {}
    for p in (expanded / "categories").glob("*.json"):
        with open(p, "r", encoding="utf-8") as f:
            data = json.load(f)
            categories[data.get("slug", p.stem)] = data

    submission_lines = []

    for pair in test_pairs:
        test_id = pair["test_id"]
        trigger_id = pair["trigger_id"]
        merchant_id = pair["merchant_id"]
        customer_id = pair.get("customer_id")

        with open(expanded / "triggers" / f"{trigger_id}.json", "r", encoding="utf-8") as f:
            trigger = json.load(f)

        with open(expanded / "merchants" / f"{merchant_id}.json", "r", encoding="utf-8") as f:
            merchant = json.load(f)

        cat_slug = merchant.get("category_slug", "dentists")
        category = categories.get(cat_slug, {})

        customer = None
        if customer_id:
            c_path = expanded / "customers" / f"{customer_id}.json"
            if c_path.exists():
                with open(c_path, "r", encoding="utf-8") as f:
                    customer = json.load(f)

        comp = compose(category=category, merchant=merchant, trigger=trigger, customer=customer)

        entry = {
            "test_id": test_id,
            "body": comp["body"],
            "cta": comp["cta"],
            "send_as": comp["send_as"],
            "suppression_key": comp["suppression_key"],
            "rationale": comp["rationale"],
        }
        submission_lines.append(entry)

    out_file = root / "submission.jsonl"
    with open(out_file, "w", encoding="utf-8") as f:
        for item in submission_lines:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")

    print(f"Successfully generated {len(submission_lines)} records in {out_file.name}!")


if __name__ == "__main__":
    main()
