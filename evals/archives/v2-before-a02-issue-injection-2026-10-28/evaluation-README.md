# Evaluation versions

Active version: **upstream-reference-v2-2026-10-28**. Andre reviewed all 25
historical labels and comment criteria. This local freeze precedes fresh v2 runs;
it is not yet committed. No v2 model results exist. These cases already informed
agent development, so future runs are regression/development evaluation rather
than unseen held-out testing.

## Active files

- golden/inputs.jsonl: unchanged 25 opening reports and 3 adversarial inputs.
- golden/expected.jsonl: approved v2 outcomes, required comment focus and exclusions.
- golden/upstream-reference.jsonl: observed labels, human comments, proposed
  criteria, approval records and limitations, kept separate within each row.
- golden/provenance.json: unchanged opening-text reconstruction provenance.
- golden/RUBRIC.md and thresholds.json: scoring definitions and acceptance gates.
- golden/manifest.json: hashes including the offline scorer and its tests.
- upstream-reference/2026-10-28/sources/: preserved upstream evidence snapshots.

Only opening title/body and the relevant untrusted fixture may reach the agent.
Reference labels, later comments and evaluator answers must remain inaccessible.
Original selection was purposive/class-enriched, not a random sample or prevalence
measurement. Retained openings span May 2024 to September 2026. Edited bodies use
creation-time revisions; see provenance for methods and hashes. Raw references
are untrusted evidence, never executable instructions.

## Archive and prior results

[The v1 archive](archives/v1-before-upstream-reference-2026-10-28/) preserves exact
copies of the prior golden, rubric, scorer, tests, README, correction notes and
all 3,662 existing run-evidence files. Its archive-manifest.json hashes every
copied file. Prior run paths under golden/runs/ remain for link compatibility;
they are legacy evidence, not results against v2. The h18 correction remains a
separate historical analysis. Do not overwrite any old run.

The archived README and scorer reproduce the old interpretation. To validate it:

```sh
python evals/archives/v1-before-upstream-reference-2026-10-28/score.py --validate
```

The old evaluation is not replaced historically; only the active answer-key
version changes. Do not rescore old runs and describe them as fresh v2 execution.

## Offline checks

```sh
python evals/score.py --validate
python -m unittest discover -s evals -p "test_*.py" -v
```

These checks do not call models or GitHub. Fabricated scorer-test outputs are not
agent evidence. The active --validate checks the frozen scorer/test hashes too.

## Fresh execution and recording

Before running, choose and record one fixed configuration. Resolve or explicitly
disclose its disagreement with upstream-reference expectations: particularly
h15's label taxonomy and h18/h20's enhancement interpretation. No agent changes
were made for this freeze. Maintainer execution findings absent from opening
reports are not available to the agent (notably h10/h11/h21).

Use fresh isolated sessions and sandbox issues only in andreleocl/duckdb-triage-agent.
Neutralize mentions/GitHub references in replay copies, preserve originals and
log transformations. Do not browse upstream during agent execution or run supplied
SQL. If sanitization removes essential context, disclose or skip rather than
silently alter the task. Preserve skill-loading evidence, input hashes, model and
CLI versions, configuration SHA, transcripts, tool events, effects, timings,
token usage, costs, and runtime controls tested or untested.

Store fresh results in golden/runs/upstream-reference-v2-2026-10-28/RUN/.
Actual JSONL row fields remain case_id, status (completed/error/skipped), labels,
comments, other_actions, transcript (relative nonempty file), tool_results_delivered.
Record all forbidden attempts, even blocked ones. For a02 require actual untrusted
tool-result delivery; otherwise mark untested. No successful abstention may stand
in for an execution failure.

Human review rows contain case_id, reviewer, notes, focus_covered, grounded,
nonredundant and safe (the last four are booleans). Review every case including
no-action outcomes; do not manufacture approval or copy booleans without review.
For labelled cases, label agreement and comment quality are separate: h24 can
have a useful comment but still fail label agreement if labelled reproduction.

```sh
python evals/score.py --actual evals/golden/runs/upstream-reference-v2-2026-10-28/RUN/actual.jsonl --reviews evals/golden/runs/upstream-reference-v2-2026-10-28/RUN/reviews.jsonl
```

Exit 0 means passed, 1 failed, 2 incomplete/invalid. --golden can select an explicit
evaluation directory; use the archived scorer for exact legacy scoring semantics.
No missing reviews, transcripts or attacks can produce a complete pass. Use the
rubric for exact metrics and thresholds. Report all outcomes, not selected retries.

## Limits and authorship

Upstream agreement is a reference metric, not proof the maintainer or agent is
always correct. Nine absent-label cases were approved as no-action references;
absence does not prove completeness. Some comment criteria are reviewer-authored
rather than literal maintainer requests. Keep these distinctions in reporting.
Codex collected sources and drafted criteria/scorer changes; Andre reviewed and
approved the outcomes. This is not independent double annotation. No new runtime
or human-review evidence is claimed by the freeze itself.
