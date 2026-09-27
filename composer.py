"""
magicpin AI Challenge — Message Composer
Modular dispatcher routing to vertical-specialized composition engines:
- Dentists
- Salons
- Restaurants
- Gyms
- Pharmacies
Enforces guardrails against vertical taboos and multiple CTAs.
"""

from __future__ import annotations
from typing import Any, Dict, Optional

from verticals.dentists import compose_dentist
from verticals.salons import compose_salon
from verticals.restaurants import compose_restaurant
from verticals.gyms import compose_gym
from verticals.pharmacies import compose_pharmacy
from guardrails import clean_taboos, validate_cta_shape


DISPATCHER = {
    "dentists": compose_dentist,
    "salons": compose_salon,
    "restaurants": compose_restaurant,
    "gyms": compose_gym,
    "pharmacies": compose_pharmacy,
}


def compose(
    category: Dict[str, Any],
    merchant: Dict[str, Any],
    trigger: Dict[str, Any],
    customer: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Compose high-compulsion message from 4 context layers.
    Routes to domain-specialized engines and passes through policy guardrails.
    """
    cat_slug = category.get("slug") or merchant.get("category_slug") or "generic"
    composer_fn = DISPATCHER.get(cat_slug, compose_dentist)

    composed = composer_fn(
        category=category,
        merchant=merchant,
        trigger=trigger,
        customer=customer,
    )

    # Apply policy guardrails: clean any taboo phrases
    body = clean_taboos(composed.get("body", ""), cat_slug)
    cta = composed.get("cta", "binary_yes_no")

    # Validate CTA shape
    if not validate_cta_shape(body, cta):
        cta = "binary_yes_no"

    composed["body"] = body
    composed["cta"] = cta
    return composed
