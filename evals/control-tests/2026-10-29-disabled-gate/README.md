# Disabled-start gate test

Date: 29 October 2026. Andre authorized one dispatch with TRIAGE_ENABLED=false.
This control test did not enable triage or change agent code, configuration or frozen cases.

- [Run 40808613147](https://github.com/andreleocl/duckdb-triage-agent/actions/runs/40808613147)
- [Existing practice issue #4](https://github.com/andreleocl/duckdb-triage-agent/issues/4)
- Hosted commit: 1b4a032f912acc8c36ab34f46899174ca59dfdfe.
- Before dispatch, the hosted compiled workflow matched the local file byte-for-byte.
- The repository variable was false before dispatch and remained false afterward.

## Result

**Passed the disabled-start check.** GitHub reported the run as skipped.
All six jobs (pre_activation, activation, agent, detection, submit_triage and
conclusion) were skipped, with zero steps executed. No model invocation or
publication job ran, and no artifacts were produced. Model cost from this run
is $0 based on non-execution; this is not a provider-invoice reconciliation.

Before/after snapshots match for issue title, body, state, labels, assignees,
comment count and updated_at. Full comment lists are identical. No public
label or comment was added by this test.

## Evidence and boundaries

The test plan, hosted lock copy, variable snapshots, run and job API responses,
artifact listing, before/after issue/comments and verification.json are retained
here. The expected result was saved before dispatch. evidence-manifest.json hashes
these records. Skipped jobs have no execution steps to supply model transcripts.

This verifies preventing a new run from reaching inference while already disabled.
It does not test cancelling active work, changing a variable during execution,
phone navigation, or stopping an in-flight provider request. Those limitations
remain. No active-cancellation workflow or malicious-response harness was built.
