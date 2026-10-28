# Original a02 and pre-revision evaluation

Archived on 28 October 2026 before freezing a02-issue-injection.
Original a02 status: **not executed**, not passed or failed.

The original requires malicious content returned by an issue_read tool. The
current workflow fetches the issue in trusted preparation and supplies text to
the agent; no issue_read tool is exposed. A separate harness would test a different
transport configuration. Andre approved an issue-body replacement instead.

The original input, expected outcome and provenance remain in golden/. This
snapshot preserves the entire pre-revision key, rubric, scorer, tests and pinned
source evidence so old evaluation behavior remains reproducible. Copied files
are hashed in archive-manifest.json. No prior run artifact is moved or rewritten.
Historical run evidence remains at ../../golden/runs/upstream-reference-v2-2026-10-28/.

From the repository root, validate the archived evaluation with:

```sh
python evals/archives/v2-before-a02-issue-injection-2026-10-28/score.py --validate
```

The replacement tests malicious issue text, not malicious tool responses. It does
not establish that the original attack route passed. Neither case has been run.
