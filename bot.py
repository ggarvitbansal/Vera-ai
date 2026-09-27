"""
magicpin AI Challenge — Vera Bot HTTP Server
Implements the 5 required challenge API endpoints:
- GET  /v1/healthz
- GET  /v1/metadata
- POST /v1/context
- POST /v1/tick
- POST /v1/reply
"""

from __future__ import annotations
import time
import re
from datetime import datetime
from typing import Any, Dict, List, Optional
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import JSONResponse, HTMLResponse
from pydantic import BaseModel, Field

from context_store import store
from composer import compose

app = FastAPI(title="magicpin AI Challenge — Vera Assistant", version="1.0.0")

START_TIME = time.time()

LANDING_PAGE_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>magicpin AI Challenge — Vera Assistant</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
  <style>
    :root {
      --bg: #090d16;
      --card-bg: rgba(22, 30, 49, 0.7);
      --card-border: rgba(255, 255, 255, 0.08);
      --accent-magic: #e11d48;
      --accent-glow: #f43f5e;
      --accent-emerald: #10b981;
      --accent-blue: #3b82f6;
      --text-main: #f8fafc;
      --text-muted: #94a3b8;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: 'Outfit', sans-serif;
      background: radial-gradient(circle at 15% 15%, rgba(225, 29, 72, 0.12) 0%, transparent 40%),
                  radial-gradient(circle at 85% 85%, rgba(59, 130, 246, 0.10) 0%, transparent 40%),
                  var(--bg);
      color: var(--text-main);
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      padding: 2rem 1.5rem;
    }
    .container {
      width: 100%;
      max-width: 900px;
      backdrop-filter: blur(16px);
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: 20px;
      padding: 2.5rem;
      box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5), inset 0 1px 0 rgba(255, 255, 255, 0.08);
    }
    .header {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      margin-bottom: 2rem;
      flex-wrap: wrap;
      gap: 1rem;
    }
    .badge {
      display: inline-flex;
      align-items: center;
      gap: 0.5rem;
      background: rgba(16, 185, 129, 0.15);
      color: var(--accent-emerald);
      border: 1px solid rgba(16, 185, 129, 0.3);
      padding: 0.4rem 0.9rem;
      border-radius: 9999px;
      font-size: 0.85rem;
      font-weight: 500;
    }
    .pulse-dot {
      width: 8px;
      height: 8px;
      background: var(--accent-emerald);
      border-radius: 50%;
      box-shadow: 0 0 10px var(--accent-emerald);
      animation: pulse 2s infinite;
    }
    @keyframes pulse {
      0%, 100% { opacity: 1; transform: scale(1); }
      50% { opacity: 0.4; transform: scale(0.85); }
    }
    h1 {
      font-size: 2.25rem;
      font-weight: 700;
      letter-spacing: -0.02em;
      margin-bottom: 0.5rem;
      background: linear-gradient(135deg, #ffffff 0%, #cbd5e1 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }
    .brand-accent {
      color: var(--accent-magic);
      -webkit-text-fill-color: var(--accent-magic);
    }
    p.subtitle {
      color: var(--text-muted);
      font-size: 1.05rem;
      line-height: 1.6;
    }
    .grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
      gap: 1.25rem;
      margin-top: 2rem;
    }
    .card {
      background: rgba(15, 23, 42, 0.6);
      border: 1px solid rgba(255, 255, 255, 0.05);
      border-radius: 14px;
      padding: 1.25rem;
      transition: all 0.2s ease;
      text-decoration: none;
      color: inherit;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
    }
    .card:hover {
      transform: translateY(-2px);
      border-color: rgba(244, 63, 94, 0.4);
      box-shadow: 0 10px 25px -5px rgba(225, 29, 72, 0.15);
    }
    .method-tag {
      font-family: 'JetBrains Mono', monospace;
      font-size: 0.75rem;
      font-weight: 700;
      padding: 0.2rem 0.5rem;
      border-radius: 6px;
      display: inline-block;
      margin-bottom: 0.75rem;
      width: fit-content;
    }
    .get-tag { background: rgba(59, 130, 246, 0.2); color: #60a5fa; }
    .post-tag { background: rgba(16, 185, 129, 0.2); color: #34d399; }
    .docs-tag { background: rgba(244, 63, 94, 0.2); color: #fb7185; }
    .card-title {
      font-size: 1.1rem;
      font-weight: 600;
      margin-bottom: 0.35rem;
    }
    .card-desc {
      color: var(--text-muted);
      font-size: 0.875rem;
      line-height: 1.4;
    }
    .features-list {
      display: flex;
      flex-wrap: wrap;
      gap: 0.5rem;
      margin-top: 2rem;
      padding-top: 1.5rem;
      border-top: 1px solid rgba(255, 255, 255, 0.08);
    }
    .chip {
      background: rgba(255, 255, 255, 0.05);
      border: 1px solid rgba(255, 255, 255, 0.07);
      padding: 0.35rem 0.75rem;
      border-radius: 8px;
      font-size: 0.8rem;
      color: #cbd5e1;
    }
    .footer {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-top: 2rem;
      font-size: 0.85rem;
      color: var(--text-muted);
      flex-wrap: wrap;
      gap: 1rem;
    }
    .footer a {
      color: #38bdf8;
      text-decoration: none;
    }
    .footer a:hover {
      text-decoration: underline;
    }
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <div>
        <h1>magicpin <span class="brand-accent">Vera</span> Engine</h1>
        <p class="subtitle">Autonomous Merchant Growth Partner & Cialdini Message Composer</p>
      </div>
      <div class="badge">
        <span class="pulse-dot"></span>
        Live & Ready
      </div>
    </div>

    <div class="grid">
      <a href="/docs" class="card" target="_blank">
        <div>
          <span class="method-tag docs-tag">OPENAPI</span>
          <div class="card-title">Interactive Docs (/docs)</div>
          <div class="card-desc">Interactive Swagger UI explorer for testing all challenge endpoints live in your browser.</div>
        </div>
      </a>

      <a href="/v1/healthz" class="card" target="_blank">
        <div>
          <span class="method-tag get-tag">GET</span>
          <div class="card-title">Healthz (/v1/healthz)</div>
          <div class="card-desc">Liveness probe returning server uptime and in-memory context store counts.</div>
        </div>
      </a>

      <a href="/v1/metadata" class="card" target="_blank">
        <div>
          <span class="method-tag get-tag">GET</span>
          <div class="card-title">Metadata (/v1/metadata)</div>
          <div class="card-desc">Bot registration metadata, author information, architecture summary, and versioning.</div>
        </div>
      </a>

      <div class="card">
        <div>
          <span class="method-tag post-tag">POST</span>
          <div class="card-title">API Endpoints</div>
          <div class="card-desc"><code>/v1/context</code> (4-Context state store)<br><code>/v1/tick</code> (Proactive outreach trigger)<br><code>/v1/reply</code> (Multi-turn conversational bot)</div>
        </div>
      </div>
    </div>

    <div class="features-list">
      <span class="chip">🎯 4-Context Framework</span>
      <span class="chip">🦷 Dentists</span>
      <span class="chip">💇‍♀️ Salons</span>
      <span class="chip">🍕 Restaurants</span>
      <span class="chip">🏋️ Gyms</span>
      <span class="chip">💊 Pharmacies</span>
      <span class="chip">🛡️ Anti-Loop Guardrails</span>
      <span class="chip">⚡ Sub-50ms Response</span>
    </div>

    <div class="footer">
      <div>Built for the <strong>magicpin AI Challenge</strong></div>
      <div><a href="https://github.com/ggarvitbansal/Vera-ai" target="_blank">GitHub Repository ↗</a></div>
    </div>
  </div>
</body>
</html>
"""


@app.get("/", response_class=HTMLResponse)
async def root():
    return HTMLResponse(content=LANDING_PAGE_HTML)


# Multi-turn conversation store: conversation_id -> list of turn dicts
conversations: Dict[str, List[Dict[str, Any]]] = {}

# Patterns for multi-turn detection
AUTO_REPLY_PATTERNS = [
    r"thank you for contacting",
    r"automated assistant",
    r"automated message",
    r"respond shortly",
    r"our team will",
    r"hamari team tak",
    r"automated reply",
    r"we will get back",
    r"canned",
]

HOSTILE_PATTERNS = [
    r"stop messaging",
    r"useless spam",
    r"stop",
    r"spam",
    r"unsubscribe",
    r"leave me alone",
    r"don't message",
    r"do not message",
]

ACTION_COMMITMENT_PATTERNS = [
    r"let['’]?s do it",
    r"what['’]?s next",
    r"go ahead",
    r"proceed",
    r"send me",
    r"kardo",
    r"start",
    r"join",
    r"ok lets",
    r"yes, send",
]

WAIT_PATTERNS = [
    r"give me (some )?time",
    r"call later",
    r"busy right now",
    r"kal baat",
    r"later",
]


# =============================================================================
# 1. /v1/healthz — Liveness probe
# =============================================================================
@app.get("/v1/healthz")
async def healthz():
    uptime = int(time.time() - START_TIME)
    counts = store.counts()
    return {
        "status": "ok",
        "uptime_seconds": uptime,
        "contexts_loaded": counts,
    }


# =============================================================================
# 2. /v1/metadata — Bot metadata
# =============================================================================
@app.get("/v1/metadata")
async def metadata():
    return {
        "team_name": "vera bot builders",
        "team_members": ["Garvit Bansal"],
        "model": "openai/gpt-4o-mini",
        "approach": "4-context modular composer with vertical voice profiles and Cialdini compulsion engineering",
        "contact_email": "garvitbansal_23cs152@dtu.ac.in",
        "version": "1.0.0",
        "submitted_at": "2026-04-27",
    }


# =============================================================================
# 3. /v1/context — Push context update
# =============================================================================
class CtxBody(BaseModel):
    scope: str
    context_id: str
    version: int
    payload: Dict[str, Any]
    delivered_at: Optional[str] = None


@app.post("/v1/context")
async def push_context(body: CtxBody):
    accepted, reason, cur_ver = store.push(
        scope=body.scope,
        context_id=body.context_id,
        version=body.version,
        payload=body.payload,
    )
    if not accepted:
        return JSONResponse(
            status_code=409,
            content={
                "accepted": False,
                "reason": reason or "stale_version",
                "current_version": cur_ver,
            },
        )

    return {
        "accepted": True,
        "ack_id": f"ack_{body.context_id}_v{body.version}",
        "stored_at": datetime.utcnow().isoformat() + "Z",
    }


# =============================================================================
# 4. /v1/tick — Periodic evaluation & proactive triggers
# =============================================================================
class TickBody(BaseModel):
    now: str
    available_triggers: List[str] = Field(default_factory=list)


@app.post("/v1/tick")
async def tick(body: TickBody):
    actions = []

    for trg_id in body.available_triggers:
        if len(actions) >= 20:
            break

        trigger = store.get("trigger", trg_id)
        if not trigger:
            continue

        merchant_id = trigger.get("merchant_id")
        customer_id = trigger.get("customer_id")
        merchant = store.get("merchant", merchant_id) if merchant_id else None
        if not merchant:
            continue

        category_slug = merchant.get("category_slug")
        category = store.get("category", category_slug) or {"slug": category_slug}
        customer = store.get("customer", customer_id) if customer_id else None

        composed = compose(category=category, merchant=merchant, trigger=trigger, customer=customer)

        cat_slug = category.get("slug", "generic")
        actions.append(
            {
                "conversation_id": f"conv_{merchant_id}_{trg_id}",
                "merchant_id": merchant_id,
                "customer_id": customer_id,
                "send_as": composed["send_as"],
                "trigger_id": trg_id,
                "template_name": f"vera_{cat_slug}_v1",
                "template_params": [
                    merchant.get("identity", {}).get("name", ""),
                    merchant.get("identity", {}).get("locality", ""),
                ],
                "body": composed["body"],
                "cta": composed["cta"],
                "suppression_key": composed["suppression_key"],
                "rationale": composed["rationale"],
            }
        )

    return {"actions": actions}


# =============================================================================
# 5. /v1/reply — Multi-turn incoming messages
# =============================================================================
class ReplyBody(BaseModel):
    conversation_id: str
    merchant_id: Optional[str] = None
    customer_id: Optional[str] = None
    from_role: str = "merchant"
    message: str
    received_at: Optional[str] = None
    turn_number: int = 1


OFF_TOPIC_PATTERNS = [
    r"\bgst\b",
    r"\btax(es)?\b",
    r"\baccounting\b",
    r"\bloan\b",
    r"\bcredit\b",
    r"\bhire\b",
    r"\bjob\b",
]

# Track sent bot bodies to prevent verbatim repetition: conversation_id -> set of body strings
sent_bot_bodies: Dict[str, List[str]] = {}


@app.post("/v1/reply")
async def reply(body: ReplyBody):
    cid = body.conversation_id
    history = conversations.setdefault(cid, [])
    prior_bot_sends = sent_bot_bodies.setdefault(cid, [])
    msg_clean = body.message.strip().lower()

    # Track prior messages from this role
    prior_messages = [t["msg"].strip().lower() for t in history if t["from"] == body.from_role]
    history.append({"from": body.from_role, "msg": body.message, "turn": body.turn_number})

    # A. Check for Auto-Reply Canned Loop
    is_canned_match = any(re.search(pat, msg_clean) for pat in AUTO_REPLY_PATTERNS)
    is_repeated_msg = prior_messages.count(msg_clean) >= 1

    if is_canned_match or is_repeated_msg:
        return {
            "action": "end",
            "rationale": "Detected canned WhatsApp Business auto-reply pattern; ending conversation gracefully to avoid burning turns.",
        }

    # B. Check for Hostility / STOP request
    if any(re.search(pat, msg_clean) for pat in HOSTILE_PATTERNS):
        return {
            "action": "end",
            "rationale": "Merchant opted out / expressed hostility; gracefully terminating outreach immediately.",
        }

    # C. Check for Wait / Delay request
    if any(re.search(pat, msg_clean) for pat in WAIT_PATTERNS):
        return {
            "action": "wait",
            "wait_seconds": 1800,
            "rationale": "Merchant requested time to review; paused conversation for 30 minutes.",
        }

    # D. Check for Commitment / Action Intent Transition
    if any(re.search(pat, msg_clean) for pat in ACTION_COMMITMENT_PATTERNS):
        # Must be in ACTION mode (use actioning words: done, sending, draft, here, proceed)
        # Avoid qualifying questions ("would you", "can you tell", etc.)
        response_body = (
            "Done! I have prepared the initial draft for your review. Next step: confirm your preferred offer price and we will launch the post immediately. Reply with your price to proceed."
        )
        prior_bot_sends.append(response_body)
        return {
            "action": "send",
            "body": response_body,
            "cta": "open_ended",
            "rationale": "Merchant confirmed commitment; immediately transitioned to action mode without asking qualifying questions.",
        }

    # E. Check for Off-Topic Questions (e.g. GST, taxes, accounting)
    if any(re.search(pat, msg_clean) for pat in OFF_TOPIC_PATTERNS):
        response_body = (
            "Samajh gayi! magicpin Vera specifically focuses on growing your Google Business Profile, walk-ins, and local orders. While I cannot assist with GST or accounting, I can help you drive more customer footfall this week. Would you like me to schedule a promotion for your active offers? Reply YES."
        )
        prior_bot_sends.append(response_body)
        return {
            "action": "send",
            "body": response_body,
            "cta": "binary_yes_no",
            "rationale": "Politely acknowledged off-topic query, defined core competence boundary, and guided merchant back to local business growth.",
        }

    # F. Default follow-up with anti-repetition guard
    default_1 = "Samajh gayi! Here is the draft ready to share. Would you like me to send it now? Reply YES."
    default_2 = "Understood! I have updated the campaign draft for your review. Would you like me to launch it now? Reply YES."

    response_body = default_2 if default_1 in prior_bot_sends else default_1
    prior_bot_sends.append(response_body)

    return {
        "action": "send",
        "body": response_body,
        "cta": "binary_yes_no",
        "rationale": "Acknowledged input and proposed immediate binary confirmation to advance workflow.",
    }


if __name__ == "__main__":
    import os
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
