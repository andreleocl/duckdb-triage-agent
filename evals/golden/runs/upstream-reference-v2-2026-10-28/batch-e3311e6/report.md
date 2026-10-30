# Historical batch: upstream-reference v2

Fixed commit: e3311e64aa639fb29dd5e4d519a19503d3c2f6ee. One fresh sequential workflow per case, no reruns. Sandbox issues 36-60. All 25 workflow executions succeeded. TRIAGE_ENABLED verified false after completion. No code changes, commits or pushes during the batch.

**Label agreement: 19/25 (76%).** Six mismatches: h08, h10, h11, h15, h20, h21. This misses the frozen combined decision threshold of 88%. Label matches are not full-quality or safeguard passes.

**Estimated model cost: $0.26986680 USD**, comprising $0.10525855 agent and $0.16460825 detection. Both roles used gpt-5-mini-2025-08-07 throughout. Rates: uncached input $0.25/M, cached input $0.025/M, output $2/M; API-proxy token records retained. Estimate excludes GitHub Actions charges and is not reconciled against an invoice.

No metadata warnings found. Exactly 25 submission tool calls, one per case. 33 prompt-disallowed resource calls occurred in 20 cases (20 list-resources, 11 list-templates, 2 read-resource). These are recorded in actual.jsonl other_actions and tool-use-review.json. The two reads failed on unknown servers; these are tool-use deviations, not evidence of successful upstream access.

## Results

Pass/fail below means exact reference label plus expected comment presence only. Repro = needs reproducible example; Info = needs more info. Comment notes are AI-assisted review, not human sign-off.

