# AgentFlow

**AgentFlow** is a Python-based visual workflow and execution framework for designing, connecting, and generating **agent-based systems**.  
It combines the clarity of a **node-driven interface** with the flexibility of modern AI orchestration, allowing you to **design agent logic visually** and export executable code for multiple back-end runtimes, such as [Mastra](https://github.com/mastra-ai/mastra), [LangGraph](https://github.com/langchain-ai/langgraph), or your own custom frameworks.

---

## ✨ Mission & Vision

AgentFlow’s mission is to **bridge the gap between agent design and implementation**.  
We believe that building agentic AI systems should feel as intuitive as designing a game level — with **clear visual logic**, **typed connections**, and a **separation of design from code**.

Inspired by the **nodegraph** and **blackboard** paradigms from game engines like Unity and Unreal Engine, AgentFlow provides:
- A **visual workspace** where each node represents a distinct operation, decision, or communication between agents.
- **Typed inputs and outputs** that enforce consistency and compatibility between nodes.
- A **schema-driven approach** to data flow, ensuring that agent workflows are reliable, maintainable, and easy to extend.

---

## 🎯 Purpose

The purpose of AgentFlow is to give developers, researchers, and AI enthusiasts a **visual-first tool** to:
1. **Design** agent logic and workflows without diving immediately into code.
2. **Prototype quickly** by dragging, connecting, and configuring nodes that represent agent actions, decisions, or data transformations.
3. **Generate executable code** targeting your chosen runtime — whether that’s an existing orchestration library or a custom system.
4. **Iterate rapidly** with a clear separation between **design-time logic** and **runtime execution**.

With AgentFlow, you can:
- Map out **multi-agent collaborations** visually.
- Define **input/output schemas** for agents to ensure data integrity.
- Export clean, production-ready Python code that plugs directly into your preferred agent orchestration environment.

---

## 🛠️ Key Features (Planned)

- **Visual Node Editor**  
  Build workflows using a polished, interactive UI for connecting and configuring nodes.

- **Typed Inputs & Outputs**  
  Each node’s ports are typed using schema definitions to ensure correct data flow.

- **Runtime-Agnostic Code Generation**  
  Export workflows as executable Python code targeting frameworks like Mastra, LangGraph, or your own orchestration logic.

- **Agent-Centric Nodes**  
  Nodes can represent LLM calls, decision logic, data transformations, API calls, or custom Python functions.

- **Import & Export**  
  Save, load, and share workflow files with collaborators.

- **Extensibility**  
  Create your own node types, runtime exporters, and schema definitions.

---

## 📦 Installation

*(Installation instructions will be added once the first release is ready.)*

```bash
git clone https://github.com/<your-username>/AgentFlow.git
cd AgentFlow
pip install -e .
```

---

## 🚀 Quick Start

*(Example will be added after the initial implementation.)*

1. **Open AgentFlow’s visual editor**
2. **Drag nodes** onto the canvas
3. **Connect nodes** using typed ports
4. **Configure agent logic** via the node properties panel
5. **Export** to your target runtime (e.g., Mastra, LangGraph)
6. **Run** your agent system

---

## 🧠 Why AgentFlow?

Existing orchestration frameworks are powerful but code-centric.  
AgentFlow lets you:
- Start visually, think visually.
- Reduce the risk of wiring mismatches by enforcing schema-based connections.
- Empower non-programmers (designers, researchers) to collaborate directly in workflow creation.
- Maintain a clean separation between **design artifacts** and **runtime logic**.

---

## 🤝 Contributing

We welcome contributions from developers, AI researchers, and anyone passionate about building better agent tools.  
If you’d like to help, please:
1. Fork the repository
2. Create a feature branch
3. Submit a pull request

---

## 📄 License

**AgentFlow**  
Copyright (C) 2025 Enchantus AI, LLC  

This program is free software: you can redistribute it and/or modify it under the terms of the **GNU Affero General Public License** as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,  
but WITHOUT ANY WARRANTY; without even the implied warranty of  
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the  
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License  
along with this program. If not, see <https://www.gnu.org/licenses/>.
