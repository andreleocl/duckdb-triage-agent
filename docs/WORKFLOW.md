# Running the triage workflow

The workflow is manual-only and gated by the repository variable `TRIAGE_ENABLED`.
An absent variable or any value other than `true` blocks activation. Opening issues
does not trigger it. Adding an API key alone does not enable it.

## Execution flow

1. Trusted activation first checks the dispatch-history limit described below.
   Only after admission does it read the selected open issue from this repository.
   It rejects pull requests, empty reports and reports over 40,000 characters.
   It records the title/body, their hash, configuration revision and skill hash in
   the `triage-input` artifact. It loads the exact skill into the rendered prompt.
2. Codex receives that skill and report. Its job has no repository checkout,
   GitHub tools, shell, editing tools or web tools. It cannot retrieve the answer
   key. The firewall's empty external domain allowlist restricts direct egress;
   model inference uses the framework's API proxy.
3. Codex submits one proposal through `submit_triage`, including for no action.
   `report_incomplete` is available for errors and does not create an issue.
   The workflow adapter delegates CLI validation to trusted code rather than
   granting the agent shell access. The skill's decision rules remain unchanged.
4. Detection requires successful activation and agent jobs and no workflow
   cancellation. Both model jobs must finish successfully before publication.
   The trusted publisher reloads code from the workflow revision, validates the
   output and target, and re-reads the issue to reject changed reports. Activation,
   both model jobs and publication require the first run attempt; the publisher
   also checks this in Python. The [hosted control tests](#hosted-control-verification)
   exercised the owner limit, three rerun routes and cancellation at both model stages.
5. A request adds one comment and one allowed label using the Actions bot token.
   No action makes no public change. Internal rationale stays in the run artifacts,
   not the comment. Run logs/artifacts in this public repository are not private.

The publisher reuses the skill validator and additionally rejects links, HTML,
encoded mentions and issue references in public questions. Attribution and a
deduplication marker count toward the 1,200-character limit; the prompt asks for
fewer than 1,000 characters to leave room. Only fixed comment/label endpoints in
`andreleocl/duckdb-triage-agent` are writable. HTTP redirects are refused.

## Setup and first live test

Do these steps only when ready for a paid live test:

1. Add an OpenAI project key as the Actions secret `OPENAI_API_KEY`. Configure
   API billing and project spending controls separately; never commit credentials.
   The compiler also supports `CODEX_API_KEY` and gives it precedence if both exist.
2. Confirm API access to the model alias `gpt-5-mini`. The compiled runtime
   uses Codex CLI 0.164.0. Changing either requires a documented test and recompile.
3. Ensure the repository has the labels `needs reproducible example` and
   `needs more info`. Create a fresh invented practice issue, not a golden case.
4. Set the Actions repository variable `TRIAGE_ENABLED` to `true`.
5. From Actions, select **DuckDB issue triage**, choose **Run workflow**, select
   `main`, and enter the issue number. This runs inference and can post publicly.

Before replaying golden cases, follow
[the evaluation guide](../evals/README.md) and replay protections in
[AGENTS.md](../AGENTS.md). This workflow does not create replay issues or inject
the adversarial tool-result fixture. That fixture needs a separate test harness;
ordinary issue replay cannot establish that it was tested.

## Model metadata

Both model jobs load a local catalogue for the configured model alias. See
[catalogue provenance and compatibility notes](../.github/codex/README.md).
Both triage and threat detection use GPT-5 mini. Codex CLI remains at 0.164.0. The detector uses a separate
configuration directory because this compiler does not merge its custom Codex
configuration. Its OpenAI proxy and authentication settings are preserved.

## Limits and stopping

The admission and cancellation guards have offline checks and
[hosted control evidence](#hosted-control-verification) for the owner limit,
three rerun routes, short queueing and downstream blocking after cancellation.
Active model execution continued after cancellation; immediate interruption is not
guaranteed. These guards apply to the tested configuration, not older workflow
revisions or reruns of those revisions.

- Before issue preparation or inference, [trusted admission](../scripts/triage_runtime.py)
  requires at most **five unique manual-dispatch run IDs** for this repository's
  `issue-triage.lock.yml` workflow within the checked hour. All users, including
  the owner, and all outcomes count: queued, failed, cancelled and blocked attempts.
  This is a global workflow limit, not five per user.
- The window is measured at admission using the runner's UTC time, rounded to
  seconds, and GitHub's run-creation timestamps. Both endpoints are inclusive:
  `admission time - 60 minutes <= created_at <= admission time`.
  The current run must appear exactly once and match its branch, commit and first
  attempt. A run queued for more than an hour is refused and needs a fresh dispatch.
- Five matching IDs including the current run can pass; six cannot. Missing,
  malformed, duplicate or truncated history and API failures block admission.
  An allowable response fits on one page; the check refuses pagination rather
  than allowing from partial results. It relies on GitHub's history visibility.
- Counting blocked attempts is intentional: repeatedly dispatching while blocked
  can prolong the wait. Other queued dispatches may also cause a conservative
  rejection. Plan authorized batches around this limit instead of repeatedly retrying.
- This checks dispatch history at admission. It does not prevent GitHub from
  creating additional runs or cap model starts or dollars per rolling hour.
- A single workflow concurrency group serializes runs. GitHub's default queue
  retains one pending run; newer pending runs can replace older pending runs.
  Run evaluation cases sequentially and account for cancelled or missing cases.
- Agent inference is limited to 10 minutes; the agent job to 15 minutes; threat
  detection to 5 minutes; the publishing step to 3 minutes. Setup/download steps
  remain subject to their GitHub job defaults.
- Per-run budgets are 50 framework AI Credits for the agent and 20 for detection.
  These are framework accounting units, not a promised invoice amount. The daily
  workflow credit guardrail is disabled. Owner-approved batches and per-run budgets
  still matter; no enforced aggregate spending cap is established by this configuration.
- Extra status comments, reactions and failure-tracking issues are disabled so
  they cannot exceed the public-output contract.

From a phone browser, open the repository's Actions page, select the workflow and
use its menu to **Disable workflow**. Open each in-progress run and choose
**Cancel workflow**; disabling alone does not cancel running jobs. Set
`TRIAGE_ENABLED` to `false` before re-enabling. Cancellation cannot undo an action
already accepted by GitHub. The publisher checks the enable flag at job startup;
it does not continuously poll repository settings.

The detection job condition requires `!cancelled()` and successful activation
and agent jobs. In the hosted test, cancelling the triage execution step prevented
detection from starting; cancelling either model stage prevented publication.
However, both active execution steps continued and exited successfully internally,
even though GitHub marked their jobs cancelled. The recorded Codex processes started
after the cancellation request timestamps; this was not evidence of prompt process
termination or a guarantee that further API calls stop. The exact cause was not
established, so it is not attributed to the model or provider. Publication still
requires successful detection. Artifact/log collection remains enabled but can be
interrupted by cancellation. Retain available usage records and inspect charges;
do not treat cancellation as an immediate spending stop.

For retries, use **Run workflow** to create a fresh main-branch dispatch, subject
to admission. Do not use **Re-run jobs**: the first-attempt guards cover activation,
both models and publication, including publisher-only reruns. Do not use an older
revision's rerun as a workaround; the new controls cannot retrofit old workflows.

Bot-authored markers prevent duplicate comments. A fresh admitted dispatch can
add a missing label after a successful comment, but does not edit that comment.
An existing triage label or older bot response otherwise stops further publication. If a
maintainer intentionally removed a label, avoid rerunning that case: retry repair
cannot distinguish intentional removal from an interrupted label request.
GitHub comment and label writes are not atomic; inspect partial failures and the
receipt before retrying. Human edits can still race the final pre-write check.

## Offline checks and evidence

`checks.yml` runs the three Python checks below on pushes and pull requests,
with Python 3.12 and a read-only token. It needs no API key, invokes no model
and does not compile the agentic workflow; compile source changes locally.

Compile with GitHub CLI and the pinned `gh-aw` extension v0.93.5:

```sh
gh aw compile issue-triage --strict --no-check-update
python -m unittest discover -s tests -v
python evals/score.py --validate
python -m unittest discover -s evals -p "test_*.py" -v
```

The `.lock.yml` is compiler-generated; never edit it manually. Tests mock GitHub
and do not call a model or post anything. They check target restrictions, output
validation, stale reports, retries, admission-history edge cases and compiled
job-condition truth tables. They check the permission/tool boundary without
proving GitHub scheduling, history visibility or cancellation behavior.
The old framework user-rate limiter was replaced by trusted admission code.

Compilation references API secrets but does not create or read their values.
The compiler's new-secret review covered the Codex authentication references:
they feed the framework-managed inference path, not our scripts. Actions and
container images in the lock file are pinned by the compiler. These are static
checks, not evidence that the hosted sandbox or provider access works.

For live runs, retain `triage-input`, `triage-receipt`, and the framework's agent,
usage and detection artifacts before retention expires (30 days by default).
Inspect the rendered prompt to verify skill inclusion, then review the transcript
to assess whether its procedure was followed. Record requested/resolved model
identity, token usage and cost where available; unavailable fields are not zero.
Score the actual posted text/actions, including attribution, not just the proposal.
Record skipped duplicate/existing-label outputs separately from successful no-action
decisions. API operation receipts preserve attempted writes even on failure.

Offline checks do not establish live behavior. Recorded sandbox runs exercised
API authentication and bot publication; the
[final scoring report](../evals/reports/2026-10-30-final-scoring/README.md)
combines the 25 historical and three adversarial results, including failures.
The [disabled-start test](../evals/control-tests/2026-10-29-disabled-gate/README.md)
recorded all jobs skipped. The
[phone cancellation test](../evals/control-tests/2026-10-29-actual-triage-cancellation/README.md)
recorded no publication, but detector inference continued after cancellation.
Those runs used earlier configurations: the framework limiter exempted the owner
and would fail open on history errors, and detection could continue after cancellation.
They remain historical evidence; the later control tests below assess the new guards.

## Hosted control verification

The [30 October control report](../evals/control-tests/2026-10-30-admission-cancellation-73e7d64/README.md)
tested the actual workflow at `73e7d64` using GPT-5 mini and invented practice reports.
The agent, frozen key and original evaluation evidence were unchanged.

| Check | Observed result |
|---|---|
| Owner/admin admission and current-run visibility | Dispatches 1-5 passed with counts 1-5; the sixth failed admission before either model or publisher ran. |
| Counting and short queueing | Cancelled dispatches counted once; reruns added no new dispatch IDs. The fifth waited behind the fourth and then passed admission. |
| Rerun routes | Full-workflow, failed-jobs and publisher-only retries skipped the guarded jobs. No new inference or public actions occurred. |
| Cancellation during triage execution | Detection and publication ran zero steps; the active triage execution continued. |
| Cancellation during detection execution | Publication ran zero steps; the active detector continued. |
| Immediate interruption | Not demonstrated: six triage responses and three detector responses completed after their respective cancellation requests; both commands exited with code 0. |

Cancellation was requested while the execution steps were active, including their
setup time; it was not synchronized to a provider request already in flight.
Partial-rerun metadata includes inherited successful jobs with original execution
timestamps; those entries must not be counted as new inference. The report retains
per-attempt logs, pre-cancel snapshots, proposals, receipts and final issue state.

Recorded API cost was **$0.05258080**, including the cancelled runs. This is a token-based
estimate, not an invoice; missing in-flight usage could add charges, and Actions costs
are excluded. The $0.25 monitoring budget was not an enforced dollar cap.
`TRIAGE_ENABLED=false` was restored and all test runs completed. These tests do not
change golden scores or establish comment quality or tool compliance.

Malformed/incomplete history, API failures, simultaneous actors, queue expiry beyond
one hour and exact rolling-hour expiry were not injected in hosted tests. Offline
checks remain the evidence for history-validation and expiry handling. A subsequent
blocked-attempt lockout-expiry test was not run. The controls do not retrofit older
revisions or establish an atomic dispatch limit or aggregate dollar cap. See
[DESIGN.md](../DESIGN.md#governance) for the governance summary.
Any further live runs require separate authorization.
