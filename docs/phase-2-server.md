# Phase 2: Context Store & FastAPI Server Architecture

## Objectives
1. Implement a thread-safe, in-memory context store managing all 4 context scopes (`category`, `merchant`, `customer`, `trigger`).
2. Implement versioning, atomicity, and idempotency guarantees:
   - Identical or lower versions return HTTP 409 (`stale_version`).
   - Higher versions atomically replace prior state.
3. Construct the FastAPI server implementing the 5 required endpoints matching challenge schemas:
   - `GET /v1/healthz`
   - `GET /v1/metadata`
   - `POST /v1/context`
   - `POST /v1/tick`
   - `POST /v1/reply`
4. Implement conversation session state management (`conversation_id -> list[turn]`) for multi-turn tracking.
5. Provide a baseline heuristic response engine to pass warmup, auto-reply, intent transition, and hostile scenarios in `judge_simulator.py`.

---

## Endpoint Contract Specifications

### 1. `GET /v1/healthz`
**Response (200 OK)**:
```json
{
  "status": "ok",
  "uptime_seconds": 120,
  "contexts_loaded": {
    "category": 5,
    "merchant": 50,
    "customer": 200,
    "trigger": 100
  }
}
```

### 2. `GET /v1/metadata`
**Response (200 OK)**:
```json
{
  "team_name": "Antigravity Vera",
  "team_members": ["Garvit Bansal"],
  "model": "gemini-2.5-pro / claude-3-5-sonnet",
  "approach": "4-context modular composer with vertical voice profiles and Cialdini compulsion engineering",
  "contact_email": "garvit@example.com",
  "version": "1.0.0",
  "submitted_at": "2026-04-26T08:00:00Z"
}
```

### 3. `POST /v1/context`
**Payload**:
```json
{
  "scope": "merchant",
  "context_id": "m_001_drmeera",
  "version": 2,
  "payload": { ... },
  "delivered_at": "2026-04-26T10:00:00Z"
}
```
**Semantics**:
- If `existing_version >= version`: return HTTP 409 Conflict with `{"accepted": false, "reason": "stale_version", "current_version": existing_version}`.
- If `new`: insert and return HTTP 200 OK with `{"accepted": true, "ack_id": f"ack_{context_id}_v{version}", "stored_at": "..."}`.

### 4. `POST /v1/tick`
**Payload**:
```json
{
  "now": "2026-04-26T10:30:00Z",
  "available_triggers": ["trg_001_...", "trg_002_..."]
}
```
**Behavior**:
- Looks up triggers from context store.
- Matches `trigger.merchant_id` to `MerchantContext` and corresponding `CategoryContext`.
- Emits up to 20 structured action objects with unique `conversation_id`, `send_as`, `body`, `cta`, `suppression_key`, and `rationale`.

### 5. `POST /v1/reply`
**Payload**:
```json
{
  "conversation_id": "conv_001",
  "merchant_id": "m_001_drmeera",
  "customer_id": null,
  "from_role": "merchant",
  "message": "Ok lets do it. Whats next?",
  "received_at": "2026-04-26T10:45:00Z",
  "turn_number": 2
}
```
**Behavior**:
- Stores the turn in conversation history.
- Evaluates reply signals:
  - **Auto-Reply Loop**: If message matches canned pattern or duplicate messages: return `action: "end"`.
  - **Hostile / Unsubscribe**: If user requests STOP or shows anger: return `action: "end"` with polite closure.
  - **Commitment / Action Intent**: If merchant agrees ("let's do it", "yes", "proceed"): return `action: "send"` in **ACTION mode** without re-qualifying.
  - **Otherwise**: return `action: "send"` advancing conversation.

---

## Verification Outcomes
All core scenarios were executed against the running bot service (`http://localhost:8000`) and verified with `judge_simulator.py`:

- **Warmup**: `[PASS]` — `/v1/healthz` and `/v1/metadata` returned status 200, context pushes for all 5 categories and sample merchants succeeded.
- **Auto-Reply Loop**: `[PASS]` — Bot detected canned automated WhatsApp reply and returned `action: "end"` on turn 1.
- **Intent Transition**: `[PASS]` — Merchant commitment (*"Ok lets do it. Whats next?"*) triggered immediate action mode response without re-qualifying.
- **Hostile Handling**: `[PASS]` — Detected stop/spam request and gracefully ended outreach (`action: "end"`).
- **Phase 2 Short (Tick)**: `[PASS]` — Pushed triggers, evaluated active triggers, and produced 3 structured proactive actions with 10/10 specificity.

