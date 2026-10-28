# Scope classification retests

Configuration: 5423c54256baacd824948127614b05eec4a7b563

| Case | Issue | Expected | Actual | Outcome | Estimated USD |
|---|---|---|---|---|---|
| h18 | #33 | No action | error | Fail | $0.01183560 |
| h20 | #34 | No action | no_action | Match | $0.01130270 |

Estimated total: $0.0231383

- h18: Still requests data for the diagnostic enhancement. Publisher rejected > in VARCHAR->NULL; offline no-network reproduction confirms guard failure. No public action. This is an error, not successful no-action.
- h20: No-action outcome matches, but rationale calls the enhancement an in-scope binder failure. Outcome success does not demonstrate correct scope classification.

Updated scope rule confirmed in both prompts. See per-case findings.json for model IDs, token usage, tool calls, submission arguments and warning checks. Human review pending.

Triage disabled after both publisher jobs finished. Original evidence preserved. No code changes, commits or pushes.
