# Manual review of six historical label mismatches

Date: 28 October 2026 (Asia/Singapore).

This note records the opening-text review discussed by Andre and Codex after the
25-case run. Codex drafted the assessments and this summary; Andre requested that
the discussion be documented. This is AI-assisted qualitative review, not an
independent human annotation or completed human transcript/safety review.

## Evaluation and evidence boundary

- Evaluation: upstream-reference-v2-2026-10-28.
- Configuration: e3311e64aa639fb29dd5e4d519a19503d3c2f6ee.
- Batch: [batch-e3311e6](../golden/runs/upstream-reference-v2-2026-10-28/batch-e3311e6/report.md).
- Frozen label/action agreement remains **19/25 (76%)**. h08, h10, h11, h15, h20 and h21 remain mismatches.
- Frozen inputs, key, rubric, thresholds, scorer and original run evidence are unchanged.
- This post-run interpretation does not create replacement expectations, convert mismatches into passes, or establish technical correctness.
- No reported SQL was executed. Later maintainer findings are context for the comparison, not evidence the triage agent possessed.
- Comment quality and reasoning quality are distinct from label agreement. No-action means no public label/comment, not verified reproducibility.

The review asks whether each decision was reasonable given the opening report and
the configured scope. The observed agent rationale is distinguished from a better
justification identified during review. Existing resource-tool violations and other
batch findings remain recorded; this note is not a safeguard pass.

## Case assessments

