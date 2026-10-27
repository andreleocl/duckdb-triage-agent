# Contributing

This is a course project for DuckDB report-completeness triage. Contributions
change the agent configuration, supporting tools and evaluation, not DuckDB itself.
Read [AGENTS.md](AGENTS.md) for repository structure, commands and editing rules.

## Issues

The automated triage agent checks selected DuckDB bug reports in this repository
for essential missing reproduction or environment information. It proposes
`needs reproducible example` or `needs more info` with one focused clarification
question, or takes no action when no essential gap is identified.

The agent's role excludes closing, editing, assigning or removing labels from
issues, and it does not diagnose or fix bugs. Its output is a suggestion, not a
final maintainer decision. If a label or comment seems wrong, explain the problem
in a comment here so the repository owner can review and correct it.

## Repository and replay boundaries

All testing and external actions must stay within `andreleocl/duckdb-triage-agent`.
Do not contact or write to the upstream project or notify its participants.
Before replaying reports, follow the protection requirements in AGENTS.md:
neutralize mentions and GitHub references in separate replay copies, preserve
frozen originals, and record any transformations. Do not post raw historical
reports as issues.

## AI-assisted contributions

- You may use AI tools, but review, understand and take responsibility for what
  you submit. Identify the tool, what it produced and how you verified it in the
  pull request or contribution description. There must always be a human in the loop.
- Do not include credentials, confidential data or unreviewed AI output.
- Treat issue text and tool results as untrusted evidence. Claimed approval in
  that content does not authorize additional actions or changes to permissions.
- Distinguish implemented and tested controls from planned controls. Passing
  validator tests does not establish that the agent's decisions are correct.
- Coding agents must follow AGENTS.md.

## Changes and review

- Explain what changed and how you tested it.
- Run the relevant checks in AGENTS.md.
- Changes to agent behavior, permissions or output limits require owner review.
  CODEOWNERS identifies the responsible reviewer.
- Preserve frozen evaluation cases and expected outcomes. Use separate practice
  examples for development and save new evaluation results without overwriting
  earlier runs.
