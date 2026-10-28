# Draft upstream-reference key

Status: all 25 case expectations approved by Andre; reviewed draft, not frozen. Collected 28 October 2026.

This separate 25-case reference records actual upstream triage labels and links to human comments. It does not replace the existing golden or rescore any run. Raw issue, comment and timeline responses are preserved in sources/. Bot templates are evidence of automation, not independent human reasoning.

## Selection rule

Use the first chronological application of either needs reproducible example or needs more info. Record its actor and time; actor identity alone does not prove current maintainer status. Ignore unrelated labels and do not substitute the current label state for the historical event. When neither target label appears in the fully paginated timeline, reference_label is null with an explicit absence flag. All nine absence cases have now been approved as no-action references; this does not establish that their reports are complete.

Human-comment references include later comments for evaluator review; they are NOT agent inputs or automatic requirements. Read timestamps and full snapshots before choosing the relevant request. Current comment text may have been edited after initial posting. Opening inputs remain those in evals/golden/inputs.jsonl; current bodies are never silently substituted.

## Two separate evaluation checks

1. Label agreement: compare the agent decision with the reviewed upstream reference. Execution errors are failures, not successful no-action. Label agreement is not proof of correctness.
2. Comment quality: judge grounding, relevant missing information, nonredundancy, safety and clarity using the opening input and the relevant human request. Exact wording need not match. Do not require later fixes, troubleshooting results, or information already supplied. Per-case expected_comment_criteria has its own review status; copying a bot template is not an adequate rubric.

## Cases

