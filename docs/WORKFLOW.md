# Running the triage workflow

The workflow is manual-only and gated by the repository variable `TRIAGE_ENABLED`.
An absent variable or any value other than `true` blocks activation. Opening issues
does not trigger it. Adding an API key alone does not enable it.

## Execution flow

1. Trusted activation code reads the selected open issue from this repository.
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
4. Both the agent job and threat detection must finish successfully before publication. The trusted
   publisher reloads code from the workflow revision, validates the output and
   target, and re-reads the issue to reject changed reports.
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

- Manual runs only, with a limit of five dispatches per user per hour, including
  the owner. Compiler rate limiting is experimental and needs live verification.
- A single workflow concurrency group serializes runs. GitHub's default queue
  retains one pending run; newer pending runs can replace older pending runs.
  Run evaluation cases sequentially and account for cancelled or missing cases.
- Agent inference is limited to 10 minutes; the agent job to 15 minutes; threat
  detection to 5 minutes; the publishing step to 3 minutes. Setup/download steps
  remain subject to their GitHub job defaults.
- Per-run budgets are 50 framework AI Credits for the agent and 20 for detection.
  These are framework accounting units, not a promised invoice amount. The daily
  workflow credit guardrail is disabled: manual-only admission, per-user limits
  and per-run budgets are used instead. Set separate API project spending limits.
- Extra status comments, reactions and failure-tracking issues are disabled so
  they cannot exceed the public-output contract.

From a phone browser, open the repository's Actions page, select the workflow and
use its menu to **Disable workflow**. Open each in-progress run and choose
**Cancel workflow**; disabling alone does not cancel running jobs. Set
`TRIAGE_ENABLED` to `false` before re-enabling. Cancellation cannot undo an action
already accepted by GitHub. The publisher checks the enable flag at job startup;
it does not continuously poll repository settings.

Bot-authored markers prevent duplicate comments. A retry can add a missing label
after a successful comment, but does not edit the existing comment. An existing
triage label or older bot response otherwise stops further publication. If a
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
validation, stale reports, retries, and the compiled permission/tool boundary.
Compilation emits an experimental-rate-limiting warning.

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
These observations do not prove universal hosted isolation or immediate interruption
of provider spending. Privileged users bypass the configured rate limit, and
history-check errors fail open; see [DESIGN.md](../DESIGN.md#governance).
Any further live runs require separate authorization.
