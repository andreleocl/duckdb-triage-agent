# Agreed historical manual review

Date: 29 October 2026 (Asia/Singapore).

Andre reviewed and agreed to the case assessments in conversation with Codex.
Codex drafted this record. This is an AI-assisted qualitative review, not an
independent annotation or a completed transcript/safety audit. No SQL was executed.
Later maintainer comments are comparison evidence, not information available to
the opening-only agent. User-supplied comments are attributed as such below.

The frozen historical result remains **19/25 label/action matches (76%)**.
The key, scorer, agent and original run evidence are unchanged. No mismatches
are converted into passes. These notes do not assign new numerical comment scores.

## Six label mismatches

See the [earlier detailed review](2026-10-28-six-label-mismatches.md).
The following clarifications supplement that record.

| Case | Original / sandbox | Agreed assessment |
|---|---|---|
| h08 | [#25395](https://github.com/duckdb/duckdb/issues/25395) / [#43](https://github.com/andreleocl/duckdb-triage-agent/issues/43) | The reproduction request was justified because necessary files were missing. At the recorded upstream snapshot there was no label or maintainer comment. It may not have been reviewed, but silence cannot establish that. The no-action reference is absence of observed action, not a confirmed completeness judgment. |
| h10 | [#25039](https://github.com/duckdb/duckdb/issues/25039) / [#45](https://github.com/andreleocl/duckdb-triage-agent/issues/45) | Environment clarification was defensible. Avoid implying the agent attempted reproduction; reduce the broad diagnostic checklist. Later maintainer testing explains a different information basis for the reproduction label. |
| h11 | [#25011](https://github.com/duckdb/duckdb/issues/25011) / [#46](https://github.com/andreleocl/duckdb-triage-agent/issues/46) | No action was defensible from apparent opening completeness, with uncertainty about the exact frontend/interrupt combination. Do not claim verified reproducibility. |
| h15 | [#22713](https://github.com/duckdb/duckdb/issues/22713) / [#50](https://github.com/andreleocl/duckdb-triage-agent/issues/50) | Useful version-conflict question, matching the maintainer's main concern. The agent's information label differs from the upstream reproduction label. Avoid asserting the version conflict demonstrably blocks reproduction. |
| h20 | [#22051](https://github.com/duckdb/duckdb/issues/22051) / [#55](https://github.com/andreleocl/duckdb-triage-agent/issues/55) | No action is a defensible alternative for a capability/design request, not a confirmed correct decision. The reproduction label had no accompanying explanation of the missing details. A later named-versus-positional-parameter discussion does not establish why that label was applied. The actual agent rationale incorrectly treats placeholder code as sufficient reproduction evidence. |
| h21 | [#21601](https://github.com/duckdb/duckdb/issues/21601) / [#56](https://github.com/andreleocl/duckdb-triage-agent/issues/56) | No action was understandable from the self-contained-looking script. The maintainer said the reproduction did not work and requested a database file plus queries that reproduce it. Apparent completeness does not establish that the script recreates the required database state. The agent must not claim it verified the crash or copy a maintainer's private-sharing offer. |

## Comment review

These judgments supplement the original AI comment notes rather than replacing
run artifacts or the frozen criteria. h15, h20 and h21 are covered above.

| Case | Original / sandbox | Agreed assessment and improvement |
|---|---|---|
| h12 | [#24291](https://github.com/duckdb/duckdb/issues/24291) / [#47](https://github.com/andreleocl/duckdb-triage-agent/issues/47) | Correct reproduction label; useful request for table definition, data and outputs. Minor redundancy in asking again for supplied commands. |
| h13 | [#22776](https://github.com/duckdb/duckdb/issues/22776) / [#48](https://github.com/andreleocl/duckdb-triage-agent/issues/48) | Correct label and useful data request. Explicitly ask for schema and allow a generator for a large-table failure; avoid repeating versions already supplied. A small example is acceptable only if it still fails. |
| h14 | [#22716](https://github.com/duckdb/duckdb/issues/22716) / [#49](https://github.com/andreleocl/duckdb-triage-agent/issues/49) | Correct label and useful Parquet sample/generator request. Do not request the already supplied backtrace. A focused clarification of the enabled-progress-bar setup is reasonable. Do not imply the agent will test locally. |
| h16 | [#22535](https://github.com/duckdb/duckdb/issues/22535) / [#51](https://github.com/andreleocl/duckdb-triage-agent/issues/51) | Correct label and useful schema/index/data request. Acknowledge confidentiality and the supplied deletion sequence. Clarify that any database file must be a shareable example; reduce unexplained extras. The comment did not explicitly demand the whole production database. |
| h17 | [#22468](https://github.com/duckdb/duckdb/issues/22468) / [#52](https://github.com/andreleocl/duckdb-triage-agent/issues/52) | Correct label; missing schemas, source rows and exact failing query justify clarification. Remove repeated version confirmation; any additional backtrace request should be optional and justified. Offer sanitized/generated inputs without credentials. |
| h18 | [#22399](https://github.com/duckdb/duckdb/issues/22399) / [#53](https://github.com/andreleocl/duckdb-triage-agent/issues/53) | Correct label and useful Parquet reproduction request. Acknowledge confidentiality, remove the unexplained traceback request, and do not assert that two files with differing schemas are proven sufficient. |
| h19 | [#22088](https://github.com/duckdb/duckdb/issues/22088) / [#54](https://github.com/andreleocl/duckdb-triage-agent/issues/54) | Correct label and useful missing-schema/data request. Acknowledge the unsuccessful tiny VALUES reduction, permit a larger example/generator, and avoid repeating the supplied error variants. The comment offered CSV as well as VALUES; it did not insist on VALUES only. |
| h22 | [#20743](https://github.com/duckdb/duckdb/issues/20743) / [#57](https://github.com/andreleocl/duckdb-triage-agent/issues/57) | Correct label and useful affected-file/state-recreation alternatives. Acknowledge the unsuccessful fresh-database attempt. Matching table/key names are reasonable because the illustrative query and supplied schema differ. |
| h23 | [#20255](https://github.com/duckdb/duckdb/issues/20255) / [#58](https://github.com/andreleocl/duckdb-triage-agent/issues/58) | Correct label, but the comment misses the full inserted-data/export/read-back sequence and destination definition. It over-focuses on suspected S3 upload errors, repeats the stated use of httpfs, and contains a malformed COPY fragment. Do not treat either reporter or maintainer hypotheses as proven causes. |
| h24 | [#13208](https://github.com/duckdb/duckdb/issues/13208) / [#59](https://github.com/andreleocl/duckdb-triage-agent/issues/59) | Correct information label and useful compiler/linker/build questions, closely matching the maintainer request. Prefer a concise minimal project/build command request; ask where both headers and library came from. A maintainer asking for a reproducible example does not by itself make the information label wrong. |
| h25 | [#12023](https://github.com/duckdb/duckdb/issues/12023) / [#60](https://github.com/andreleocl/duckdb-triage-agent/issues/60) | Correct label; packaging questions are relevant but incomplete, not irrelevant. The comment misses the unclear source version 22 and should ask for a release tag/commit. Its explanation overstates what packaging versions/files establish and assumes a dependency provides package_build rather than allowing a source-path problem. |

## Maintainer context discussed with Andre

Andre supplied or confirmed the following comments during review. These contextual
summaries do not add them to model inputs or amend preserved source snapshots.

- h13: the maintainer could not reproduce and requested a self-contained example with data.
- h14: the maintainer tried TPC-H in place of the unavailable input and could not reproduce.
- h19: the maintainer suggested disabling top_n_window_elimination to narrow the cause.
  This is more targeted troubleshooting, not proof the agent's reproduction request
  was inaccurate or that the maintainer had private context.
- h21: the maintainer requested a database file plus queries that actually reproduce.
  A private-sharing offer belongs to the maintainer, not the sandbox agent.
- h23: the maintainer questioned partial uploads and suspected a different path by
  which NULLs reached the file. This remained a hypothesis requiring reproduction.
- h24: the maintainer asked for exact code, compiler command line and linker flags.
- h25: the maintainer suspected setuptools source copying broke a relative path to
  scripts/package_build.py. This makes packaging questions relevant, but does not
  confirm the cause or remove the need to identify the source revision.

## Points to carry into DESIGN.md

Andre explicitly requested preserving these findings for the design document:

1. **Upstream silence is not a completeness verdict (h08).** A reference derived
   from no observed label/comment can reflect an unreviewed issue; review status
   remains unknown. Report this limitation alongside exact-label agreement.
2. **Expert debugging goes beyond completeness checks (h19).** The agent identified
   missing inputs, while the maintainer proposed a specific optimizer experiment.
   First-pass assistance does not replace domain expertise.
3. **A complete-looking example may not reproduce (h21).** The agent did not execute
   SQL and could not verify that the script recreates the necessary database state.
4. **Separate symptoms from suspected causes (h23).** Request the complete failing
   sequence without adopting a reporter's hypothesis as the investigation target.
5. **Labels, questions and reasoning are separate measures (h15/h20/h24/h25).**
   A reasonable question can receive a different label; a matching label can
   accompany an incomplete comment; a defensible outcome can have weak reasoning.

No new live evaluation or agent refinement is implied by these findings.
Resource-tool deviations remain in the original evidence and are not excused by
this comment review. Adversarial safety and completion remain separately described
in the [adversarial review](2026-10-28-adversarial-safety-and-triage.md).

## Evidence

- [Opening reports](../golden/inputs.jsonl)
- [Upstream reference](../golden/upstream-reference.jsonl)
- [Recorded comments and rationales](../golden/runs/upstream-reference-v2-2026-10-28/batch-e3311e6/historical-summary.json)
- [Historical batch report](../golden/runs/upstream-reference-v2-2026-10-28/batch-e3311e6/report.md)

This note is outside the original batch evidence manifest. It preserves the
chronology of post-run interpretation without rewriting the recorded run.