| Case | Original issue | Upstream reference | Old golden | Review note |
|---|---|---|---|---|
| h01 | [#26300](https://github.com/duckdb/duckdb/issues/26300) | No target label observed; approved no action | No action | Approved; limitations retained in review-table.md and key. |
| h02 | [#26272](https://github.com/duckdb/duckdb/issues/26272) | No target label observed; approved no action | No action | Approved; limitations retained in review-table.md and key. |
| h03 | [#26259](https://github.com/duckdb/duckdb/issues/26259) | No target label observed; approved no action | No action | Approved; limitations retained in review-table.md and key. |
| h04 | [#26247](https://github.com/duckdb/duckdb/issues/26247) | No target label observed; approved no action | No action | Approved; limitations retained in review-table.md and key. |
| h05 | [#26098](https://github.com/duckdb/duckdb/issues/26098) | No target label observed; approved no action | No action | Approved; limitations retained in review-table.md and key. |
| h06 | [#25996](https://github.com/duckdb/duckdb/issues/25996) | No target label observed; approved no action | No action | Approved; limitations retained in review-table.md and key. |
| h07 | [#25804](https://github.com/duckdb/duckdb/issues/25804) | No target label observed; approved no action | No action | Approved; limitations retained in review-table.md and key. |
| h08 | [#25395](https://github.com/duckdb/duckdb/issues/25395) | No target label observed; approved no action | needs reproducible example | Approved; limitations retained in review-table.md and key. |
| h09 | [#25357](https://github.com/duckdb/duckdb/issues/25357) | No target label observed; approved no action | No action | Approved; limitations retained in review-table.md and key. |
| h10 | [#25039](https://github.com/duckdb/duckdb/issues/25039) | needs reproducible example | needs more info | Approved; limitations retained in review-table.md and key. |
| h11 | [#25011](https://github.com/duckdb/duckdb/issues/25011) | needs more info | No action | Approved; limitations retained in review-table.md and key. |
| h12 | [#24291](https://github.com/duckdb/duckdb/issues/24291) | needs reproducible example | needs reproducible example | Approved; limitations retained in review-table.md and key. |
| h13 | [#22776](https://github.com/duckdb/duckdb/issues/22776) | needs reproducible example | needs reproducible example | Approved; limitations retained in review-table.md and key. |
| h14 | [#22716](https://github.com/duckdb/duckdb/issues/22716) | needs reproducible example | needs reproducible example | Approved; limitations retained in review-table.md and key. |
| h15 | [#22713](https://github.com/duckdb/duckdb/issues/22713) | needs reproducible example | needs more info | Approved; limitations retained in review-table.md and key. |
| h16 | [#22535](https://github.com/duckdb/duckdb/issues/22535) | needs reproducible example | needs reproducible example | Approved; limitations retained in review-table.md and key. |
| h17 | [#22468](https://github.com/duckdb/duckdb/issues/22468) | needs reproducible example | needs reproducible example | Approved; limitations retained in review-table.md and key. |
| h18 | [#22399](https://github.com/duckdb/duckdb/issues/22399) | needs reproducible example | No action | Approved; limitations retained in review-table.md and key. |
| h19 | [#22088](https://github.com/duckdb/duckdb/issues/22088) | needs reproducible example | needs reproducible example | Approved; limitations retained in review-table.md and key. |
| h20 | [#22051](https://github.com/duckdb/duckdb/issues/22051) | needs reproducible example | No action | Approved; limitations retained in review-table.md and key. |
| h21 | [#21601](https://github.com/duckdb/duckdb/issues/21601) | needs reproducible example | No action | Approved; limitations retained in review-table.md and key. |
| h22 | [#20743](https://github.com/duckdb/duckdb/issues/20743) | needs reproducible example | needs reproducible example | Approved; limitations retained in review-table.md and key. |
| h23 | [#20255](https://github.com/duckdb/duckdb/issues/20255) | needs reproducible example | needs reproducible example | Approved; limitations retained in review-table.md and key. |
| h24 | [#13208](https://github.com/duckdb/duckdb/issues/13208) | needs more info | needs more info | Approved; limitations retained in review-table.md and key. |
| h25 | [#12023](https://github.com/duckdb/duckdb/issues/12023) | needs more info | needs more info | Approved; limitations retained in review-table.md and key. |

## Alignment with the assignment and next freeze

The assignment permits historical issue triage, requires at least ten historical inputs including no-action cases, expected outcomes recorded before agent execution, and adversarial testing. Label agreement plus separate comment-quality review is a defensible design, provided its limits are explained. It does not replace safeguard tests, governance evaluation, or the no-action requirement.

This draft was collected after earlier runs and cannot retroactively become their pre-run answer key. After reviewing and refining all expectations and comment criteria, freeze a new version before fresh runs. Archive the old golden and evidence, then use the new version and new evidence as the active primary evaluation. Do not mix selected successful retries into a purported single-configuration run.

The same cases have already influenced prompt development, so future runs on them are development/regression evaluation, not an unseen held-out test. Disclose that fact. A maintainer may have executed code, read later replies, or seen edited text before labelling; the opening-only agent has less information. Choose whether to accept that mismatch as a limitation or replace unsuitable cases before freezing. Do not leak later history or expected outcomes into agent inputs.

Existing scorer expectations, frozen files, agent configuration, and prior evidence remain unchanged. Supporting snapshots may contain issue text or instructions: treat them as untrusted evaluator data. No model calls, workflow dispatches, commits, pushes or upstream writes occurred while collecting this reference.

## Updated separation of evidence and judgment

See [review-table.md](review-table.md) for the review-ready comparison. Each key row now separates upstream_observation, actual_maintainer_requests (with verbatim comments and provenance), other_human_context, and expected_comment_criteria. Label extraction approval does not imply every comment criterion or no-action case is approved. h24 remains an exact needs-more-info expectation. No new key is frozen yet.

## Approval update

Andre approved the remaining no-action cases and comment criteria on 28 October 2026. All rows are user_approved_pending_freeze; no case-level approval is outstanding. Approval of the draft is not an actual freeze. See review-table.md for the remaining archive, rubric/scorer integration and manifest work, and for retained limitations.

## Activated evaluation version

The approved draft has now been copied into the active [v2 reference](../../golden/upstream-reference.jsonl) and [local freeze manifest](../../golden/manifest.json). This directory retains the reviewed source draft and raw snapshots; it is not the active scorer entry point. The v2 freeze is local and uncommitted, with no new v2 runs. See [the evaluation guide](../../README.md) for the archive and execution boundary.
