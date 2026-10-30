# Hosted admission and cancellation verification

Tested the actual `issue-triage.lock.yml` workflow at `73e7d64c4a95c0cc23fd63d725499e4ad2f0fbec` on 30 October 2026. GPT-5 mini, the agent instructions, workflow, frozen key and prior evidence were unchanged. These are operational control tests using invented reports, not a new golden evaluation or comment-quality score.

## Findings

- The owner/admin was subject to the admission limit: dispatches 1–5 were admitted and dispatch 6 was rejected before either model or publisher ran. Admission logs counted each unique run ID once, including cancelled runs; job reruns did not become new dispatch IDs.
- Publisher-only, full-workflow and failed-jobs reruns were blocked from new model execution/publication. The publisher-only test used previously successful output, so it exercised the retained-output retry route.
- Cancelling the triage execution step prevented detection from starting and prevented publication. Cancelling the detection execution step prevented publication.
- **Cancellation did not promptly interrupt the active model execution.** Both cancelled execution steps continued through recorded responses and exited with code 0, although their jobs were ultimately marked cancelled. The successful control is prevention of downstream execution/publication, not immediate provider interruption.
- A queued fifth dispatch was admitted after the fourth finished. It was created at 08:38:30 UTC, observed pending with no jobs, started pre-activation at 08:41:47 UTC and passed admission at 08:42:24 UTC with count 5.
- `TRIAGE_ENABLED=false` was restored after dispatch 6. All six dispatches and all requested rerun attempts completed. Nothing was committed or pushed.

## Dispatches

All runs were initiated through the owner account `andreleocl`, whose administrator permission is recorded in [owner-permission.json](owner-permission.json). The reports describe an invented CSV import failure with the input CSV omitted. The expected normal action was `needs reproducible example` and a focused request for the missing CSV. Runs 2 and 3 were deliberately cancelled; run 6 reused issue 69 and was expected to be denied before reading/preparing its report.

