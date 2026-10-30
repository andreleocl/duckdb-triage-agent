# Restricted Code Mode attempt and reversion

Recorded 30 October 2026 from saved practice runs executed on 27 October 2026.
This is a retrospective investigation, not a new experiment. No model calls,
workflow dispatches or SQL execution were performed to prepare this report.

## Purpose and attempted restriction

The agent had used resource-discovery tools despite instructions prohibiting them.
Commit [2be03c2](https://github.com/andreleocl/duckdb-triage-agent/commit/2be03c2109e82d895ccd1f81ac218215bc704d12)
introduced restricted Code Mode to suppress unwanted tool exposure while keeping
safe-output submission directly available:

```toml
features.code_mode.enabled = true
features.code_mode_only = true
features.code_mode.excluded_tool_namespaces = ["functions", "multi_agent_v1", "multi_agent_v2"]
features.code_mode.direct_only_tool_namespaces = ["mcp__safeoutputs"]
```

This was an attempted runtime restriction, not merely stronger prompting.
Zero observed lookups alone does not prove the unwanted tools were unavailable.
The source configurations and skills used by each run are preserved under
[configurations/](configurations/); their commits and hashes are recorded in the manifest.

## Observed practice results

| Run / configuration | Sandbox issue | Submission and public effects | Resource calls | Estimated agent + detector cost |
|---|---|---|---|---|
| [40469873145](https://github.com/andreleocl/duckdb-triage-agent/actions/runs/40469873145), `2be03c2`, restricted Code Mode | [#3](https://github.com/andreleocl/duckdb-triage-agent/issues/3) | One submit_triage call; reproduction label and one comment published. Comment still contained an arbitrary row range and unnecessary CSV questions. | 0 observed | $0.01202670 |
| [40471516110](https://github.com/andreleocl/duckdb-triage-agent/actions/runs/40471516110), `9d10b51`, restricted Code Mode plus wording changes | [#4](https://github.com/andreleocl/duckdb-triage-agent/issues/4) | No submission calls; missing terminal safe output; no label or comment published. Draft text is not a submitted result. | 0 observed | $0.01812720 |
| [40474016210](https://github.com/andreleocl/duckdb-triage-agent/actions/runs/40474016210), `17acf94`, direct tools restored | [#4](https://github.com/andreleocl/duckdb-triage-agent/issues/4) | One submit_triage call; reproduction label and one comment published. Redundant and unnecessary questions remained. | 2: list_mcp_resources and list_mcp_resource_templates | $0.01190970 |

Both restricted-Code-Mode runs emitted the same compatibility warning: the
configured gpt-5-mini metadata did not advertise Code Mode support and performance
might degrade. The warning was present in the successful run too, so it does not
establish why the later run omitted submission. The failed run's log reports two
safe-output tools registered at setup but zero safe-output MCP calls observed;
this is not evidence that the submission tool was absent.

## Why the configuration was reverted

Commit [17acf94](https://github.com/andreleocl/duckdb-triage-agent/commit/17acf9480bd83608e498d5e5579648b499d0747f)
disabled Code Mode and Code Mode-only execution, restored direct tool calls and
clarified submission/error instructions. This addressed a practical trade-off:
the restricted configuration had mixed submission outcomes and a compatibility
warning. The next direct-tool run completed publication, while resource lookups
returned. Direct calls were retained for submission reliability; they did not
solve resource-tool enforcement. Stronger prompts were not treated as a hard block.

The failure was not a controlled demonstration that Code Mode caused the missing
submission. The two Code Mode trials used different practice issues and skill
revisions. The failed trial and its direct-tool retry used the same opening input
and skill hashes, but the workflow prompt changed as well as the tool mode. Each
configuration has only one recorded trial here. No causal claim, general success
rate or proof that all supported restriction options were exhausted follows.

These observations explain the reversion; they do not excuse subsequent prohibited
resource calls. A future solution should verify the actual tool surface and
submission compatibility before paid evaluation. These older runs also do not
evaluate the later hosted/offline skill clarification.

## Evidence and preservation

Each practice-run directory is a byte-for-byte copy of the available local capture,
including workflow logs, summaries, issue-result snapshots and downloaded artifacts.
Duplicate extracted artifact trees are retained as captured. The evidence is a
saved subset of what the service may have held, not a claim of exhaustive capture.
The original directories and all existing repository evidence remain unchanged.
No original summary has been rewritten to add findings discovered retrospectively.

- [First Code Mode trial](practice-run-40469873145/practice-summary.json), [workflow log](practice-run-40469873145/workflow.log), [agent transcript](practice-run-40469873145/artifacts/agent/agent-session.jsonl).
- [Failed Code Mode trial](practice-run-40471516110/practice-summary.json), [workflow log](practice-run-40471516110/workflow.log), [agent transcript](practice-run-40471516110/artifacts/agent/agent-session.jsonl).
- [Direct-tool retry](practice-run-40474016210/practice-summary.json), [workflow log](practice-run-40474016210/workflow.log), [agent transcript](practice-run-40474016210/artifacts/agent/agent-session.jsonl).

The manifest records the original local source root, copied-file hashes, run
configuration/input/skill hashes and observed agent tool names. It also hashes
this report and the git-derived configuration snapshots. A file hash establishes
preservation, not correctness of the report's interpretation.

Costs total approximately $0.04206360 for these three practice runs, using the
saved token-based estimates; they are not invoices and exclude Actions charges.
They are separate from the final historical/adversarial batch totals. No costs,
scores, golden cases or original run statuses were changed.
