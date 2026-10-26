# Findings, 2026-10-24

**Recheck on the 0.13.0 wheel, 2026-10-26.** `run.py` now runs dataprof from
`envs/dataprof013` (Python 3.12, PyPI wheel, 25 MB) instead of the dev build.
All nine dataprof cells give the same verdicts and failed checks as below.
Issue 1 at the end is fixed in 0.13.0 (#1065): the reordered file now scores
key uniqueness 100. The other tools were not rerun.

Versions: dataprof master at 7448871a (0.13 dev; footprint measured on the
0.12.0 wheel), soda-duckdb 4.28.0, pandera 0.34.1, great-expectations 1.24.1,
databricks-labs-dqx 0.17.0 on pyspark 3.5 local + Temurin 17,
ydata-profiling 4.18.4. Python 3.12 for every tool except the dataprof dev
build (3.15). Raw numbers in `results.json`; rerun with `python run.py`.

## Scenario A: the seven rules written by hand

| defect | Soda v4 | pandera | GX | DQX | dataprof |
|---|---|---|---|---|---|
| D1 duplicate order_id | not evaluated | yes | yes | yes | no rule (#904) |
| D2 customer_id nulls | not evaluated | yes | yes | yes | yes |
| D3 negative amount | not evaluated | yes | yes | yes | no rule (#908) |
| D4 status 'shiped' | not evaluated | yes | yes | yes | no rule, no ticket |
| D5 email nulls 2% to 15% | not evaluated | yes | yes | yes | yes |
| D6 added column | yes | yes | yes | yes | no (presence only without a baseline) |
| D7 '12,50' amounts | yes (type) | yes | yes | yes | finding only, gate cannot use it |
| false positives on accepted/clean | none | none | none | none | none |
| user lines (code + config) | 41 | 20 | 26 | 37 | 6 |

Soda: one text value makes `amount` VARCHAR in DuckDB, the batched aggregate
query fails with a binder error, and five unrelated checks are NOT_EVALUATED.
The verdict is still a failure, from the schema check.

DQX: `DQEngine` calls `ws.clusters.select_spark_version()` at construction, so
outside Databricks it needs a mocked WorkspaceClient. A dataset-level failure
(schema) moves every row to the invalid split.

dataprof's 6 lines are short because 4 of the 7 rules cannot be written.

## Scenario B: learn from the accepted file, gate the next ones

| | clean day | today |
|---|---|---|
| dataprof baseline gate (10 lines) | pass | fail: added column, email null increase, score drop |
| pandera `infer_schema` (8 lines) | **fail**: order_id and created_at above the learned max | fail: D2, D3, D7 (+ the same two false positives); misses D1, D4, D5, D6 |
| DQX profiler + generator (11 lines) | **fail**: 4 range rules | fail: D2, D4, D7 + false positives; misses D1, D5, D6 |

- Learned min/max bounds break on monotonic columns (ids, timestamps) every new
  day. dataprof's baseline rules are the only learned gate that passed the
  clean day.
- DQX profiles a 1,000-row sample with no fixed seed: two runs on the same file
  learned different bounds (order_id max 3365, then 3402), and the rules fail
  the very file they were learned from.
- dataprof's score drop on today is real but for the wrong reason: completeness
  98.85 to 62.35 comes from the new optional `coupon_code` (60% empty). With
  that column removed, the score drops 1.92 points and a 5-point score rule
  passes a batch carrying D1, D2, D3, D4 and D7.

## Scenario C: no rules at all

| | today |
|---|---|
| dataprof `findings()` (2 lines) | locale_numbers amount (D7), null_heavy coupon_code |
| ydata-profiling alerts (3 lines) | MISSING email/coupon_code; D1 visible only because `UNIQUE:order_id` disappears |

Neither flags D1, D3, D4. dataprof already computes what D1 and D3 need
(`key_uniqueness` 99.95 on order_id, min -18.94) but no finding reads it. D4
needs value counts the report does not hold.

## Footprint and time

| | packages | MB installed | prerequisites | one run (10k rows) |
|---|---|---|---|---|
| dataprof 0.12.0 | 1 | 24 | none | 0.2 s |
| Soda v4 + DuckDB | 30 | 75 | load the CSV into DuckDB first | 0.9 s |
| pandera | 15 | 107 | pandas | 0.8 s |
| GX | 37 | 275 | pandas | 2.7 s |
| DQX | 31 | 597 | Java 17, Spark, mocked workspace | 9 s |
| ydata-profiling | 56 | 515 | setuptools<80 (imports pkg_resources) | 3.5 s |

Times include interpreter start and imports; DQX includes local Spark start.

## dataprof issues found on the way

1. **Key column chosen by column order.** With no `identifier_columns` hint the
   first id-like name is the key. Putting `customer_id` before `order_id` in
   the accepted file moves the score 99.21 to 96.25 (uniqueness 100 to 80.24):
   a foreign key is scored as the table key. Filed as #1065, fixed in 0.13.0.
2. **Raw accessor float noise**: `report["email"].null_percentage` is
   15.010000000000002 (serialized 15.01).
