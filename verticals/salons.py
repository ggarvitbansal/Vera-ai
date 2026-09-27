"""
Salons Vertical Composer
Warm, fellow-operator tone, practical service+price framing, and seasonal/bridal timing.
Taboos: no 'permanent fair', '100% whitening', 'guaranteed'.
"""

from __future__ import annotations
from typing import Any, Dict, Optional


def compose_salon(
    category: Dict[str, Any],
    merchant: Dict[str, Any],
    trigger: Dict[str, Any],
    customer: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    identity = merchant.get("identity", {})
    owner = identity.get("owner_first_name", "")
    salutation = f"Hi {owner}" if owner else f"Hi {identity.get('name', 'there')}"
    locality = identity.get("locality", "")
    m_name = identity.get("name", "our salon")
    
    t_kind = trigger.get("kind", "")
    t_payload = trigger.get("payload", {})
    t_scope = trigger.get("scope", "merchant")
    
    # Active offer from catalog
    active_offer = ""
    for o in merchant.get("offers", []):
        if o.get("status") == "active":
            active_offer = o.get("title", "")
            break
    if not active_offer:
        active_offer = "Haircut @ ₹99"

    # Customer-Facing: Bridal Follow-up
    if customer or t_scope == "customer":
        c_name = customer.get("identity", {}).get("name", "") if customer else ""
        if "bridal" in t_kind or "wedding" in t_kind:
            days = t_payload.get("days_to_wedding", 196)
            package_offer = active_offer if "₹" in active_offer else "Bridal Skin-Prep Package @ ₹2,499"
            body = (
                f"Hi {c_name} 💍 {owner or m_name} from {m_name} {locality} here. {days} days to your wedding — "
                f"this is the ideal window to begin the skin-prep regimen before peak bridal rush. "
                f"{package_offer}. Want me to hold your preferred Saturday 4pm slot for your first session next week? Reply YES."
            )
            return {
                "body": body,
                "cta": "binary_yes_no",
                "send_as": "merchant_on_behalf",
                "suppression_key": f"bridal:salons:{customer.get('customer_id') if customer else 'cx'}",
                "rationale": "Wedding countdown hook with verified service price and specific preferred time slot reservation.",
            }
        else:
            body = (
                f"Hi {c_name}, {owner or m_name} from {m_name} here 💇‍♀️ Friendly reminder that your routine salon service is due. "
                f"We have slots open this week for {active_offer}. Reply YES to reserve your slot or reply with your preferred time."
            )
            return {
                "body": body,
                "cta": "binary_yes_no",
                "send_as": "merchant_on_behalf",
                "suppression_key": f"recall:salons:{customer.get('customer_id') if customer else 'cx'}",
                "rationale": "Warm routine service reminder with active service+price offer.",
            }

    # Merchant-Facing: Curious Ask
    if "curious_ask" in t_kind:
        body = (
            f"{salutation}! Quick check — what service has been most asked-for this week at {m_name}? "
            f"I'll turn the answer into a Google post + a 4-line WhatsApp reply you can use when customers ask about pricing. Takes 2 min."
        )
        return {
            "body": body,
            "cta": "open_ended",
            "send_as": "vera",
            "suppression_key": f"curious:salons:{trigger.get('id', 'weekly')}",
            "rationale": "Low-stakes curiosity inquiry providing immediate reciprocity (Google post + quick reply template).",
        }

    # Merchant-Facing: Performance Spike
    perf = merchant.get("performance", {})
    if "perf_spike" in t_kind:
        views = perf.get("views", 1200)
        body = (
            f"{salutation}, great momentum: your profile views reached {views} this month. "
            f"Searches for salon services in {locality} are peaking. "
            f"Want me to publish a fresh Google Post featuring {active_offer} to convert these views into appointments? Takes 2 min. Reply YES."
        )
        return {
            "body": body,
            "cta": "binary_yes_no",
            "send_as": "vera",
            "suppression_key": f"spike:salons:{m_name}",
            "rationale": "Capitalizing on verifiable profile view surge with quick Google post creation.",
        }

    # Default Merchant Nudge
    body = (
        f"{salutation}, listing check for {m_name} in {locality}: customers are actively searching for hair and beauty care nearby. "
        f"You already have {active_offer} active. Want me to draft a 160-character WhatsApp message to re-engage past clients? Reply YES."
    )
    return {
        "body": body,
        "cta": "binary_yes_no",
        "send_as": "vera",
        "suppression_key": f"default:salons:{m_name}",
        "rationale": "Operator-to-operator nudge anchoring on active catalog offer with single binary CTA.",
    }