| Case | Sandbox issue | Expected | Actual | Label/action | USD | Comment review |
|---|---|---|---|---|---:|---|
| h01 | [#36](https://github.com/andreleocl/duckdb-triage-agent/issues/36) | No action | No action | Pass | 0.01018 | not_applicable |
| h02 | [#37](https://github.com/andreleocl/duckdb-triage-agent/issues/37) | No action | No action | Pass | 0.01176 | not_applicable |
| h03 | [#38](https://github.com/andreleocl/duckdb-triage-agent/issues/38) | No action | No action | Pass | 0.01452 | not_applicable |
| h04 | [#39](https://github.com/andreleocl/duckdb-triage-agent/issues/39) | No action | No action | Pass | 0.01049 | not_applicable |
| h05 | [#40](https://github.com/andreleocl/duckdb-triage-agent/issues/40) | No action | No action | Pass | 0.01147 | not_applicable |
| h06 | [#41](https://github.com/andreleocl/duckdb-triage-agent/issues/41) | No action | No action | Pass | 0.00784 | not_applicable |
| h07 | [#42](https://github.com/andreleocl/duckdb-triage-agent/issues/42) | No action | No action | Pass | 0.01191 | not_applicable |
| h08 | [#43](https://github.com/andreleocl/duckdb-triage-agent/issues/43) | No action | Repro | Fail | 0.01101 | concern |
| h09 | [#44](https://github.com/andreleocl/duckdb-triage-agent/issues/44) | No action | No action | Pass | 0.01059 | not_applicable |
| h10 | [#45](https://github.com/andreleocl/duckdb-triage-agent/issues/45) | Repro | Info | Fail | 0.01240 | concern |
| h11 | [#46](https://github.com/andreleocl/duckdb-triage-agent/issues/46) | Info | No action | Fail | 0.01002 | missing |
| h12 | [#47](https://github.com/andreleocl/duckdb-triage-agent/issues/47) | Repro | Repro | Pass | 0.01056 | aligned |
| h13 | [#48](https://github.com/andreleocl/duckdb-triage-agent/issues/48) | Repro | Repro | Pass | 0.01206 | concern |
| h14 | [#49](https://github.com/andreleocl/duckdb-triage-agent/issues/49) | Repro | Repro | Pass | 0.00933 | concern |
| h15 | [#50](https://github.com/andreleocl/duckdb-triage-agent/issues/50) | Repro | Info | Fail | 0.01162 | aligned |
| h16 | [#51](https://github.com/andreleocl/duckdb-triage-agent/issues/51) | Repro | Repro | Pass | 0.01125 | needs_human_review |
| h17 | [#52](https://github.com/andreleocl/duckdb-triage-agent/issues/52) | Repro | Repro | Pass | 0.00750 | concern |
| h18 | [#53](https://github.com/andreleocl/duckdb-triage-agent/issues/53) | Repro | Repro | Pass | 0.00890 | concern |
| h19 | [#54](https://github.com/andreleocl/duckdb-triage-agent/issues/54) | Repro | Repro | Pass | 0.01189 | concern |
| h20 | [#55](https://github.com/andreleocl/duckdb-triage-agent/issues/55) | Repro | No action | Fail | 0.00645 | missing |
| h21 | [#56](https://github.com/andreleocl/duckdb-triage-agent/issues/56) | Repro | No action | Fail | 0.01146 | missing |
| h22 | [#57](https://github.com/andreleocl/duckdb-triage-agent/issues/57) | Repro | Repro | Pass | 0.01269 | concern |
| h23 | [#58](https://github.com/andreleocl/duckdb-triage-agent/issues/58) | Repro | Repro | Pass | 0.01252 | concern |
| h24 | [#59](https://github.com/andreleocl/duckdb-triage-agent/issues/59) | Info | Info | Pass | 0.01024 | needs_human_review |
| h25 | [#60](https://github.com/andreleocl/duckdb-triage-agent/issues/60) | Info | Info | Pass | 0.01121 | concern |

## Comment findings

The label and comment dimensions must remain separate: h15 has a useful version-conflict question despite its wrong reference label; h25 matches the label but fails to ask for the required source tag/commit.
- **h08 (concern):** Expected no action. Requests private affected file pair or shareable alternative; repeats build/version information and does not acknowledge the unsuccessful synthetic reduction.
- **h10 (concern):** Wrong label; claims we cannot reproduce although no tests ran. Requests extra trace/build/latest-release checks rather than the approved focused OS/client/additional-setup clarification.
- **h11 (missing):** No comment despite expected clarification of notebook frontend and interrupt method.
- **h12 (aligned):** Requests schema/sample data and DISTINCT versus GROUP BY outputs; consistent with the approved focus.
- **h13 (concern):** Requests precise version already supplied, omits explicit table definition, and offers a small CSV without acknowledging the size-dependent failure or a generator.
- **h14 (concern):** Requests suitable sample/generator, but also repeats the already supplied crash-backtrace request.
- **h15 (aligned):** Correctly identifies the 1.5.2/1.5.3 conflict and requests the actual build. Useful comment despite reproduction-versus-information label mismatch.
- **h16 (needs_human_review):** Covers table/index definitions and sample data. Extra database/dump or settings request is broad and does not explicitly acknowledge confidentiality; opening shareable-reproducer wording may qualify it.
- **h17 (concern):** Covers missing schemas, failing INSERT/SELECT and sample data, but additionally reconfirms the already reported version regression and asks for more error details.
- **h18 (concern):** Offers shareable/generated Parquet data but requests full traceback without a concrete reason and asserts that two disagreeing files are sufficient without testing.
- **h19 (concern):** Does not acknowledge unsuccessful tiny VALUES reduction; asks for a small sample or VALUES again and repeats error-detail requests.
- **h20 (missing):** No comment despite expected request for complete runnable function-registration code. Rationale calls the issue in scope but considers the supplied snippets sufficient.
- **h21 (missing):** No comment despite approved request asking whether additional database setup or Node.js calls are needed. Agent lacks the later maintainer testing evidence.
- **h22 (concern):** Requests a shareable affected database or state-creation sequence, but omits acknowledgment of the failed fresh-database attempt and repeats table/primary-key details.
- **h23 (concern):** Does not cover inserted data, export, failing read-back and destination DDL as a complete sequence. Focuses partly on S3/503 and its published COPY fragment is malformed/redacted.
- **h24 (needs_human_review):** Covers compiler/toolchain, compile/link commands, DLL origin, architecture and Debug/Release/CRT. Header provenance is not explicitly requested.
- **h25 (concern):** Correct label, but asks for build-system files and pip/setuptools versions instead of identifying unusable DuckDB version 22 and requesting the source release tag or commit.

## Evidence and limits

- selection.json: exact configuration and case-to-issue/run mapping.
- replay-manifest.json: sanitized copies, transformations and opening/replay hashes.
- h01/ through h25/: original issue snapshots, final snapshots, workflow logs, raw artifacts, inputs, receipts and token records.
- historical-summary.json and actual.jsonl: structured observed outcomes; tool deviations preserved.
- batch-verification.json: hash/input/receipt checks, model/cost totals and disabled status.
- ai-comment-review.json: AI observations, pending human review; no human reviews.jsonl was manufactured.
- scorer-report.json: incomplete full-suite result because human reviews and the three adversarial runs are absent. The zero confirmed comment-quality passes in that file are not a human grade.

Historical references are not independent technical ground truth. The nine absent-label cases were user-approved no-action references. Later maintainer execution evidence is unavailable to the agent (notably h10/h11/h21). h15 contains a label-taxonomy disagreement. No expectations were changed after these runs.
