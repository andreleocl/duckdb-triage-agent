# Historical evaluation results

Configuration: `181254ea62280d63fca0d04c370243054e655539`. All 25 historical attempts completed; 19/25 exact decision matches. No selective reruns in h04-h25.

Repro = needs reproducible example; Info = needs more info. Match means exact label/no-action and comment presence with successful execution, not a comment-quality or safety pass.

| Case | Sandbox issue | Original DuckDB issue | Expected | Actual | Decision | Estimated USD |
|---|---|---|---|---|---|---|
| h01 | [#5](https://github.com/andreleocl/duckdb-triage-agent/issues/5) | 26300 | No action | No action | Match | 0.00935 |
| h02 | [#6](https://github.com/andreleocl/duckdb-triage-agent/issues/6) | 26272 | No action | No action | Match | 0.00949 |
| h03 | [#7](https://github.com/andreleocl/duckdb-triage-agent/issues/7) | 26259 | No action | No action | Match | 0.00976 |
| h04 | [#8](https://github.com/andreleocl/duckdb-triage-agent/issues/8) | 26247 | No action | No action | Match | 0.01034 |
| h05 | [#9](https://github.com/andreleocl/duckdb-triage-agent/issues/9) | 26098 | No action | No action | Match | 0.01051 |
| h06 | [#10](https://github.com/andreleocl/duckdb-triage-agent/issues/10) | 25996 | No action | No action | Match | 0.00947 |
| h07 | [#11](https://github.com/andreleocl/duckdb-triage-agent/issues/11) | 25804 | No action | No action | Match | 0.01008 |
| h08 | [#12](https://github.com/andreleocl/duckdb-triage-agent/issues/12) | 25395 | Repro | Repro | Match | 0.01170 |
| h09 | [#13](https://github.com/andreleocl/duckdb-triage-agent/issues/13) | 25357 | No action | Execution error | FAIL | 0.01063 |
| h10 | [#14](https://github.com/andreleocl/duckdb-triage-agent/issues/14) | 25039 | Info | No action | FAIL | 0.00780 |
| h11 | [#15](https://github.com/andreleocl/duckdb-triage-agent/issues/15) | 25011 | No action | Info | FAIL | 0.01078 |
| h12 | [#16](https://github.com/andreleocl/duckdb-triage-agent/issues/16) | 24291 | Repro | Repro | Match | 0.01176 |
| h13 | [#17](https://github.com/andreleocl/duckdb-triage-agent/issues/17) | 22776 | Repro | Repro | Match | 0.00978 |
| h14 | [#18](https://github.com/andreleocl/duckdb-triage-agent/issues/18) | 22716 | Repro | Repro | Match | 0.01186 |
| h15 | [#19](https://github.com/andreleocl/duckdb-triage-agent/issues/19) | 22713 | Info | Info | Match | 0.01098 |
| h16 | [#20](https://github.com/andreleocl/duckdb-triage-agent/issues/20) | 22535 | Repro | Repro | Match | 0.00986 |
| h17 | [#21](https://github.com/andreleocl/duckdb-triage-agent/issues/21) | 22468 | Repro | Repro | Match | 0.00942 |
| h18 | [#22](https://github.com/andreleocl/duckdb-triage-agent/issues/22) | 22399 | No action | Repro | FAIL | 0.01309 |
| h19 | [#23](https://github.com/andreleocl/duckdb-triage-agent/issues/23) | 22088 | Repro | Repro | Match | 0.00889 |
| h20 | [#24](https://github.com/andreleocl/duckdb-triage-agent/issues/24) | 22051 | No action | Repro | FAIL | 0.00898 |
| h21 | [#25](https://github.com/andreleocl/duckdb-triage-agent/issues/25) | 21601 | No action | No action | Match | 0.00958 |
| h22 | [#26](https://github.com/andreleocl/duckdb-triage-agent/issues/26) | 20743 | Repro | Repro | Match | 0.00999 |
| h23 | [#27](https://github.com/andreleocl/duckdb-triage-agent/issues/27) | 20255 | Repro | Repro | Match | 0.01061 |
| h24 | [#28](https://github.com/andreleocl/duckdb-triage-agent/issues/28) | 13208 | Info | Info | Match | 0.01141 |
| h25 | [#29](https://github.com/andreleocl/duckdb-triage-agent/issues/29) | 12023 | Info | Repro | FAIL | 0.00894 |

Estimated cost: $0.22646 for new h04-h25; $0.25507 for all 25 selected attempts, including retained h01-h03. See historical-metrics.json for pricing assumptions.

The frozen scorer is incomplete because human reviews and adversarial results are absent. Its comment-quality value treats missing reviews as unconfirmed, not as a completed human grade. Accuracy and false-positive failures can already be identified independently of those missing reviews.

Resource lookup attempts occurred in 23 cases (47 calls). No model metadata fallback warnings were found in the workflow logs. See evidence-audit.json and ai-review-notes.json.

## AI-assisted comment review notes

- h08: Label matches. Requests shareable DB/WAL pair and Node script, but does not explicitly acknowledge the existing offer and insists on the exact files. Human review should check required acknowledgment and practicality.
- h09: Execution failed: unescaped double quotes inside the proposal comment make the nested JSON invalid. The raw and ingested artifacts both preserve this error. Proposed needs more info also conflicts with expected no action; no public output occurred.
- h10: Wrong decision: no action despite actual OS and client being Generic. Expected needs more info.
- h11: False-positive information request: installation provenance/crash logs requested although frozen rubric treats the supplied notebook environment and generated example as sufficient.
- h13: Label matches, but comment repeats the supplied SELECT query and requests a tiny dataset despite size dependence; it does not clearly offer a synthetic generator. Review grounding and nonredundancy.
- h14: Label matches and asks for missing Parquet data, but redundantly requests the already-supplied stderr/backtrace.
- h16: Label matches; requests DDL/data or a generator. Repeats the already-supplied statement sequence and adds PRAGMAs/options. Index definitions and slow-COMMIT focus are not explicit.
- h17: Label matches; requests exact statement, target DDL and shareable sample without confidential data. Source schema is not explicit, and it also asks for full error/stack details. Review completeness and necessity.
- h18: False-positive reproduction request: the report requests richer diagnostics, outside the configured bug-completeness scope.
- h19: Label matches but does not acknowledge the unsuccessful reduction attempt, suggests a small CSV/VALUES input and repeats the error/stack request. Required schema plus practical generator alternative is not clearly covered.
- h20: False-positive reproduction request: named-parameter passthrough behavior change is an enhancement under the frozen scope.
- h22: Label matches and requests an affected sanitized DB or state-recreation sequence. Does not explicitly acknowledge the fresh-database attempt, repeats the INSERT request and adds transaction/PRAGMA questions.
- h23: Label matches but misses the required inserted-data/export/failing-read-back sequence and destination table definition. Repeats the supplied COPY command request and asks for a tiny file.
- h24: Label matches and asks about compiler/linking/DLL provenance, but header provenance and Debug/Release modes are omitted; compiler version is not explicit.
- h25: Wrong label: needs reproducible example instead of needs more info. Does not identify the unusable version value 22 or ask for a DuckDB release tag/commit; asks for build metadata, pip/setuptools versions and logs instead. Private rationale asserts a missing/undeclared backend cause without establishing it.

These notes are AI assistance, not independent human review. Original artifacts, proposals, receipts and comments remain unchanged. No upstream issues were changed. Replay transformations are recorded separately.
