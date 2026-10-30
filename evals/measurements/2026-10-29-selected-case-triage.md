# Existing-sample triage measurement

Measured locally on 29 October 2026 using upstream snapshots retrieved on
28 October 2026. No new network collection or agent execution was performed.
Codex calculated and drafted this report following Andre's approval of the method.
This is a descriptive measurement of the selected cases, not a repository census.

## Sources and method

Source: the 25 h01-h25 JSON files in
[the saved source directory](../upstream-reference/2026-10-28/sources/).
For each case, read issue.created_at, comments and timeline from its snapshot.
Select timeline events whose event is labeled and whose label is exactly
needs reproducible example or needs more info. Sort by created_at and select
only the first matching event; repeated applications do not add cases.
Compute elapsed hours as (label timestamp minus opening timestamp) / 3600.
Compute the median over the 16 labelled cases using unrounded elapsed times.
Exclude absent-label cases from that median; absence is not zero elapsed time.
Count distinct actor logins on those first events (accounts, not verified people).

For bot follow-up, select comments by duckdb-bot or duckdblabs-bot whose body
contains the case-insensitive phrase reproducible example and whose timestamp
is at or after the selected label event. Count issues with at least one such
comment, not total comments. This phrase/account rule is a proxy for reproduction
guidance, not a general semantic classifier. Links below allow inspection.
All timestamps are UTC. No assumption of full repository coverage is made.

## Findings

- Selected issues opened from 13 May 2024 through 30 September 2026.
- 16 of the 25 selected cases have a recorded target-label application:
  13 reproduction labels and three information labels; nine have neither.
- Six different accounts applied those first target labels.
- Median opening-to-first-target-label time among the 16 labelled cases: **25.1 hours**.
- All 13 reproduction-labelled cases have a subsequent matching bot guidance comment.

These observations document recurring human-account classification followed by
bot guidance, supporting assistance with initial assessment and tailored questions.
They do not establish automatic-trigger implementation or causal workload savings.

## Per-case audit table

Elapsed hours are rounded only for display. A dash means no observed target event,
not no maintainer activity. The snapshot link contains the event and comment records.

