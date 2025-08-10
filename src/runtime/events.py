from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict


@dataclass(frozen=True)
class Event:
    type: str
    payload: Dict[str, Any]


class EventBus:
    """Simple in-process pub/sub used by the engine and WS bridge."""

    def __init__(self) -> None:
        self._subs: list[callable[[Event], None]] = []

    def subscribe(self, fn: callable[[Event], None]) -> None:
        self._subs.append(fn)

    def publish(self, evt: Event) -> None:
        for fn in list(self._subs):
            try:
                fn(evt)
            except Exception:
                # Keep bus resilient
                pass
