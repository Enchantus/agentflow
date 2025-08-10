from __future__ import annotations

import shlex
from typing import Any, Dict

from .ir import (
    new_ir,
    save_ir,
    load_ir,
    add_node,
    add_exec_edge,
    add_data_edge,
    remove_node,
    describe,
)

BANNER = (
    "AgentFlow Builder — type 'help' for commands. "
    "Build a flow, then 'save <path>' to write an IR JSON."
)


class FlowBuilder:
    def __init__(self, ir: Dict[str, Any] | None = None) -> None:
        self.ir: Dict[str, Any] = ir or new_ir()

    def cmdloop(self) -> None:
        print(BANNER)
        while True:
            try:
                line = input("agentflow> ").strip()
            except (EOFError, KeyboardInterrupt):
                print()
                break
            if not line:
                continue
            if line.lower() in {"quit", "exit"}:
                break
            self.handle(line)

    def handle(self, line: str) -> None:
        parts = shlex.split(line)
        cmd = parts[0].lower()
        args = parts[1:]

        try:
            if cmd in {"help", "h", "?"}:
                self.cmd_help()
            elif cmd == "show":
                self.cmd_show()
            elif cmd == "new":
                self.ir = new_ir()
                print("Started a new empty flow.")
            elif cmd == "load":
                self._require(len(args) == 1, "Usage: load <path>")
                self.ir = load_ir(args[0])
                print(f"Loaded IR from {args[0]}")
            elif cmd == "save":
                self._require(len(args) == 1, "Usage: save <path>")
                save_ir(self.ir, args[0])
                print(f"Saved IR to {args[0]}")
            elif cmd == "add":
                self._require(args, "Usage: add <node|exec|data> ...")
                sub = args[0].lower()
                if sub == "node":
                    self._require(len(args) == 3, "Usage: add node <id> <kind>")
                    add_node(self.ir, args[1], args[2])
                    print(f"Added node {args[1]} ({args[2]})")
                elif sub == "exec":
                    self._require(len(args) == 3, "Usage: add exec <from_node> <to_node>")
                    add_exec_edge(self.ir, args[1], args[2])
                    print(f"Added exec edge: {args[1]} -> {args[2]}")
                elif sub == "data":
                    self._require(len(args) == 5, "Usage: add data <from_node> <from_port> <to_node> <to_port>")
                    add_data_edge(self.ir, args[1], args[2], args[3], args[4])
                    print(f"Added data edge: {args[1]}:{args[2]} -> {args[3]}:{args[4]}")
                else:
                    print("Unknown 'add' subtype. Use: node | exec | data")
            elif cmd == "remove":
                self._require(len(args) == 2 and args[0] == "node", "Usage: remove node <id>")
                remove_node(self.ir, args[1])
                print(f"Removed node {args[1]} (and connected edges)")
            elif cmd == "list":
                self._require(args, "Usage: list <nodes|edges>")
                sub = args[0].lower()
                g = self.ir["graph"]
                if sub == "nodes":
                    for n in g["nodes"]:
                        print(f"- {n['id']} ({n.get('kind')})")
                elif sub == "edges":
                    for e in g["edges"]["exec"]:
                        print(f"- exec: {e['from'][0]} -> {e['to'][0]}")
                    for e in g["edges"]["data"]:
                        print(f"- data: {e['from'][0]}:{e['from'][1]} -> {e['to'][0]}:{e['to'][1]}")
                else:
                    print("Unknown list target. Use: nodes | edges")
            else:
                print("Unknown command. Type 'help' for assistance.")
        except Exception as exc:
            print(f"Error: {exc}")

    def cmd_show(self) -> None:
        print(describe(self.ir))

    @staticmethod
    def _require(condition: bool, msg: str) -> None:
        if not condition:
            raise ValueError(msg)

    @staticmethod
    def cmd_help() -> None:
        print(
            """Commands:
  help                        Show this help
  show                        Print a summary of the current flow
  new                         Start a new empty flow
  load <path>                 Load an IR from JSON
  save <path>                 Save the current flow to JSON
  add node <id> <kind>        Add a node
  add exec <from> <to>        Add an execution edge
  add data <from> <fp> <to> <tp>  Add a data edge (ports)
  remove node <id>            Remove a node (and its edges)
  list nodes|edges            List nodes or edges
  quit / exit                 Leave the builder
"""
        )
