from __future__ import annotations

from typing import Any, Dict, List, Tuple

from pydantic import BaseModel, Field


class DataEdge(BaseModel):
    src: Tuple[str, str]  # (node_id, port)
    dst: Tuple[str, str]


class ExecEdge(BaseModel):
    src: str
    dst: str


class NodeInstance(BaseModel):
    id: str
    type: str
    params: Dict[str, Any] = Field(default_factory=dict)
    inputs: Dict[str, Any] = Field(default_factory=dict)
    position: Tuple[float, float] | None = None


class GraphEdges(BaseModel):
    data: List[DataEdge] = Field(default_factory=list)
    exec: List[ExecEdge] = Field(default_factory=list)


class GraphModel(BaseModel):
    version: str = "0.2.0"
    meta: Dict[str, Any] = Field(default_factory=dict)
    nodes: List[NodeInstance] = Field(default_factory=list)
    edges: GraphEdges = Field(default_factory=GraphEdges)
