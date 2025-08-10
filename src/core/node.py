from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Mapping, Optional, Tuple


@dataclass
class NodeContext:
    """Execution context handed to every node."""
    run_id: str
    node_id: str
    services: "ServiceContainer"
    blackboard: "Blackboard"


class Node:
    """Abstract executable node."""

    TYPE_NAME: str = "Base/Node"
    INPUTS: Mapping[str, str] = {}   # port -> type name
    OUTPUTS: Mapping[str, str] = {}
    PARAMS: Mapping[str, str] = {}

    def run(
        self,
        ctx: NodeContext,
        inputs: Mapping[str, Any],
        params: Mapping[str, Any],
    ) -> Mapping[str, Any]:
        """Execute node and return output dict."""
        raise NotImplementedError
