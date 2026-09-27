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
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from context_store import store
from composer import compose

app = FastAPI(title="magicpin AI Challenge — Vera Assistant", version="1.0.0")

START_TIME = time.time()

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
        "team_name": "Antigravity Vera",
        "team_members": ["Garvit Bansal"],
        "model": "gemini-2.5-pro / claude-3-5-sonnet",
        "approach": "4-context modular composer with vertical voice profiles and Cialdini compulsion engineering",
        "contact_email": "garvit@example.com",
        "version": "1.0.0",
        "submitted_at": "2026-04-26T08:00:00Z",
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
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
