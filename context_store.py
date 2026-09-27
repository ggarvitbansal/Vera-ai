"""
magicpin AI Challenge — Context Store
Thread-safe, in-memory storage for the 4-context framework:
- category
- merchant
- customer
- trigger
Enforces idempotency, atomic version updates, and stale version conflict detection (HTTP 409).
"""

from __future__ import annotations
import threading
from typing import Any, Dict, Optional, Tuple
from datetime import datetime


class ContextStore:
    def __init__(self) -> None:
        self._lock = threading.RLock()
        # Storage format: (scope, context_id) -> {"version": int, "payload": dict, "stored_at": str}
        self._store: Dict[Tuple[str, str], Dict[str, Any]] = {}

    def push(
        self, scope: str, context_id: str, version: int, payload: Dict[str, Any]
    ) -> Tuple[bool, Optional[str], Optional[int]]:
        """
        Store or update a context object atomically.
        Returns:
            (accepted: bool, error_reason: str | None, current_version: int | None)
        """
        key = (scope, context_id)
        with self._lock:
            existing = self._store.get(key)
            if existing is not None:
                current_ver = existing["version"]
                if current_ver > version:
                    return False, "stale_version", current_ver
                elif current_ver == version:
                    # Idempotent no-op
                    return True, None, current_ver

            self._store[key] = {
                "version": version,
                "payload": payload,
                "stored_at": datetime.utcnow().isoformat() + "Z",
            }
            return True, None, version

    def get(self, scope: str, context_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve payload for a given (scope, context_id)."""
        key = (scope, context_id)
        with self._lock:
            entry = self._store.get(key)
            return entry["payload"] if entry else None

    def get_version(self, scope: str, context_id: str) -> Optional[int]:
        """Retrieve version number for a given (scope, context_id)."""
        key = (scope, context_id)
        with self._lock:
            entry = self._store.get(key)
            return entry["version"] if entry else None

    def get_all(self, scope: str) -> Dict[str, Dict[str, Any]]:
        """Retrieve all context payloads for a given scope."""
        with self._lock:
            return {
                cid: entry["payload"]
                for (s, cid), entry in self._store.items()
                if s == scope
            }

    def counts(self) -> Dict[str, int]:
        """Return counts of loaded contexts by scope."""
        counts = {"category": 0, "merchant": 0, "customer": 0, "trigger": 0}
        with self._lock:
            for (scope, _), _ in self._store.items():
                counts[scope] = counts.get(scope, 0) + 1
        return counts

    def clear(self) -> None:
        """Clear all stored contexts."""
        with self._lock:
            self._store.clear()


# Global singleton instance
store = ContextStore()
