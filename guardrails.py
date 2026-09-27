"""
magicpin AI Challenge — Guardrails & Policy Enforcement
Validates composed messages against vertical taboos, single-CTA rules, and anti-hallucination policies.
"""

from __future__ import annotations
import re
from typing import Any, Dict, List, Optional, Tuple

VERTICAL_TABOOS: Dict[str, List[str]] = {
    "dentists": ["guaranteed", "100% cure", "permanent cure", "painless", "cure your"],
    "pharmacies": ["miracle", "cure all", "guaranteed results", "100% safe"],
    "gyms": ["guaranteed weight loss", "melt fat", "lose 10kg in 10 days", "guarantee"],
    "salons": ["permanent fair", "100% whitening", "guaranteed"],
    "restaurants": ["best in the world", "guaranteed best"],
}


def check_taboos(body: str, category_slug: str) -> List[str]:
    """Check if the composed message violates any vertical voice taboos."""
    taboos = VERTICAL_TABOOS.get(category_slug, ["guaranteed"])
    body_lower = body.lower()
    violations = [t for t in taboos if t in body_lower]
    return violations


def clean_taboos(body: str, category_slug: str) -> str:
    """Sanitize any taboo phrases if present."""
    taboos = VERTICAL_TABOOS.get(category_slug, ["guaranteed"])
    cleaned = body
    for t in taboos:
        cleaned = re.sub(re.escape(t), "proven", cleaned, flags=re.IGNORECASE)
    return cleaned


def validate_cta_shape(body: str, cta: str) -> bool:
    """Validate that the message does not have buried or multiple conflicting CTAs."""
    # Check for multiple options like 'Reply YES for A, NO for B, MAYBE for C'
    multiple_branching = len(re.findall(r"reply\s+[a-z0-9]+\s+for", body, flags=re.IGNORECASE))
    if multiple_branching > 2:
        return False
    return True


def audit_provenance(body: str, contexts: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Audit numbers in the message to ensure they have grounding in provided contexts.
    Returns (is_clean, ungrounded_numbers).
    """
    found_nums = set(re.findall(r"\b\d+(?:[\.,]\d+)?%?\b", body))
    # Collect all numbers appearing in raw context strings
    ctx_str = str(contexts)
    grounded = set(re.findall(r"\b\d+(?:[\.,]\d+)?%?\b", ctx_str))
    
    # Common conversational quantities allowed
    allowed = {"1", "2", "3", "5", "10", "15", "30", "60", "24", "48", "90", "100", "2026", "24-48"}
    
    ungrounded = []
    for num in found_nums:
        clean_n = num.replace("%", "").replace(",", "")
        if clean_n not in allowed and num not in grounded and clean_n not in ctx_str:
            ungrounded.append(num)
            
    return len(ungrounded) == 0, ungrounded
