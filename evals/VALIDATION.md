# Freeze validation

Validated on 2026-10-27 with Python 3.12.10.

- `python evals/score.py --validate`: all 28 cases and frozen file hashes valid.
- `python -m unittest discover -s evals -p "test_*.py" -v`: 7 tests passed.

Tests use fabricated outputs to check the scorer, including missing evidence,
wrong decisions, unsafe actions and attack-fixture delivery. They do not run an
agent or measure agent performance. Configured-agent runs at this freeze: **0**.
