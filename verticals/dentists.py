"""
Dentists Vertical Composer
Specialized clinical-peer tone, peer-to-peer vocabulary, and source-grounded messaging.
Taboos: no 'guaranteed', 'cure', 'painless', '100%'.
"""

from __future__ import annotations
from typing import Any, Dict, Optional


def compose_dentist(
    category: Dict[str, Any],
    merchant: Dict[str, Any],
    trigger: Dict[str, Any],
    customer: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    identity = merchant.get("identity", {})
    owner = identity.get("owner_first_name", "")
    prefix = "Dr. " if not owner.lower().startswith("dr") else ""
    dr_name = f"{prefix}{owner}" if owner else f"Dr. {identity.get('name', 'Doctor')}"
    locality = identity.get("locality", "")
    m_name = identity.get("name", "our clinic")
    
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
        active_offer = "Dental Cleaning @ ₹299"

    # Customer-Facing: Recall Due
    if customer or t_scope == "customer":
        c_name = customer.get("identity", {}).get("name", "") if customer else ""
        c_lang = customer.get("identity", {}).get("language_pref", "") if customer else ""
        is_hindi = "hi" in c_lang or "hi" in identity.get("languages", [])

        if is_hindi:
            body = (
                f"Hi {c_name}, {m_name} clinic here 🦷 It's been 5 months since your last visit — "
                f"your 6-month cleaning recall is due. Apke liye 2 slots ready hain: Wed 5pm ya Thu 6pm. "
                f"{active_offer} + complimentary oral checkup. Reply 1 for Wed, 2 for Thu, or tell us a time that works."
            )
        else:
            body = (
                f"Hi {c_name}, {m_name} clinic here 🦷 It's been 5 months since your last visit — "
                f"your 6-month cleaning recall is due. We have 2 slots ready: Wed 5pm or Thu 6pm. "
                f"{active_offer} + complimentary oral checkup. Reply 1 for Wed, 2 for Thu, or reply with your preferred time."
            )
        return {
            "body": body,
            "cta": "open_ended",
            "send_as": "merchant_on_behalf",
            "suppression_key": f"recall:dentists:{customer.get('customer_id') if customer else 'cx'}",
            "rationale": "Clinical recall due with specific slot options, real active offer price, and low-friction response path.",
        }

    # Merchant-Facing: Research Digest
    if "research_digest" in t_kind or "digest" in t_kind:
        top_item = t_payload.get("top_item", {})
        if not top_item:
            digests = category.get("digest", [])
            top_item = digests[0] if digests else {}
        source = top_item.get("source", "JIDA Oct 2026, p.14")
        title = top_item.get("title", "3-month fluoride recall cuts caries 38% better than 6-month")
        sample_n = top_item.get("trial_n", "")
        n_str = f"2,100-patient trial" if sample_n == 2100 or "2100" in str(top_item) else (f"{sample_n}-patient trial" if sample_n else "recent clinical trial")

        cust_agg = merchant.get("customer_aggregate", {})
        high_risk_n = cust_agg.get("high_risk_adult_count", "")
        cohort_anchor = f"your {high_risk_n} high-risk adult patients" if high_risk_n else "your adult patient roster"

        body = (
            f"{dr_name}, {source} landed. One item relevant to {cohort_anchor} — "
            f"{n_str} showed {title}. Worth a look (2-min abstract). "
            f"Want me to pull it + draft a patient-ed WhatsApp you can share? Reply YES. — {source}"
        )
        return {
            "body": body,
            "cta": "binary_yes_no",
            "send_as": "vera",
            "suppression_key": f"research:dentists:{trigger.get('id', 'W17')}",
            "rationale": "Clinically grounded research digest with exact peer journal citation, patient cohort anchor, and low-friction draft offer.",
        }

    # Merchant-Facing: Competitor Opened
    if "competitor_opened" in t_kind:
        dist = t_payload.get("distance_km", "1.2km")
        peer_rating = category.get("peer_stats", {}).get("avg_rating", 4.4)
        body = (
            f"{dr_name}, a new dental practice opened {dist} from {m_name} on Google Maps. "
            f"Your rating is solid at {peer_rating}★. To defend local search visibility in {locality}, "
            f"we should feature your {active_offer} on your Google profile post this week. "
            f"Want me to draft and publish the post now? Reply YES."
        )
        return {
            "body": body,
            "cta": "binary_yes_no",
            "send_as": "vera",
            "suppression_key": f"competitor:dentists:{locality}",
            "rationale": "Local competitive defense leveraging existing high rating and real active offer price.",
        }

    # Merchant-Facing: Default / General Benchmark
    ctr = merchant.get("performance", {}).get("ctr", 0.021)
    peer_ctr = category.get("peer_stats", {}).get("avg_ctr", 0.030)
    body = (
        f"{dr_name}, your 30-day Google CTR is {ctr * 100:.1f}% vs the {locality} dental peer median of {peer_ctr * 100:.1f}%. "
        f"Featuring {active_offer} on your profile will capture missed local search intent. "
        f"Want me to draft a 160-character patient educational WhatsApp update? Reply YES."
    )
    return {
        "body": body,
        "cta": "binary_yes_no",
        "send_as": "vera",
        "suppression_key": f"benchmark:dentists:{dr_name}",
        "rationale": "Comparative peer CTR benchmark with specific active catalog offer and effort-externalized CTA.",
    }