| Dispatch | Practice issue | Run | Result | Recorded API estimate (USD) |
|---|---|---|---|---:|
| 1 | [#69](https://github.com/andreleocl/duckdb-triage-agent/issues/69) | [41026019311](https://github.com/andreleocl/duckdb-triage-agent/actions/runs/41026019311) | Admitted at count 1; one comment and reproduction label published. | $0.01044160 |
| 2 | [#70](https://github.com/andreleocl/duckdb-triage-agent/issues/70) | [41026720311](https://github.com/andreleocl/duckdb-triage-agent/actions/runs/41026720311) | Admitted at count 2; cancelled during triage execution; detection/publisher ran zero steps. | $0.00703530 |
| 3 | [#71](https://github.com/andreleocl/duckdb-triage-agent/issues/71) | [41027150369](https://github.com/andreleocl/duckdb-triage-agent/actions/runs/41027150369) | Admitted at count 3; cancelled during detection execution; publisher ran zero steps. | $0.01118610 |
| 4 | [#72](https://github.com/andreleocl/duckdb-triage-agent/issues/72) | [41027692913](https://github.com/andreleocl/duckdb-triage-agent/actions/runs/41027692913) | Admitted at count 4; one comment and reproduction label published. | $0.01122525 |
| 5 | [#73](https://github.com/andreleocl/duckdb-triage-agent/issues/73) | [41027810949](https://github.com/andreleocl/duckdb-triage-agent/actions/runs/41027810949) | Admitted at count 5 after queueing; one comment and reproduction label published. | $0.01269255 |
| 6 | [#69](https://github.com/andreleocl/duckdb-triage-agent/issues/69) | [41028388343](https://github.com/andreleocl/duckdb-triage-agent/actions/runs/41028388343) | Rejected at admission: five-dispatch limit; both models and publisher skipped. | $0.00000000 |

**Total recorded API estimate: $0.05258080 (about 5.26 US cents)**, below the $0.25 monitoring budget. This budget was not an enforced dollar cap. Costs use unique request IDs from each first attempt’s agent/detection token logs at $0.25/M uncached input, $0.025/M cached input and $2/M output tokens. All recorded model IDs were `gpt-5-mini-2025-08-07`. Duplicate fallback/usage artifacts and inherited rerun logs are not counted again. No model steps ran in the rejected dispatch or the guarded rerun routes.

These are recorded usage estimates, not an OpenAI invoice. Cancelled or in-flight requests missing from local token records could add provider charges. GitHub Actions costs are excluded. See [costs.json](costs.json).

## Rerun routes

| Source run / attempt | Route | Observed result |
|---|---|---|
| [41026019311 / 2](https://github.com/andreleocl/duckdb-triage-agent/actions/runs/41026019311/attempts/2) | publisher-only | submit_triage skipped with zero steps; no new model calls or public actions. |
| [41026019311 / 3](https://github.com/andreleocl/duckdb-triage-agent/actions/runs/41026019311/attempts/3) | all jobs | activation, agent, detection, submit_triage skipped with zero steps; no new model calls or public actions. |
| [41026720311 / 2](https://github.com/andreleocl/duckdb-triage-agent/actions/runs/41026720311/attempts/2) | failed jobs | agent, detection, submit_triage skipped with zero steps; no new model calls or public actions. |

GitHub includes inherited successful jobs in partial-rerun responses, with new job IDs/attempt fields but the original start/end timestamps. Those entries are not evidence of fresh execution. The guarded jobs had zero steps, and the original model timestamps were retained. Issue 69 still had exactly one bot comment and label after all retries and the rejected sixth dispatch; cancelled issue 70 had neither.

The first publisher-rerun monitoring query briefly received HTTP 404 before GitHub exposed attempt 2. It was re-read without another rerun request; the same attempt then showed the publisher skipped. This was an observation delay, not an additional workflow dispatch or admission bypass.

## Cancellation evidence and limitation

Cancellation was sent through GitHub’s normal cancel endpoint after the relevant execution step was observed `in_progress`, followed by a 12-second observation window. The pre-cancel job snapshots are retained. This timing proves cancellation during the execution step; it does not establish that a provider request was already underway when cancellation was sent.

| Stage | Cancel request recorded (UTC) | Responses completed after request | Last recorded response (UTC) | Downstream result |
|---|---|---:|---|---|
| Triage | 08:30:27.233 | 6 | 08:30:43.332 | Detection and publisher marked cancelled with zero steps; no public actions. |
| Detection | 08:35:45.331 | 3 | 08:35:56.214 | Publisher marked cancelled with zero steps; no public actions. |

Both corresponding execution logs end in `Process exiting with code: 0`. The detector never started in the triage-cancellation test, but it continued to finish its work in the detection-cancellation test. Do not describe this as an immediate model kill switch or a guarantee that cancellation halts billing. The cause of continued active execution was not established by these tests.

## Evidence and scope

- [selection.json](selection.json): configuration, planned checks and monitoring budget recorded before dispatch; invented report bodies are in `issue-1.json` through `issue-5.json`.
- [operations.jsonl](operations.jsonl): dispatch, rerun, cancellation, status and disable observations; [results.json](results.json): structured results; [history-after.json](history-after.json): the six unique dispatches in the queried hour.
- Each run directory retains attempt-specific job/run metadata and logs; first-attempt artifacts retain prompts, skill/input hashes, model logs, outputs and receipts where generated. `jobs-before-cancel.json` captures the cancellation-stage observation.
- Final issue snapshots record three normally published comments/labels and no publication on either cancelled issue. [gate-final.json](gate-final.json) records the disabled variable.
- [evidence-manifest.json](evidence-manifest.json) hashes the files in this evidence directory and records hashes of the unchanged implementation/skill and frozen evaluation manifest.

This verifies the owner/admin boundary and the three tested rerun routes for this revision. It is not a proof against all scheduler races, simultaneous actors, incomplete history, API failures, a queue wait exceeding one hour, or exact rolling-hour expiry; those edge cases were not injected in hosted execution. The short queue wait was tested, not hour-long expiry. Counting blocked attempts can extend lockout; the rejected sixth dispatch remains in history, but a subsequent lockout-expiry test was not run.

The limit counts dispatch history at admission, not model starts or dollars per rolling hour. It is not atomic with other dispatch creation. Existing offline checks remain the evidence for malformed/incomplete-history and expired-queue handling. These guards do not retrofit older workflow revisions. This control test does not resolve the separate tool-compliance or comment-quality limitations, and the existing evaluation scores are unchanged.
