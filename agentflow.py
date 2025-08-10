from __future__ import annotations

import argparse
import pathlib
import socket
import sys
import uvicorn

# Ensure ./src is importable
_REPO_ROOT = pathlib.Path(__file__).resolve().parent
_SRC = _REPO_ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from server.app import create_app  # noqa: E402


def _port_is_free(host: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.2)
        return s.connect_ex((host, port)) != 0


def _pick_port(host: str, preferred: int, max_tries: int = 15) -> int:
    port = preferred
    for _ in range(max_tries):
        if _port_is_free(host, port):
            return port
        port += 1
    raise RuntimeError(f"No free port near {preferred} (tried {max_tries} ports).")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="AgentFlow — Agentic AI Node Graph Runtime")
    parser.add_argument("--serve", action="store_true", help="Run HTTP server (default).")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8080)
    args = parser.parse_args(argv)

    app = create_app()
    port = _pick_port(args.host, args.port)
    print(f"Serving AgentFlow on http://{args.host}:{port}")
    uvicorn.run(app, host=args.host, port=port, log_level="info")


if __name__ == "__main__":
    main()
