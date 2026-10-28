# Same rules, five tools

An experiment outside the [dataprof](https://github.com/AndreaBozzo/dataprof) repo. One orders file accepted
yesterday, one batch today with seven planted defects (see `make_data.py`).
Each tool gets the same job, written the way its docs suggest.

## The rules (scenario A: rules I write)

| id | rule |
|----|------|
| R1 | customer_id has no nulls |
| R2 | order_id is unique |
| R3 | amount >= 0 |
| R4 | status in {pending, paid, shipped, cancelled} |
| R5 | the column set is exactly the agreed seven |
| R6 | email null rate below 7% |
| R7 | amount is numeric |

## Scenario B: learn from the accepted file, gate today

No hand-written thresholds: whatever the tool can derive from yesterday.

## Scenario C: zero config

What the tool says about today with no rules at all.

Code between `# >>> user` and `# <<< user` is what is counted; the rest is the
harness printing a uniform RESULT line.

## Setup

One virtual environment per tool under `envs/`, so their dependencies never
meet. The layout is Windows (`envs/<tool>/Scripts/python.exe`); the versions
are the ones in [FINDINGS.md](FINDINGS.md).

```bash
for spec in "dataprof013 dataprof==0.13.1" "soda soda-duckdb==4.28.0" \
            "pandera pandera==0.34.1" "gx great-expectations==1.24.1" \
            "dqx databricks-labs-dqx==0.17.0 pyspark==3.5.9" "ydata ydata-profiling==4.18.4"; do
  set -- $spec; env=$1; shift
  uv venv --python 3.12 envs/$env && uv pip install --python envs/$env/Scripts/python.exe "$@"
done
```

DQX also needs Java 17 (`JAVA_HOME`, default Temurin 17 under
`C:/Program Files/Eclipse Adoptium`); ydata-profiling needs `setuptools<80`.

Run: `python make_data.py && python run.py`.
