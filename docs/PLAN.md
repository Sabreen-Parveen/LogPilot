# LogPilot — Build Plan (~10 working days)

Each milestone ends with something runnable, tested, and committed, so you can stop at any
point and still have a coherent project.

| # | Milestone | Days | Deliverable | Interview talking point |
|---|-----------|------|-------------|-------------------------|
| 1 | Skeleton + data | 1 | Failure taxonomy, synthetic labelled logs (train/incidents/eval split), runbooks, Loghub downloader | Why a closed label taxonomy makes "root-cause accuracy" measurable; leakage-free splits |
| 2 | LLM layer | 0.5 | `LLMClient` interface with Ollama + Anthropic/OpenAI backends, token/cost/latency accounting | Provider abstraction; every call is metered so eval can report cost |
| 3 | RAG | 1 | Chroma index of incidents + runbooks with `bge-small` / `all-MiniLM` embeddings; `search_incidents()` | Chunking choices, embedding model trade-offs, retrieval recall@k measured separately |
| 4 | LangGraph agent | 2 | `parse → retrieve → diagnose → write_report` graph with typed state, structured JSON output, retry on bad JSON | Why a graph instead of one prompt: inspectable steps, per-node eval, conditional edges |
| 5 | MCP server | 1 | `read_log`, `search_incidents`, `run_check` tools over stdio; agent can call them as tools | MCP as a tool contract decoupled from the agent; sandboxing `run_check` |
| 6 | Eval harness | 1.5 | `logpilot eval` → accuracy, macro-F1, retrieval recall, p50/p95 latency, tokens, $ → `reports/*.md` + JSON | Offline eval as a regression test for prompts; confusion matrix to find weak classes |
| 7 | ML baseline | 1 | TF-IDF + IsolationForest (anomaly detection) and LogisticRegression (classification) on the same eval set | When classic ML beats LLMs (cheap, fast) and where it fails (unseen phrasing, explanations) |
| 8 | Self-improvement | 1.5 | Loop: run eval on a *dev* split → collect failures → LLM proposes prompt edits / few-shot examples / retrieval k → re-eval → keep if better; report before/after on *held-out test* | Avoiding overfitting the eval set (dev vs test), optimisation as search with an acceptance rule |
| 9 | Ship | 1 | FastAPI `/triage`, Dockerfile, pytest, GitHub Actions (lint + tests with a fake LLM), README w/ diagram + results table | Deterministic CI with a mocked LLM; containerising a model-backed service |

Buffer: ~1 day for things going wrong (they will — usually JSON parsing from small local models).

## Key design decisions (decided up front)

- **Python 3.11+**, `uv` for env management, `src/` layout.
- **Closed taxonomy of 10 root-cause categories** (`src/logpilot/data/taxonomy.py`). The agent must
  output one of them, so accuracy is exact-match, not a vibes judgement. The free-text explanation
  is graded separately (optional LLM-as-judge).
- **Three disjoint data splits** generated from different seeds:
  `incidents` (goes into the RAG index), `dev` (used by the self-improvement loop),
  `test` (only ever used for final reported numbers).
- **Every LLM call goes through one client** that records tokens, latency, and cost.
- **A `FakeLLM`** lets the whole pipeline run in CI with no model.
