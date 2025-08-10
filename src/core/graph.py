from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Literal, Optional, Tuple, TypedDict


PortDirection = Literal["in", "out"]


class NodeInstance(TypedDict, total=False):
    id: str
    type: str
    params: Dict[str, Any]        # constant params (like Shader Graph node inspector)
    inputs: Dict[str, Any]        # default input values (used if no incoming data edge)
    position: Tuple[float, float] # editor hint only


class DataEdge(TypedDict):
    src: Tuple[str, str]  # (node_id, port)
    dst: Tuple[str, str]  # (node_id, port)


class ExecEdge(TypedDict):
    src: str              # src node id (implicit 'out')
    dst: str              # dst node id (implicit 'exec')


class GraphModel(TypedDict):
    version: str
    meta: Dict[str, Any]
    nodes: List[NodeInstance]
    edges: Dict[str, List[Any]]   # {"data": List[DataEdge], "exec": List[ExecEdge]}


IR_VERSION = "0.2.0"


def new_graph() -> GraphModel:
    return {
        "version": IR_VERSION,
        "meta": {"id": "untitled"},
        "nodes": [],
        "edges": {"data": [], "exec": []},
    }


@dataclass(frozen=True)
class CompiledGraph:
    model: GraphModel
    fanin: Dict[str, List[DataEdge]] = field(default_factory=dict)
    fanout: Dict[str, List[DataEdge]] = field(default_factory=dict)
    exec_next: Dict[str, List[str]] = field(default_factory=dict)
    exec_prev_count: Dict[str, int] = field(default_factory=dict)

    @staticmethod
    def compile(model: GraphModel) -> "CompiledGraph":
        fanin: Dict[str, List[DataEdge]] = {}
        fanout: Dict[str, List[DataEdge]] = {}
        exec_next: Dict[str, List[str]] = {}
        exec_prev_count: Dict[str, int] = {}

        for e in model["edges"]["data"]:
            fanin.setdefault(e["dst"][0], []).append(e)
            fanout.setdefault(e["src"][0], []).append(e)

        for e in model["edges"]["exec"]:
            exec_next.setdefault(e["src"], []).append(e["dst"])
            exec_prev_count[e["dst"]] = exec_prev_count.get(e["dst"], 0) + 1
            exec_prev_count.setdefault(e["src"], exec_prev_count.get(e["src"], 0))

        return CompiledGraph(
            model=model,
            fanin=fanin,
            fanout=fanout,
            exec_next=exec_next,
            exec_prev_count=exec_prev_count,
        )
