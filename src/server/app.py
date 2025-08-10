from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles

from core.blackboard import Blackboard
from core.registry import REGISTRY
from runtime.events import Event, EventBus
from runtime.services import ServiceContainer
from server.schemas import GraphModel

# single in-memory graph for MVP
_GRAPH = GraphModel()
_SERVICES = ServiceContainer()
_BUS = EventBus()
_ENGINE = Engine(_SERVICES, _BUS)


def create_app() -> FastAPI:
    app = FastAPI(title="AgentFlow Runtime", version="0.1.0")

    static_dir = Path(__file__).parent / "static"
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

    @app.get("/", response_class=HTMLResponse)
    async def index() -> Any:
        return FileResponse(static_dir / "index.html")

    @app.get("/api/nodes")
    async def list_nodes() -> Dict[str, Any]:
        items = []
        for t in REGISTRY.list_types():
            cls = REGISTRY.get(t)
            items.append(
                {
                    "type": t,
                    "inputs": getattr(cls, "INPUTS", {}),
                    "outputs": getattr(cls, "OUTPUTS", {}),
                    "params": getattr(cls, "PARAMS", {}),
                }
            )
        return {"nodes": items}

    @app.get("/api/graph", response_model=GraphModel)
    async def get_graph() -> GraphModel:
        return _GRAPH

    @app.put("/api/graph", response_model=dict)
    async def put_graph(graph: GraphModel) -> Dict[str, Any]:
        global _GRAPH
        _GRAPH = graph
        return {"ok": True, "version": graph.version}

    @app.post("/api/run", response_model=dict)
    async def run_graph(payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
        inputs = (payload or {}).get("inputs", {})
        result = _ENGINE.run(_GRAPH, inputs=inputs)
        return {"ok": True, **result}

    @app.websocket("/ws/events")
    async def ws_events(ws: WebSocket) -> None:
        await ws.accept()

        def forward(evt):
            try:
                import json
                ws._loop.create_task(ws.send_text(json.dumps({"type": evt.type, "payload": evt.payload})))  # type: ignore[attr-defined]
            except Exception:
                pass

        _BUS.subscribe(forward)
        try:
            while True:
                await ws.receive_text()
        except WebSocketDisconnect:
            pass

    return app
