from __future__ import annotations

from typing import Any, Dict, Optional


class Blackboard:
    """Shared key-value store."""

    def __init__(self) -> None:
        self._data: Dict[str, Any] = {}

    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self._data[key] = value

    def as_dict(self) -> Dict[str, Any]:
        return dict(self._data)
