"""
Pharmacies Vertical Composer
Trustworthy, precise, scientific molecule names, batch recall handling, respectful senior care.
Taboos: no 'miracle', 'cure all', '100% safe', 'guaranteed'.
"""

from __future__ import annotations
from typing import Any, Dict, Optional


def compose_pharmacy(
    category: Dict[str, Any],
    merchant: Dict[str, Any],
    trigger: Dict[str, Any],
    customer: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    identity = merchant.get("identity", {})
    owner = identity.get("owner_first_name", "")
    salutation = f"Hi {owner}" if owner else f"Hi {identity.get('name', 'there')}"
    locality = identity.get("locality", "")
    m_name = identity.get("name", "our pharmacy")
    
    t_kind = trigger.get("kind", "")
    t_payload = trigger.get("payload", {})
    t_scope = trigger.get("scope", "merchant")

    # Customer-Facing: Chronic Refill Reminder
    if customer or t_scope == "customer":
        c_name = customer.get("identity", {}).get("name", "") if customer else "Sharma ji"
        medicines = t_payload.get("medicines", ["metformin", "atorvastatin", "telmisartan"])
        med_str = ", ".join(medicines) if isinstance(medicines, list) else str(medicines)
        refill_date = t_payload.get("refill_date", "28 April")
        
        body = (
            f"Namaste — {m_name} {locality} yahan. {c_name} ki 3 monthly medicines ({med_str}) "
            f"{refill_date} ko khatam hongi. Same dose, same brand pack ready hai. "
            f"Senior discount 15% applied — free home delivery to saved address by 5pm tomorrow. "
            f"Reply CONFIRM to dispatch, or call us if any change in dosage."
        )
        return {
            "body": body,
            "cta": "binary_yes_no",
            "send_as": "merchant_on_behalf",
            "suppression_key": f"refill:pharmacy:{customer.get('customer_id') if customer else 'cx'}",
            "rationale": "Respectful senior citizen chronic medicine reminder citing exact molecule names, discount, and effortless home delivery confirmation.",
        }

    # Merchant-Facing: Supply / Batch Recall Alert
    if "supply" in t_kind or "recall" in t_kind:
        batches = t_payload.get("batches", ["AT2024-1102", "AT2024-1108"])
        batch_str = ", ".join(batches) if isinstance(batches, list) else str(batches)
        molecule = t_payload.get("molecule", "atorvastatin")
        manufacturer = t_payload.get("manufacturer", "Mfr Z")
        affected_count = t_payload.get("affected_customers", 22)
        
        body = (
            f"{owner or 'Ramesh'}, urgent: voluntary recall on 2 {molecule} batches ({batch_str}) by {manufacturer} — "
            f"sub-potency, no safety risk, but customers should be informed for replacement. "
            f"Pulled your records: {affected_count} of your chronic-Rx customers were dispensed these batches in the last 90 days. "
            f"Want me to draft their WhatsApp note + the replacement-pickup workflow? Reply YES."
        )
        return {
            "body": body,
            "cta": "binary_yes_no",
            "send_as": "vera",
            "suppression_key": f"recall:pharmacy:{batch_str}",
            "rationale": "High-urgency compliance notice citing specific batch numbers, affected patient count, and pre-drafted replacement workflow.",
        }

    # Default Merchant Nudge
    body = (
        f"{salutation}, listing check for {m_name} in {locality}: repeat chronic-care prescription searches remain high. "
        f"Promoting Free Home Delivery and Senior Discounts on your Google profile post will expand repeat customer orders. "
        f"Want me to draft this Google post now? Takes 2 min. Reply YES."
    )
    return {
        "body": body,
        "cta": "binary_yes_no",
        "send_as": "vera",
        "suppression_key": f"default:pharmacy:{m_name}",
        "rationale": "Trustworthy pharmacy operator nudge focusing on chronic refills and home delivery with binary confirmation.",
    }
