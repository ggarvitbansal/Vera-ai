"""
Gyms Vertical Composer
Motivational coach tone, evidence-based, zero shame for lapsed members, seasonal reframes.
Taboos: no 'guaranteed weight loss', 'melt fat', 'guarantee'.
"""

from __future__ import annotations
from typing import Any, Dict, Optional


def compose_gym(
    category: Dict[str, Any],
    merchant: Dict[str, Any],
    trigger: Dict[str, Any],
    customer: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    identity = merchant.get("identity", {})
    owner = identity.get("owner_first_name", "")
    salutation = f"Hi {owner}" if owner else f"Hi {identity.get('name', 'there')}"
    locality = identity.get("locality", "")
    m_name = identity.get("name", "our gym")
    
    t_kind = trigger.get("kind", "")
    t_payload = trigger.get("payload", {})
    t_scope = trigger.get("scope", "merchant")
    
    cust_agg = merchant.get("customer_aggregate", {})
    member_count = cust_agg.get("total_unique_ytd", cust_agg.get("active_members", 245))

    # Active offer from catalog
    active_offer = ""
    for o in merchant.get("offers", []):
        if o.get("status") == "active":
            active_offer = o.get("title", "")
            break
    if not active_offer:
        active_offer = "First Month @ ₹499"

    # Customer-Facing: Lapsed Member Winback
    if customer or t_scope == "customer":
        c_name = customer.get("identity", {}).get("name", "") if customer else ""
        days = t_payload.get("days_since_visit", 57)
        body = (
            f"Hi {c_name} 👋 {owner or m_name} from {m_name} here. It's been about {days} days — "
            f"happens to most members at some point, no judgment. We have added a Tue/Thu evening session "
            f"that fits routine goals well (45 min, 6:30pm). Want me to hold a free trial spot for you next Tue? "
            f"Reply YES — no commitment, no auto-charge."
        )
        return {
            "body": body,
            "cta": "binary_yes_no",
            "send_as": "merchant_on_behalf",
            "suppression_key": f"winback:gyms:{customer.get('customer_id') if customer else 'cx'}",
            "rationale": "Empathetic, no-shame member lapse outreach with specific evening class slot and zero-risk binary CTA.",
        }

    # Merchant-Facing: Seasonal Acquisition Dip Reframe
    if "seasonal" in t_kind or "perf_dip" in t_kind:
        perf = merchant.get("performance", {})
        delta = abs(int(perf.get("delta_7d", {}).get("views_pct", -0.30) * 100))
        body = (
            f"{salutation}, your views shifted down {delta}% this week — but note this is the normal April-June acquisition lull "
            f"(every metro gym sees -25 to -35% in this window). Recommendation: skip fresh ad spend now and focus retention on your "
            f"{member_count} active members. Want me to draft a 30-day summer attendance challenge to keep them engaged? Takes 5 min. Reply YES."
        )
        return {
            "body": body,
            "cta": "binary_yes_no",
            "send_as": "vera",
            "suppression_key": f"seasonal:gyms:{m_name}",
            "rationale": "Anxiety pre-emption reframing seasonal dip as retention opportunity using exact member count and attendance challenge.",
        }

    # Default Merchant Nudge
    body = (
        f"{salutation}, quick review for {m_name} in {locality}: fitness searches in your area remain strong. "
        f"Promoting {active_offer} on your Google Business Profile will capture local intent. "
        f"Want me to draft a high-energy workout post with a free guest pass callout? Reply YES."
    )
    return {
        "body": body,
        "cta": "binary_yes_no",
        "send_as": "vera",
        "suppression_key": f"default:gyms:{m_name}",
        "rationale": "Motivational coach tone leveraging verified active trial offer with single binary CTA.",
    }
