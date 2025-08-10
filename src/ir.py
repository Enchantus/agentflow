from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

IR_VERSION = "0.1.0"


def new_ir() -> Dict[str, Any]:
    return {
        "version": IR_VERSION,
        "meta": {"id": "untitled"},
        "graph": {"nodes": [], "edges": {"exec": [], "data": []}},
    }


def load_ir(path: str | Path) -> Dict[str, Any]:
    p = Path(path)
    data = json.loads(p.read_text(encoding="utf-8"))
    if "graph" not in data or not isinstance(data["graph"], dict):
        raise ValueError("Invalid IR: missing 'graph' object.")
    data.setdefault("version", IR_VERSION)
    g = data["graph"]
    g.setdefault("nodes", [])
    g.setdefault("edges", {})
    g["edges"].setdefault("exec", [])
    g["edges"].setdefault("data", [])
    return data


def save_ir(ir: Dict[str, Any], path: str | Path) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(ir, indent=2), encoding="utf-8")


def add_node(ir: Dict[str, Any], node_id: str, kind: str) -> None:
    nodes = ir["graph"]["nodes"]
    if any(n.get("id") == node_id for n in nodes):
        raise ValueError(f"Node id already exists: {node_id}")
    nodes.append({"id": node_id, "kind": kind, "inputs": {}, "outputs": {}})


def remove_node(ir: Dict[str, Any], node_id: str) -> None:
    g = ir["graph"]
    g["nodes"] = [n for n in g["nodes"] if n.get("id") != node_id]
    g["edges"]["exec"] = [
        e for e in g["edges"]["exec"]
        if e.get("from", [None])[0] != node_id and e.get("to", [None])[0] != node_id
    ]
    g["edges"]["data"] = [
        e for e in g["edges"]["data"]
        if e.get("from", [None])[0] != node_id and e.get("to", [None])[0] != node_id
    ]


def add_exec_edge(ir: Dict[str, Any], src_node: str, dst_node: str) -> None:
    ir["graph"]["edges"]["exec"].append(
        {"from": [src_node, "out"], "to": [dst_node, "exec"]}
    )


def add_data_edge(
    ir: Dict[str, Any], src_node: str, src_port: str, dst_node: str, dst_port: str
) -> None:
    ir["graph"]["edges"]["data"].append(
        {"from": [src_node, src_port], "to": [dst_node, dst_port]}
    )


def describe(ir: Dict[str, Any]) -> str:
    g = ir["graph"]
    nodes = g["nodes"]
    exec_edges = g["edges"]["exec"]
    data_edges = g["edges"]["data"]
    return (
        f"IR Version: {ir.get('version')}\n"
        f"Nodes ({len(nodes)}): {[n['id'] for n in nodes]}\n"
        f"Exec edges: {len(exec_edges)}\n"
        f"Data edges: {len(data_edges)}"
    )