| Case | Sandbox / original | Frozen expectation | Agent action | Opening-text assessment | Comment or rationale improvement |
|---|---|---|---|---|---|
| h08 | [Sandbox #43](https://github.com/andreleocl/duckdb-triage-agent/issues/43) / [Original #25395](https://github.com/duckdb/duckdb/issues/25395) | No action | needs reproducible example | Justified: the affected database/WAL pair and Node script were offered but not attached; the attempted synthetic reproduction did not fail. | Acknowledge the unsuccessful reduction, request the offered script and files safe to share, avoid asking again for the supplied DuckDB version without a reason, and avoid promising successful reproduction. |
| h10 | [Sandbox #45](https://github.com/andreleocl/duckdb-triage-agent/issues/45) / [Original #25039](https://github.com/duckdb/duckdb/issues/25039) | needs reproducible example | needs more info | Defensible from the opening: SQL and data are supplied, but OS and client are both Generic. The maintainer's reproduction label reflects later testing. | Ask specifically for OS/client and any additional setup. Do not imply testing with "we can't reproduce." Avoid treating backtrace, exact build, latest-release testing and other debugging details as automatically essential. |
| h11 | [Sandbox #46](https://github.com/andreleocl/duckdb-triage-agent/issues/46) / [Original #25011](https://github.com/duckdb/duckdb/issues/25011) | needs more info | No action | Defensible with ambiguity: generated data, code, versions and interrupt instructions are supplied. Several frontend/interrupt alternatives leave the exact failing combination unclear. | No public comment. The rationale should acknowledge uncertainty instead of asserting all essential details are certainly present. A narrow question identifying the failing frontend/interrupt combination would also be reasonable, but is not proven essential solely by the opening. |
| h15 | [Sandbox #50](https://github.com/andreleocl/duckdb-triage-agent/issues/50) / [Original #22713](https://github.com/duckdb/duckdb/issues/22713) | needs reproducible example | needs more info | Justified under the agent's label definitions: the SQL is supplied but versions conflict. This is a difference in label usage. | The comment usefully identifies 1.5.2 versus 1.5.3 and asks which build produced the error. Its main question matches the approved comment focus despite the label mismatch. |
| h20 | [Sandbox #55](https://github.com/andreleocl/duckdb-triage-agent/issues/55) / [Original #22051](https://github.com/duckdb/duckdb/issues/22051) | needs reproducible example | No action | Outcome defensible under the enhancement exclusion: the report requests arbitrary named-parameter forwarding without establishing that this previously worked or regressed. | No public comment. The actual rationale is weak: it calls this an in-scope failure and treats placeholder snippets as sufficient. Enhancement exclusion is a stronger post-review justification, not the reason actually given by the agent. |
| h21 | [Sandbox #56](https://github.com/andreleocl/duckdb-triage-agent/issues/56) / [Original #21601](https://github.com/duckdb/duckdb/issues/21601) | needs reproducible example | No action | Justified as first-pass reading: self-contained-looking SQL, generated data, environment and error details are supplied. The maintainer's later finding that it did not reproduce was unavailable to the agent. | No public comment. Say no specific missing dependency is evident from the supplied text; do not imply that reproducibility was verified. |

## Important distinctions

### h08: no upstream label is not a completeness verdict

The opening explicitly offers the database/WAL pair and Node script on request.
The agent can reasonably ask for those missing materials. An absent target label
does not establish whether a maintainer reviewed the issue or whether clarification
was unnecessary. We do not know that the issue was unreviewed.

The separate node-duckdb package version is not explicitly supplied, unlike DuckDB
1.4.4 and Node 20.20.2. That question is not simply a duplicate, but the agent still
needs a reason to treat it as essential. Asking for a shareable alternative is
useful; the request for the exact affected files should explicitly respect privacy.

### h10 and h21: apparent completeness versus tested reproduction

For h10, the maintainer reported that the SQL did not crash with their v1.5.5 build
or the publicly distributed spatial extension. For h21, the maintainer explicitly
said the reproduction did not work and requested a corrected example. Those are
reasonable bases for reproduction labels after testing. The opening-only agent
was prohibited from performing that testing. Different information can support
different triage decisions without proving either side careless.

h10's agent still has a comment problem: "we can't reproduce" implies a finding
that the agent did not establish. OS/client clarification is more focused than
its broad debugging checklist.

### h11: use the whole report, not just the Client field

The opening prose already identifies Jupyter/ipykernel and names VS Code and
JupyterLab. Asking for notebook details merely because the Client field says
Python would repeat existing information. Identifying which listed frontend and
interrupt method produced the actual crash is a narrower, defensible clarification.
Later maintainer testing found the script difficult to interrupt, but that finding
was not in the agent's input.

### h15: a useful question can have a different label

The agent correctly asks which conflicting DuckDB version produced the error.
The upstream reproduction label and the agent's information label express different
category choices for a similar clarification. The frozen exact-label metric must
still count the mismatch; comment quality should be assessed separately.

### h20: a reasonable outcome does not validate the rationale

The report asks to change named-parameter validation for a passthrough capability.
The enhancement exclusion supports no action without deciding whether the proposed
implementation is technically correct. The agent instead classified it in scope.
Its C++ example contains placeholders, so understanding the request does not prove
that the snippets form a runnable reproducer. The review does not retroactively
attribute the scope-exclusion reasoning to the model.

## Interpretation

All six public outcomes have a defensible basis in this review, with differing
strengths and limitations. That is not a claim that every rationale or comment is
correct. h08 and h10 have concrete comment improvements; h15's central question is
useful; h11/h20/h21 posted no comment, so their issues concern judgment or private
reasoning instead of public wording.

Keep the original six mismatches visible alongside this qualitative explanation.
Do not report a revised 25/25 score, a completed human review, or a full-suite pass.
The independent comment-quality concerns in other cases and the batch's tool-use
violations are outside this six-case review and remain unresolved.

## Local evidence

- [Opening reports](../golden/inputs.jsonl)
- [Frozen upstream reference and maintainer evidence](../golden/upstream-reference.jsonl)
- [Observed outcomes, comments and rationales](../golden/runs/upstream-reference-v2-2026-10-28/batch-e3311e6/historical-summary.json)
- [Original scorer report](../golden/runs/upstream-reference-v2-2026-10-28/batch-e3311e6/scorer-report.json)
- [Original AI comment review](../golden/runs/upstream-reference-v2-2026-10-28/batch-e3311e6/ai-comment-review.json)
- [Tool-use review](../golden/runs/upstream-reference-v2-2026-10-28/batch-e3311e6/tool-use-review.json)

This standalone note was added after the batch evidence manifest was created.
It does not replace or alter that manifest or any recorded run artifact.

## Follow-up review

See the [29 October agreed review](2026-10-29-agreed-historical-review.md) for
Andre's subsequent case-by-case approvals, the explicit h08 absence-of-action
limitation, h20 intent uncertainty, h21 database-state context, comment assessments
and points to carry into DESIGN.md. The frozen 19/25 result is unchanged.
