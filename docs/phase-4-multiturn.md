# Phase 4: Multi-Turn Conversation & Replay Handlers

## Objectives
1. Implement advanced multi-turn conversation resilience and state tracking across WhatsApp session windows.
2. Handle the 3 Phase 4 Replay Stress Scenarios defined by the judge:
   - **Auto-Reply Hell**: Identify canned WhatsApp Business automated messages ("Thank you for contacting...", "automated reply", repeated messages) and exit gracefully with `action: "end"` to avoid wasting turns.
   - **Intent Transition**: When the merchant signals commitment (*"Ok lets do it. Whats next?"*, *"kardo"*, *"go ahead"*), immediately transition to **ACTION mode** (using action terms: *done, sending, draft, here, proceed*) and strictly avoid regression into qualifying questions.
   - **Hostile & Off-Topic Requests**:
     - Explicit opt-out / STOP requests: End outreach politely without arguing (`action: "end"`).
     - Off-topic diversions (e.g., *"Can you help me file my GST?"*): Acknowledge politely and steer back to the core GBP & local growth mission.
3. Multi-turn Cadence & Anti-Repetition:
   - Track prior bot sends within the session to ensure the bot never repeats the same message verbatim.
   - Support mid-conversation language shifts (English to Hindi).

---

## State Model
Each conversation tracks:
- `conversation_id`: Unique identifier
- `turns`: Array of `{"turn": int, "from": "merchant"|"customer"|"vera", "msg": str, "timestamp": str}`
- `intent_state`: `"initial"` -> `"pitching"` -> `"action_pending"` -> `"action_completed"` -> `"ended"`
- `sent_bodies`: Set of previous bot messages to prevent repetition penalties.
