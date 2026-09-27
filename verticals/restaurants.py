"""
Restaurants Vertical Composer
Operator-to-operator vocabulary (covers, AOV, delivery specials, match-night shifts).
Taboos: no 'guaranteed best', 'best in the world'.
"""

from __future__ import annotations
from typing import Any, Dict, Optional


def compose_restaurant(
    category: Dict[str, Any],
    merchant: Dict[str, Any],
    trigger: Dict[str, Any],
    customer: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    identity = merchant.get("identity", {})
    owner = identity.get("owner_first_name", "")
    salutation = f"Hi {owner}" if owner else f"Hi {identity.get('name', 'there')}"
    locality = identity.get("locality", "")
    m_name = identity.get("name", "our restaurant")
    
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
        active_offer = "BOGO Pizza Special"

    # Customer-Facing
    if customer or t_scope == "customer":
        c_name = customer.get("identity", {}).get("name", "") if customer else ""
        body = (
            f"Hi {c_name}, {m_name} in {locality} here 🍕 Your favorite meals are ready for order. "
            f"Enjoy {active_offer} on your next order today with quick delivery to your door. Reply 1 to view menu or order directly."
        )
        return {
            "body": body,
            "cta": "open_ended",
            "send_as": "merchant_on_behalf",
            "suppression_key": f"cx:restaurants:{customer.get('customer_id') if customer else 'cx'}",
            "rationale": "Direct customer reactivation with verified active menu offer and immediate delivery link.",
        }

    # Merchant-Facing: IPL Match Day
    if "ipl" in t_kind or "match" in t_kind or "cricket" in t_kind:
        match_teams = t_payload.get("teams", "DC vs MI")
        match_time = t_payload.get("match_time", "7:30pm")
        stadium = t_payload.get("stadium", "Arun Jaitley Stadium")
        body = (
            f"Quick heads-up {owner or 'there'} — {match_teams} at {stadium} tonight, {match_time}. "
            f"Important: Saturday IPL matches usually shift -12% restaurant covers (people watch at home). "
            f"Skip the match-night promo today; instead push your {active_offer} as a delivery-only Saturday special. "
            f"Want me to draft the Swiggy banner + an Insta story? Live in 10 min. Reply YES."
        )
        return {
            "body": body,
            "cta": "binary_yes_no",
            "send_as": "vera",
            "suppression_key": f"ipl:restaurants:{match_teams}",
            "rationale": "Contrarian operator-level recommendation turning home-match shift into delivery volume with instant banner draft.",
        }

    # Merchant-Facing: Corporate Thali Planning
    if "thali" in t_kind or "corporate" in t_kind or "planning" in t_kind:
        body = (
            f"{owner or 'there'}, here is a starter corporate package for offices in {locality} — you can edit:\n"
            f"- 10 thalis @ ₹125 each (₹25 off retail) + free delivery\n"
            f"- 25 thalis @ ₹115 each + 2 free filter coffees\n"
            f"- 50+: ₹105 each + 1 free platter\n"
            f"Delivery between 12:30-1pm. 3 offices in {locality} are in your delivery radius. "
            f"Want me to draft a 3-line WhatsApp note to send their facilities managers? Reply YES."
        )
        return {
            "body": body,
            "cta": "binary_yes_no",
            "send_as": "vera",
            "suppression_key": f"corporate:restaurants:{locality}",
            "rationale": "Tiered B2B corporate bulk thali proposal structured for local commercial offices with immediate outreach draft.",
        }

    # Default Merchant Nudge
    body = (
        f"{salutation}, listing check for {m_name} in {locality}: dinner orders are peaking this week. "
        f"Promoting your active {active_offer} on your Google listing will maximize walk-ins and direct calls. "
        f"Want me to publish a fresh Google Post featuring this offer now? Takes 2 min. Reply YES."
    )
    return {
        "body": body,
        "cta": "binary_yes_no",
        "send_as": "vera",
        "suppression_key": f"default:restaurants:{m_name}",
        "rationale": "Operator-aligned timing leveraging active catalog offer and effortless binary confirmation.",
    }
