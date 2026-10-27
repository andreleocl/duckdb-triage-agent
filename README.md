# duckdb-triage-agent

Sandbox for CS467 Assignment 3: configuring a Codex agent with a GitHub Agentic Workflow and a triage skill to identify missing reproduction information in bug reports, evaluated on historical issues from duckdb/duckdb.

This repository is a sandbox. The agent is not deployed to the DuckDB project.

## Current stage

The [evaluation freeze](evals/README.md) contains 25 historical cases, 3 constructed
adversarial cases, expected outcomes, a rubric and an offline scorer. No agent,
skill or workflow has been built or evaluated yet. API access will be decided later.

```sh
python evals/score.py --validate
python -m unittest discover -s evals -p "test_*.py" -v
```
