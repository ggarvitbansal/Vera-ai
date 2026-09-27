# Phase 1: Environment & Dataset Setup

## Objectives
1. Set up an isolated Python virtual environment (`.venv`) adhering to repository python standards.
2. Install core runtime dependencies:
   - `fastapi` & `uvicorn` (high-performance async ASGI web server)
   - `pydantic` (strict payload validation matching challenge brief schemas)
   - `httpx` (async HTTP client)
   - `python-dotenv` (environment variable configuration for API keys)
3. Expand synthetic seed dataset using `dataset/generate_dataset.py` to create the full reference challenge dataset in `expanded/`:
   - 5 categories (`dentists`, `salons`, `restaurants`, `gyms`, `pharmacies`)
   - 50 merchants (10 per vertical)
   - 200 customers
   - 100 triggers (external & internal)
   - 30 canonical test pairs (`test_pairs.json`)
4. Verify data integrity and structure.

---

## Directory Structure After Phase 1
```
magicpin-ai-challenge/
├── .venv/                         # Python virtual environment
├── requirements.txt               # Pinned dependencies
├── dataset/                       # Seed dataset & expansion generator
│   ├── categories/                # 5 base CategoryContext JSONs
│   ├── merchants_seed.json        # 10 merchant seeds
│   ├── customers_seed.json        # 15 customer seeds
│   ├── triggers_seed.json         # 25 trigger seeds
│   └── generate_dataset.py        # Expansion script
├── expanded/                      # Generated challenge dataset
│   ├── categories/                # 5 vertical JSON files
│   ├── merchants/                 # 50 individual merchant JSON files
│   ├── customers/                 # 200 customer JSON files
│   ├── triggers/                  # 100 trigger JSON files
│   └── test_pairs.json            # 30 canonical benchmark evaluation pairs
├── docs/                          # Project documentation
│   ├── execution-plan.md          # Global roadmap & evaluation criteria
│   └── phase-1-setup.md           # This document
├── challenge-brief.md             # Core challenge brief
├── challenge-testing-brief.md     # Testing harness specification
└── judge_simulator.py             # Official local LLM evaluation harness
```

---

## Step-by-Step Implementation

### 1. Dataset Generation
Run:
```bash
python dataset/generate_dataset.py --seed-dir dataset --out expanded
```

### 2. Virtual Environment Creation
Run:
```bash
python -m venv .venv
```

### 3. Dependency Installation
Run:
```bash
.venv\Scripts\pip install fastapi uvicorn pydantic httpx python-dotenv
.venv\Scripts\pip freeze > requirements.txt
```

### 4. Verification Checkpoints
- [x] Check that `expanded/categories/` contains 5 files.
- [x] Check that `expanded/merchants/` contains 50 files.
- [x] Check that `expanded/customers/` contains 200 files.
- [x] Check that `expanded/triggers/` contains 100 files.
- [x] Check that `expanded/test_pairs.json` contains 30 pairs.
- [x] Virtual environment activates and packages import cleanly.