| Case / issue | Opening UTC | First target label UTC | Label | Actor | Hours | Bot guidance | Snapshot |
|---|---|---|---|---|---:|---|---|
| [h01](https://github.com/duckdb/duckdb/issues/26300) | 2026-09-30T17:57:09Z | - | - | - | - | - | [source](../upstream-reference/2026-10-28/sources/h01.json) |
| [h02](https://github.com/duckdb/duckdb/issues/26272) | 2026-09-29T20:49:25Z | - | - | - | - | - | [source](../upstream-reference/2026-10-28/sources/h02.json) |
| [h03](https://github.com/duckdb/duckdb/issues/26259) | 2026-09-29T13:35:50Z | - | - | - | - | - | [source](../upstream-reference/2026-10-28/sources/h03.json) |
| [h04](https://github.com/duckdb/duckdb/issues/26247) | 2026-09-29T08:16:37Z | - | - | - | - | - | [source](../upstream-reference/2026-10-28/sources/h04.json) |
| [h05](https://github.com/duckdb/duckdb/issues/26098) | 2026-09-23T15:05:42Z | - | - | - | - | - | [source](../upstream-reference/2026-10-28/sources/h05.json) |
| [h06](https://github.com/duckdb/duckdb/issues/25996) | 2026-09-21T20:24:14Z | - | - | - | - | - | [source](../upstream-reference/2026-10-28/sources/h06.json) |
| [h07](https://github.com/duckdb/duckdb/issues/25804) | 2026-09-16T13:47:47Z | - | - | - | - | - | [source](../upstream-reference/2026-10-28/sources/h07.json) |
| [h08](https://github.com/duckdb/duckdb/issues/25395) | 2026-09-06T01:22:00Z | - | - | - | - | - | [source](../upstream-reference/2026-10-28/sources/h08.json) |
| [h09](https://github.com/duckdb/duckdb/issues/25357) | 2026-09-04T11:39:29Z | - | - | - | - | - | [source](../upstream-reference/2026-10-28/sources/h09.json) |
| [h10](https://github.com/duckdb/duckdb/issues/25039) | 2026-08-27T02:56:40Z | 2026-08-27T05:51:26Z | needs reproducible example | Tishj | 2.91 | [comment](https://github.com/duckdb/duckdb/issues/25039#issuecomment-5434946210) | [source](../upstream-reference/2026-10-28/sources/h10.json) |
| [h11](https://github.com/duckdb/duckdb/issues/25011) | 2026-08-25T14:09:20Z | 2026-08-27T06:14:05Z | needs more info | Tishj | 40.08 | - | [source](../upstream-reference/2026-10-28/sources/h11.json) |
| [h12](https://github.com/duckdb/duckdb/issues/24291) | 2026-07-29T23:14:22Z | 2026-08-06T07:37:20Z | needs reproducible example | DinosL | 176.38 | [comment](https://github.com/duckdb/duckdb/issues/24291#issuecomment-5201791345) | [source](../upstream-reference/2026-10-28/sources/h12.json) |
| [h13](https://github.com/duckdb/duckdb/issues/22776) | 2026-05-20T06:12:32Z | 2026-05-20T07:44:46Z | needs reproducible example | DinosL | 1.54 | [comment](https://github.com/duckdb/duckdb/issues/22776#issuecomment-4495854686) | [source](../upstream-reference/2026-10-28/sources/h13.json) |
| [h14](https://github.com/duckdb/duckdb/issues/22716) | 2026-05-17T03:56:30Z | 2026-05-18T08:24:18Z | needs reproducible example | DinosL | 28.46 | [comment](https://github.com/duckdb/duckdb/issues/22716#issuecomment-4475778052) | [source](../upstream-reference/2026-10-28/sources/h14.json) |
| [h15](https://github.com/duckdb/duckdb/issues/22713) | 2026-05-16T20:16:04Z | 2026-05-18T08:14:52Z | needs reproducible example | DinosL | 35.98 | [comment](https://github.com/duckdb/duckdb/issues/22713#issuecomment-4475717625) | [source](../upstream-reference/2026-10-28/sources/h15.json) |
| [h16](https://github.com/duckdb/duckdb/issues/22535) | 2026-05-09T20:38:45Z | 2026-05-11T09:25:33Z | needs reproducible example | DinosL | 36.78 | [comment](https://github.com/duckdb/duckdb/issues/22535#issuecomment-4419250808) | [source](../upstream-reference/2026-10-28/sources/h16.json) |
| [h17](https://github.com/duckdb/duckdb/issues/22468) | 2026-05-04T22:35:55Z | 2026-05-05T07:33:09Z | needs reproducible example | DinosL | 8.95 | [comment](https://github.com/duckdb/duckdb/issues/22468#issuecomment-4377337290) | [source](../upstream-reference/2026-10-28/sources/h17.json) |
| [h18](https://github.com/duckdb/duckdb/issues/22399) | 2026-04-30T13:11:55Z | 2026-05-01T10:51:57Z | needs reproducible example | DinosL | 21.67 | [comment](https://github.com/duckdb/duckdb/issues/22399#issuecomment-4358965167) | [source](../upstream-reference/2026-10-28/sources/h18.json) |
| [h19](https://github.com/duckdb/duckdb/issues/22088) | 2026-04-15T10:58:48Z | 2026-04-16T16:58:37Z | needs reproducible example | DinosL | 30.00 | [comment](https://github.com/duckdb/duckdb/issues/22088#issuecomment-4261923828) | [source](../upstream-reference/2026-10-28/sources/h19.json) |
| [h20](https://github.com/duckdb/duckdb/issues/22051) | 2026-04-14T04:16:41Z | 2026-04-14T08:45:46Z | needs reproducible example | DinosL | 4.48 | [comment](https://github.com/duckdb/duckdb/issues/22051#issuecomment-4242557883) | [source](../upstream-reference/2026-10-28/sources/h20.json) |
| [h21](https://github.com/duckdb/duckdb/issues/21601) | 2026-03-24T20:23:49Z | 2026-03-25T15:44:59Z | needs reproducible example | Mytherin | 19.35 | [comment](https://github.com/duckdb/duckdb/issues/21601#issuecomment-4127666663) | [source](../upstream-reference/2026-10-28/sources/h21.json) |
| [h22](https://github.com/duckdb/duckdb/issues/20743) | 2026-01-30T05:56:12Z | 2026-02-02T15:25:27Z | needs reproducible example | Mytherin | 81.49 | [comment](https://github.com/duckdb/duckdb/issues/20743#issuecomment-3835850159) | [source](../upstream-reference/2026-10-28/sources/h22.json) |
| [h23](https://github.com/duckdb/duckdb/issues/20255) | 2025-12-18T17:05:22Z | 2025-12-24T09:06:06Z | needs reproducible example | samansmink | 136.01 | [comment](https://github.com/duckdb/duckdb/issues/20255#issuecomment-3689177639) | [source](../upstream-reference/2026-10-28/sources/h23.json) |
| [h24](https://github.com/duckdb/duckdb/issues/13208) | 2024-07-30T14:59:07Z | 2024-07-31T10:45:06Z | needs more info | hannes | 19.77 | - | [source](../upstream-reference/2026-10-28/sources/h24.json) |
| [h25](https://github.com/duckdb/duckdb/issues/12023) | 2024-05-13T08:00:51Z | 2024-05-13T08:40:23Z | needs more info | szarnyasg | 0.66 | - | [source](../upstream-reference/2026-10-28/sources/h25.json) |

## Limitations and interpretation

- Cases were deliberately selected for evaluation, including clarification and
  no-action cases. The 16/25 proportion is not DuckDB's incomplete-report rate.
- The date range describes the earliest/latest selected openings, not continuous
  sampling of all issues over that interval. Snapshots are a later observation.
- Opening-to-label time is not first-response time, working time, or avoidable delay.
  Investigation and unsuccessful reproduction may precede a label.
- Later maintainer findings informed reference labels; the agent only saw openings.
  This measurement is evaluator context and must not enter the agent's issue input.
- No label/comment does not establish that a report was reviewed or complete (h08).
- Six actor accounts do not measure total staffing or overall workload distribution.
- The bot-comment sequence does not prove the bot's trigger code or that every
  template was appropriate. Timestamp ordering alone does not establish causation.
- No actual maintainer time savings, production benefit or model-versus-rule
  advantage was measured. This supports the existence of the task, not its prevalence.

The companion JSON retains unrounded elapsed hours, source hashes, timestamps and
matching comment links. Both files are derived analysis outside the frozen key
and batch manifests; original snapshots, expected outcomes and run evidence remain unchanged.
