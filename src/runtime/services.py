from __future__ import annotations

from typing import Any, Dict


class ServiceContainer:
    """Very small DI container."""

    def __init__(self) -> None:
        self._services: Dict[str, Any] = {}

    def add(self, name: str, service: Any) -> None:
        self._services[name] = service

    def get(self, name: str) -> Any:
        if name not in self._services:
            raise KeyError(f"Service not found: {name}")
        return self._services[name]
