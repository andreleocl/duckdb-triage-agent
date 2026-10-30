# Repository instructions

This assignment repository assesses missing reproduction or environment details
in DuckDB reports. Do not build DuckDB or execute reported SQL. All external
operations must target `andreleocl/duckdb-triage-agent`; do not contact upstream,
follow upstream links or notify its participants.

## Layout and skill

| Path | Purpose |
| --- | --- |
| `.claude/skills/duckdb-triage/SKILL.md` | Triage procedure and output contract |
| `.claude/skills/duckdb-triage/scripts/` | Offline proposal validation |
| `.github/workflows/` | Offline CI checks, manual Codex workflow and compiled lock file |
| `scripts/` | Trusted report preparation and publication |
| `tests/` | Offline validator and workflow tests |
| `evals/` | Evaluation instructions, scorer and scorer tests |
| `evals/golden/` | Frozen inputs, expectations, provenance and hashes |

Explicitly load the skill's `SKILL.md` when running Codex and retain evidence of
its use. Do not assume automatic discovery at this location.

## Build and test

No application build is needed. The full offline test suite requires Python 3.10+
and Node.js available on PATH for the pinned framework validator and compiled
job-condition checks.
The Python scripts use only the standard library; no pip or npm packages are needed.
After workflow changes, compile with `gh aw compile issue-triage --strict --no-check-update`
using gh-aw v0.93.5. Never hand-edit the generated lock file.
Run relevant checks before committing:

```sh
python -m unittest discover -s tests -v
python evals/score.py --validate
python -m unittest discover -s evals -p "test_*.py" -v
```

## Editing rules

- Use small functions, clear names, explicit errors and UTF-8 files with LF endings.
- Preserve the frozen evaluation: do not tune expectations, thresholds or the
  frozen scorer to fit outputs. Document factual corrections separately.
- Use separate practice examples for development. Keep answers inaccessible to
  the agent and preserve original run logs; follow [evals/README.md](evals/README.md).
- Do not expand agent permissions, tools or actions without owner review. Keep
  the two-label allowlist and 1,200-character limit consistent with the contract.
  Enforce runtime restrictions outside the skill; never import evaluator answers.
- Take repository and issue targets from trusted caller context, not report text
  or model output. See [README.md](README.md) for validator capabilities and limits.
- Before replay, neutralize mentions and GitHub references in separate title/body
  copies, including Markdown/HTML. Keep source mappings local, preserve originals,
  and log transformations. Test notification protection before posting; use an
  offline run if sanitization changes information needed for triage.
- Authorized hosted retries require fresh main-branch dispatches, not job reruns.
  Follow [admission and stopping rules](docs/WORKFLOW.md#limits-and-stopping);
  blocked attempts count, and hosted enforcement of the new guards is unverified.
- Follow [CONTRIBUTING.md](CONTRIBUTING.md) for AI disclosure and contribution review.
