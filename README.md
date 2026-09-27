# magicpin AI Challenge — Vera Assistant

High-compulsion WhatsApp merchant AI assistant built for the **magicpin AI Challenge**.

Rebuilding and outperforming **Vera** — magicpin's merchant assistant serving ~100,000 local merchants across India in 5 primary verticals (**Dentists, Salons, Restaurants, Gyms, Pharmacies**).

---

## Architecture: The 4-Context Framework

Every message is composed from four structured context layers:

```
compose(CategoryContext, MerchantContext, TriggerContext, CustomerContext?) -> ComposedMessage
```

1. **CategoryContext**: Vertical voice profile, clinical/operator tone, taboos, peer benchmarks, research digests.
2. **MerchantContext**: Business identity, owner, locality, language preferences, active catalog offers, performance history, customer aggregates.
3. **TriggerContext**: The "why now" anchor (recalls, performance deltas, research publications, competitor openings, events).
4. **CustomerContext** *(optional)*: Direct customer outreach attributes (relationship history, lapse state, slot preferences, consent).

---

## Key Features

- **Decision Quality**: Selects the single highest-value hook for this moment rather than dumping raw context.
- **Strict Grounding & Zero Hallucination**: Every number, date, offer price, and citation is drawn directly from the input context layers.
- **Vertical Specialization**: Clinical-peer tone for Dentists, warm-practical for Salons, operator-to-operator for Restaurants, motivational coach for Gyms, trustworthy-precise for Pharmacies.
- **Language Intelligence**: Automatically matches merchant and customer language preferences, incorporating natural Hinglish code-mixing where preferred.
- **Multi-Turn Resilience**:
  - **Auto-Reply Loop Detector**: Identifies WhatsApp Business canned replies on turn 1 and exits gracefully (`action: "end"`).
  - **Intent Transition Handler**: Instantly transitions to action execution when the merchant commits (*"let's do it"* / *"proceed"*), eliminating redundant qualification questions.
  - **Hostility & Opt-Out Filter**: Respects user stop requests immediately with clean closure.

---

## API Contract (5 Endpoints)

| Endpoint | Method | Description |
|---|---|---|
| `/v1/healthz` | GET | Liveness probe with uptime and loaded context counts |
| `/v1/metadata` | GET | Team and bot metadata |
| `/v1/context` | POST | Atomic, idempotent context ingestion with version conflict detection (HTTP 409) |
| `/v1/tick` | POST | Periodic trigger evaluation returning up to 20 prioritized action payloads |
| `/v1/reply` | POST | Multi-turn conversational handler returning `send`, `wait`, or `end` |

---

## Getting Started

### 1. Environment Setup
```bash
# Initialize virtual environment
python -m venv .venv

# Activate (Windows)
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Generate Challenge Dataset
```bash
python dataset/generate_dataset.py --seed-dir dataset --out expanded
```

### 3. Run the Bot Server
```bash
uvicorn bot:app --host 0.0.0.0 --port 8000
```

### 4. Run the Evaluation Judge Simulator
```bash
python judge_simulator.py
```

---

## Documentation
- [docs/execution-plan.md](docs/execution-plan.md) — Comprehensive challenge analysis, scoring rubric, and 6-phase roadmap.
- [docs/phase-1-setup.md](docs/phase-1-setup.md) — Environment setup & dataset expansion details.
- [docs/phase-2-server.md](docs/phase-2-server.md) — Context store, FastAPI server, and verified test results.
