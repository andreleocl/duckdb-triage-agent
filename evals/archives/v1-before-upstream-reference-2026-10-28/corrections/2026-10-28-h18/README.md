# h18 answer-key correction ? 28 October 2026

This is a separate retrospective annotation correction authorized by Andre after
reviewing the maintainer evidence, drafted by Codex. It does not rewrite the frozen
golden, original results, scorer, or agent instructions, and is not a new model run.

## Reason and evidence

Case h18 is [Error message on missing column lacks essential details](https://github.com/duckdb/duckdb/issues/22399).
The original expected label was **no action**, based on interpreting the report
solely as a request for richer diagnostics. That interpretation excluded a
reasonable request for a shareable reproducer too confidently.

The user-supplied [maintainer screenshot](maintainer-evidence.png) shows a May 1
reproduction-label event, the corresponding bot template, and a maintainer's own
comment asking the reporter to isolate a minimal case by examining the Parquet
schemas. The label text is truncated in the image; Andre identified it as
`needs reproducible example`. The personal comment independently supports the
reproduction request. This evidence was supplied in chat; no fresh upstream
request was made for this correction. The screenshot hash is in
[comparison.json](comparison.json).

**Corrected expectation for this separate analysis: `needs reproducible example`.**
The report supplies a query and error but no shareable data. Requesting synthetic
or shareable input is reasonable even when the intended improvement concerns
error diagnostics. Confidential data alone neither requires a clarification nor
justifies no action. This correction is a reviewed judgment for this case, not a
rule that all upstream labels become ground truth. The enhancement interpretation
remains a source of ambiguity, and the agent's scope policy is unchanged.

## Original versus corrected result

The [original h18 receipt](../../golden/runs/final-181254e/h18/artifacts/triage-receipt/receipt.json)
records run `40502143512` on configuration
`181254ea62280d63fca0d04c370243054e655539`, with successful publication of one
`needs reproducible example` label and one comment to sandbox issue #22.

| Measure | Original frozen interpretation | Separate corrected interpretation |
|---|---|---|
| Expected h18 label | No action | needs reproducible example |
| Actual original h18 label | needs reproducible example | Same recorded output |
| h18 exact decision match | Fail | Match |
| Original 25-case decision matches | 19/25 (76%) | 20/25 (80%) |
| Comment quality | Requires separate review | Still requires separate review |
| Full evaluation | Incomplete | Still incomplete; not a pass |

The comparison uses the same original 25 attempts in
[actual.jsonl](../../golden/runs/final-181254e/actual.jsonl), changing only the h18
expected label in this separate calculation. A match requires completed execution,
the exact expected label list, and matching comment presence, as in the frozen
scorer. No later retry replaces any original attempt. The calculation and source
hashes are recorded in [comparison.json](comparison.json). Other cases and all
frozen expectations remain unchanged. Running the unchanged scorer still uses the
original golden; the 80% figure is a correction analysis, not its new output.

The revised 80% remains below the frozen 88% accuracy threshold. Human comment
reviews and adversarial evaluation are still missing. This correction does not
establish overall evaluation success or production reliability.

## What this does not excuse

The original comment contains awkward/redacted query wording and asks for a full
traceback. Whether those questions were necessary and clear remains a separate
comment-quality judgment. Recorded prohibited tool calls remain recorded.

The later [publisher-rejected attempt](../../golden/runs/2026-10-28-scope-5423c54/h18/findings.json)
still counts as an execution failure: correcting the intended label does not turn
a rejected submission into successful no action. Its `VARCHAR->NULL` rejection
and the subsequent publisher fix are separate from this answer-key correction.
Other retry findings remain untouched historical records; this note explains the
revised label interpretation rather than silently rewriting their conclusions.

No agent changes, live runs, commits or pushes were performed for this correction.
