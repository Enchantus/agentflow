from __future__ import annotations

from typing import Dict, Iterable, Type
from .node import Node


class NodeRegistry:
    """Global pluggable node registry."""

    def __init__(self) -> None:
        self._types: Dict[str, Type[Node]] = {}

    def register(self, cls: Type[Node]) -> None:
        self._types[cls.TYPE_NAME] = cls

    def get(self, type_name: str) -> Type[Node]:
        if type_name not in self._types:
            raise KeyError(f"Unknown node type: {type_name}")
        return self._types[type_name]

    def list_types(self) -> Iterable[str]:
        return sorted(self._types.keys())


REGISTRY = NodeRegistry()


def register_node(cls: Type[Node]) -> Type[Node]:
    REGISTRY.register(cls)
    return cls
