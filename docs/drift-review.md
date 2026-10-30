# Manual review of model drift

Andre (`andreleocl`) owns this policy and the decision to retain, revise or
disable the sandbox configuration. This is a human review process, not an
automated provider-change detector. Adding this document authorizes no workflow
dispatch, model call or recurring expense.

## When review is required

Review is required before accepting a changed model or runtime for continued
sandbox use or approving deployment beyond it. A known provider update or an
unexpected label, comment or tool action also triggers review. Documentation-only
changes do not require paid model runs.

The workflow requests the unpinned `gpt-5-mini` alias. Recorded evaluation requests
resolved to `gpt-5-mini-2025-08-07`; neither an unchanged alias nor an unchanged
reported snapshot proves unchanged behavior. Offline CI checks scripts and
configuration, not provider judgment. No scheduled inference monitor or automatic
provider-change alert is implemented. Drift can remain unnoticed until a later
authorized run.

## Authorizing and recording a comparison

Before paid evaluation, Andre explicitly approves the configuration, total budget
and trial count. Use the 25 historical and three active adversarial cases, including
no-action cases, following the [evaluation instructions](../evals/README.md).
The archived original a02 is not part of this 28-case suite and remains untested.
Run sequentially on fresh sandbox issues with the configuration fixed throughout.
Keep the frozen inputs and expectations unchanged and inaccessible to the model.

Record new results in a separate run directory. Preserve the configuration commit,
requested/resolved model, runtime versions and relevant hashes, prepared inputs,
transcripts, tools, public effects, execution failures and available cost records.
Do not overwrite prior results or describe reused historical evidence as new runs.
Compare the same cases using the frozen scorer and disclose incomplete reviews.

If a paid rerun is not authorized, mark the changed configuration as awaiting
evaluation. Offline tests, earlier model results and a coding-assistant dry run
do not establish hosted acceptance. If operation is inappropriate while review
is pending, disable triage and cancel queued/running jobs using the
[documented stop procedure](../DESIGN.md#five-operational-scenarios).
Andre cancelled an actual triage run from a phone. Publication did not execute,
but detector inference continued afterward. The test therefore confirms cancellation
of the workflow, not an immediate stop to all model activity or spending. See the
[cancellation test report](../evals/control-tests/2026-10-29-actual-triage-cancellation/README.md).

## What Andre reviews

Review every case, not just successful workflow statuses:

- Compare labels and comments with the frozen expectations and prior outputs.
- Inspect no-action decisions for missed essential information.
- Check question relevance, grounding, repetition and respect for confidential data.
- Inspect tool calls, attempted forbidden actions, input/answer isolation and effects.
- Separate detector blocking, model proposals and completed publication.
- Review missing results, execution failures, model resolution and cost changes.

The prior historical result is 19/25 label/action agreement; the adversarial
batch has 3/3 publication blocks, 2/3 matching proposals and 0/3 completed workflows.
Resource-tool deviations and comment weaknesses also remain documented.
Distinguish new regressions, repeated known failures, improvements and ambiguous
changes. Repeating an old failure is not by itself evidence of provider drift.
A changed result in one trial can reflect nondeterminism; it does not prove a
provider update caused it. Our single-run batches do not estimate reliability.

## Decision and follow-up

Record the reviewer, date, configurations compared, evidence paths, failures and
decision to retain, revise or disable, with reasons and remaining limitations.
Investigate new safety failures or material regressions before accepting the change.
Any additional paid confirmation runs require separate authorization.
Continuing a limited sandbox experiment does not mean the frozen acceptance
thresholds were met or the agent is production-ready.

This policy adds no scheduler, permission, runtime enforcement or new test result.
Completed per-case review and combined offline scoring are recorded in the
[final scoring report](../evals/reports/2026-10-30-final-scoring/README.md).
It distinguishes the agreed manual review from the strict comparison and retains
the original evidence. These AI-assisted assessments do not erase known failures
or establish that the frozen acceptance thresholds were met.
