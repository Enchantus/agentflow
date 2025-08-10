from __future__ import annotations

from typing import Any, Mapping

from src.core.node import Node, NodeContext
from src.core.registry import register_node


@register_node
class AFConst(Node):
    TYPE_NAME = "AgentFlow/Const"
    OUTPUTS = {"out": "any"}
    PARAMS = {"value": "any"}

    def run(self, ctx: NodeContext, inputs: Mapping[str, Any], params: Mapping[str, Any]):
        return {"out": params.get("value")}


@register_node
class AFConcat(Node):
    TYPE_NAME = "AgentFlow/Concat"
    INPUTS = {"a": "string", "b": "string"}
    OUTPUTS = {"out": "string"}

    def run(self, ctx: NodeContext, inputs: Mapping[str, Any], params: Mapping[str, Any]):
        a = str(inputs.get("a", ""))
        b = str(inputs.get("b", ""))
        return {"out": a + b}


@register_node
class AFBranch(Node):
    TYPE_NAME = "AgentFlow/Branch"
    INPUTS = {"value": "any"}
    PARAMS = {"bb_key": "string", "equals": "any"}
    OUTPUTS = {"out": "any"}  # pass-through

    def run(self, ctx: NodeContext, inputs: Mapping[str, Any], params: Mapping[str, Any]):
        key = str(params.get("bb_key", ""))
        equals = params.get("equals")
        ctx.blackboard.set(key, inputs.get("value"))
        # Simple comparison side-effect for demo
        ctx.blackboard.set(f"{key}__match", inputs.get("value") == equals)
        return {"out": inputs.get("value")}
