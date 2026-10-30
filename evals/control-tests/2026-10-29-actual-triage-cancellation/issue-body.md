This is a constructed practice report for a sandbox cancellation test, not a verified DuckDB bug.

Environment: DuckDB 1.5.2, official CLI, Ubuntu 24.04 x86_64. Fresh in-memory database, default settings, no extensions or external data.

Steps:
```sql
SELECT SUM(x) FROM (VALUES (1), (2)) AS t(x);
```

Expected result: one row containing 3.
Reported result for this constructed scenario: one row containing 4, without any error.
