# LogPilot

AI agent that triages failing CI/test logs: parses the log, retrieves similar past incidents and
runbooks, diagnoses the root cause, and writes a bug report. It is evaluated against a labelled
set and compared with a classic ML baseline.

> Status: Milestone 1 of 9 (data + taxonomy). See [docs/PLAN.md](docs/PLAN.md).

## Quickstart
```bash
uv venv && uv pip install -e ".[dev]"
python -m logpilot.data.synth      # -> data/synthetic/{incidents,dev,test}.jsonl
python -m logpilot.data.loghub     # optional: real logs for the ML baseline
pytest
```

## Data
| Split | Cases | Used for |
|-------|-------|----------|
| incidents | 80 | RAG index (past incidents + their resolutions) |
| dev | 50 | Self-improvement loop (prompt tuning) |
| test | 100 | Final reported metrics only |

10 root-cause categories ([taxonomy.py](src/logpilot/data/taxonomy.py)). 40% of cases are "hard":
they contain red-herring lines that suggest a different category. Incidents and eval splits draw
from disjoint signal templates, so retrieval has to generalise instead of matching exact strings.
