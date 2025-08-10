from __future__ import annotations

import uuid
from typing import Any, Dict, List, Mapping

from core.blackboard import Blackboard
from runtime.events import Event, EventBus
from runtime.services import ServiceContainer
from core.registry import REGISTRY
from server.schemas import GraphModel, DataEdge, ExecEdge


class Engine:
    def __init__(self, services: ServiceContainer, bus: EventBus) -> None:
        self._services = services
        self._bus = bus

    def run(self, graph: GraphModel, *, inputs: Dict[str, Any] | None = None) -> Dict[str, Any]:
        run_id = str(uuid.uuid4())
        bb = Blackboard()
        if inputs:
            for k, v in inputs.items():
                bb.set(k, v)

        self._bus.publish(Event("GraphStarted", {"run_id": run_id, "meta": graph.meta}))

        # Compile adjacency once
        fanin: Dict[str, List[DataEdge]] = {}
        exec_next: Dict[str, List[str]] = {}
        exec_prev_count: Dict[str, int] = {}

        for e in graph.edges.data:
            fanin.setdefault(e.dst[0], []).append(e)

        for e in graph.edges.exec:
            exec_next.setdefault(e.src, []).append(e.dst)
            exec_prev_count[e.dst] = exec_prev_count.get(e.dst, 0) + 1
            exec_prev_count.setdefault(e.src, exec_prev_count.get(e.src, 0))

        node_map = {n.id: n for n in graph.nodes}
        ready_exec = [n.id for n in graph.nodes if exec_prev_count.get(n.id, 0) == 0]
        visited: set[str] = set()
        last_outputs: Dict[str, Dict[str, Any]] = {}

        def prev_exec_nodes(node_id: str) -> List[str]:
            return [src for src, ns in exec_next.items() if node_id in ns]

        while ready_exec:
            nid = ready_exec.pop(0)
            node = node_map[nid]

            data_inputs: Dict[str, Any] = dict(node.inputs)
            for e in fanin.get(nid, []):
                src_id, src_port = e.src
                if src_id in last_outputs and src_port in last_outputs[src_id]:
                    data_inputs[e.dst[1]] = last_outputs[src_id][src_port]

            from core.node import NodeContext  # local import to avoid cycles
            ctx = NodeContext(run_id=run_id, node_id=nid, services=self._services, blackboard=bb)

            self._bus.publish(Event("NodeStarted", {"run_id": run_id, "node_id": nid, "type": node.type}))
            node_cls = REGISTRY.get(node.type)
            out = node_cls().run(ctx, data_inputs, node.params)
            last_outputs[nid] = dict(out)
            self._bus.publish(Event("NodeFinished", {"run_id": run_id, "node_id": nid, "outputs": out}))

            visited.add(nid)
            for nxt in exec_next.get(nid, []):
                if all(prev in visited for prev in prev_exec_nodes(nxt)):
                    ready_exec.append(nxt)

        self._bus.publish(Event("GraphFinished", {"run_id": run_id, "blackboard": bb.as_dict()}))
        return {"run_id": run_id, "blackboard": bb.as_dict(), "last_outputs": last_outputs}
