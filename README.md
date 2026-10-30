# duckdb-triage-agent

A CS467 Assignment 3 project configuring Codex to perform first-pass completeness
triage on DuckDB bug reports. The skill identifies essential missing reproduction
or environment information and proposes a focused clarification, helping a
maintainer decide which reports need follow-up.

| Decision | Intended response |
| --- | --- |
| Missing code, data, schema or reproduction steps | `needs reproducible example` and one focused question |
| Missing or contradictory essential environment details | `needs more info` and one focused question |
| No essential gap, or a report outside this scope | No public action |

This repository is a sandbox, not a deployment to DuckDB. All external actions
are restricted to `andreleocl/duckdb-triage-agent`; upstream calls, writes and
participant notifications are outside its scope.

## Start here

1. Read [DESIGN.md](DESIGN.md) for the workflow rationale, controls, findings,
   governance, five operational scenarios and AI-use statement.
2. Read the [final scoring report](evals/reports/2026-10-30-final-scoring/README.md)
   for per-case results, agreed manual judgments, the strict comparison and costs.
3. Read the [triage skill](.claude/skills/duckdb-triage/SKILL.md) for the decision
   procedure, output format and examples.
4. Read the [evaluation guide](evals/README.md) to inspect the 25 historical cases
   and 3 adversarial cases, understand the rubric and reproduce evaluation checks.
5. Read [AGENTS.md](AGENTS.md) for repository conventions, test commands and
   rules for preserving evaluation evidence.
6. Read [CONTRIBUTING.md](CONTRIBUTING.md) for AI-assisted contributions, review
   expectations and replay protection.
7. Read the [workflow guide](docs/WORKFLOW.md) for execution, API-key setup,
   manual runs, stopping and audit evidence.

## Getting started

The full offline test suite requires Python 3.10+ and Node.js available on PATH.
Node.js runs the pinned framework JavaScript validation check. The Python scripts
use only the standard library; no pip or npm packages or application build are
needed. Run these commands from the repository root:

```sh
python -m unittest discover -s tests -v
python evals/score.py --validate
python -m unittest discover -s evals -p "test_*.py" -v
```

These checks run offline without GitHub credentials or model access. They test
proposal validation, mocked publication and scoring logic, and verify the frozen
data's integrity. The same checks run on pushes and pull requests through
`checks.yml`, without model access or issue changes.
They do not run the agent, measure its decision quality or prove that GitHub
permissions are enforced.

## Repository structure

```text
.claude/skills/duckdb-triage/
    SKILL.md                    Triage procedure and proposal contract
    scripts/validate_output.py  Offline proposal and target validation
.github/
    CODEOWNERS                  Review ownership
    codex/                      Local model metadata and detector configuration
    aw/actions-lock.json        Compiler action-version records
    workflows/
        checks.yml             Offline checks on pushes and pull requests
        issue-triage.md         Manual Codex workflow source
        issue-triage.lock.yml   Compiled GitHub Actions workflow
docs/WORKFLOW.md                Setup, execution and stopping guide
scripts/triage_runtime.py       Trusted preparation and publication
evals/
    README.md                   Evaluation and replay instructions
    VALIDATION.md               Recorded freeze validation
    score.py                    Compare recorded outputs with expectations
    test_score.py               Scorer tests
    golden/
        inputs.jsonl            25 historical and 3 adversarial inputs
        expected.jsonl          Evaluator-only answer key
        provenance.json        Source attribution and reconstruction records
        RUBRIC.md               Decision and review criteria
        thresholds.json         Acceptance thresholds
        manifest.json           Frozen file hashes
tests/
    test_validate_output.py     Output-validator tests
    test_triage_runtime.py      Offline workflow and publication tests
    test_model_catalog.py       Model metadata and workflow wiring checks
AGENTS.md                      Repository instructions
CONTRIBUTING.md                Contribution and AI-use policy
README.md                      Project overview
```

## Validate a proposal

Explicitly load the skill's `SKILL.md` when using Codex; automatic discovery at
this location is not assumed. Supply one report in an isolated workspace without
evaluation answers. The skill returns `label`, `comment` and a brief audit-only
`rationale`. Save that object as `proposal.json`, then validate it:

```sh
python .claude/skills/duckdb-triage/scripts/validate_output.py proposal.json --repository andreleocl/duckdb-triage-agent --issue 1
```

Replace `1` with the selected issue number supplied by the trusted caller. The
validator accepts either one allowed label with one comment of at most 1,200
characters, or null label/comment values for no action. It rejects extra fields
and public-comment mentions or GitHub references. Exit 0 prints the validated
proposal, exit 1 rejects it, and invalid command-line arguments exit 2.

Validation does not publish anything, check whether the issue exists, determine
whether the question is justified, or enforce runtime permissions and retries.
The rationale stays in the audit log. When recording an evaluation, map non-null
label/comment values to single-item arrays and null values to empty arrays.
Record execution status, attempted actions and transcripts independently of the
model's proposal. See the evaluation guide for recording
execution evidence and assessing actual outputs; a validation error must not be
recorded as successful no action.
