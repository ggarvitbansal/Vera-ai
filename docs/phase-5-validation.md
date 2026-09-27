# Phase 5: Verification & Benchmark Evaluation

## Objectives
1. Perform comprehensive local validation against `judge_simulator.py`.
2. Generate the static canonical `submission.jsonl` covering all 30 test pairs from `expanded/test_pairs.json`.
3. Audit outputs across the 5 evaluation dimensions:
   - Decision Quality
   - Specificity (10/10)
   - Category Fit
   - Merchant Fit
   - Engagement Compulsion

---

## Generated Canonical Artifact: `submission.jsonl`
- Generated using `generate_submission.py`.
- Formatted as 30 JSON Lines (one per canonical test pair).
- Contains:
  - `test_id` (T01 - T30)
  - `body` (Grounded message)
  - `cta` (`binary_yes_no` | `open_ended` | `none`)
  - `send_as` (`vera` | `merchant_on_behalf`)
  - `suppression_key`
  - `rationale`

---

## Local Judge Simulator Verification Matrix

| Test Suite | Target | Status | Observed Behavior |
|---|---|---|---|
| `warmup` | Endpoint Health & Metadata | `PASS` | `/v1/healthz` (200 OK), `/v1/metadata` (200 OK), context push for 5 categories & 10 merchants. |
| `auto_reply_hell` | Canned WA Auto-Reply | `PASS` | Identified repetitive automated canned response on turn 1 and terminated (`action: "end"`). |
| `intent_transition` | Immediate Action Mode | `PASS` | Transitioned directly to campaign drafting upon commitment without asking qualifying questions. |
| `hostile` | Hostility & Opt-Out | `PASS` | Ended interaction gracefully on STOP/spam request (`action: "end"`). |
| `phase2_short` | Tick Proactive Composition | `PASS` | Evaluated active triggers and generated 3 actions with **10/10 Specificity** and zero hallucinations. |
| `all` | Full Test Harness | `PASS` | 100% pass across all scenarios. |
