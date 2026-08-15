# TRACEBACK AI Investigation Agent — Isolated LangGraph Engine

This folder contains the **isolated implementation and test suite** for the TRACEBACK AI Root-Cause Investigation Agent built with **LangChain** and **LangGraph**.

> [!IMPORTANT]
> **ISOLATION DIRECTIVE**: This package is 100% self-contained inside `langgraph_investigation_agent/`. It does NOT modify existing FastAPI routes, production DB schemas, or frontend UI components.

---

## 1. Quick Start

### A. Environment Configuration
Copy `.env.example` to `.env` and set appropriate API keys (or run in synthetic testing mode):
```bash
cp .env.example .env
```

### B. Run Synthetic Investigation Demo
Execute all 5 investigation scenarios end-to-end:
```bash
python3 -m app.run_demo
```

### C. Run Full Pytest Test Suite
```bash
python3 -m pytest tests -v
```

### D. Inspect & Generate Workflow Diagrams
```bash
python3 scripts/inspect_graph.py
```

---

## 2. Architecture & Directory Overview

```
langgraph_investigation_agent/
├── app/
│   ├── graph/          # State definition, Nodes, Router functions, Workflow graph
│   ├── tools/          # PostgreSQL structured log tool & tool schemas
│   ├── models/         # Pydantic structured output models & LLM/Vision abstractions
│   ├── retrieval/      # Qdrant knowledge retrieval, previous incident retrieval & Reranker
│   └── analysis/       # Evidence filtering, Self-RAG decision & Hypothesis generator
├── tests/              # 8 comprehensive pytest test files covering nodes, state, routing, full workflow
├── examples/           # 5 synthetic input JSON scenario fixtures
├── diagrams/           # Visual workflow diagrams (.mmd, .png, .svg)
└── reports/            # Detailed Architecture Report & Empirical Test Report
```
