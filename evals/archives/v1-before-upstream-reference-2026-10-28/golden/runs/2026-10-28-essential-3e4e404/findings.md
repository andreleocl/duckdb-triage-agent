# Essential-information development retests

Configuration: 3e4e40401f90ce969aacbbbe8c215f8bd5fc040a

| Case | Sandbox issue | Expected | Actual | Decision matches | Estimated USD |
|---|---|---|---|---|---|
| h09 | #30 | No action | No action | True | $0.00828030 |
| h11 | #31 | No action | No action | True | $0.01029200 |
| h18 | #32 | No action | needs reproducible example | False | $0.01244835 |

Estimated total: $0.03102065

h09 and h11 match the frozen no-action expectations. h18 still treats an error-message improvement request as a cast-failure reproduction request and asks for samples, traceback and an already supplied read_parquet call. All are single observations; model reliability is not established.

Triage disabled. h11 attempt 1 was cancelled before jobs/model calls; attempt 2 completed. Original evidence preserved. No code modifications, commits or pushes.

See each case findings.json for token counts, raw submission arguments, observed effects and tool-call counts. Unwanted resource lookups remain. No metadata fallback warnings found in reviewed logs. Human review pending.
