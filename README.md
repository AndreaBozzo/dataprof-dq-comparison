# Same rules, five tools

Local experiment (not part of the dataprof repo). One orders file accepted
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

Run: `python make_data.py && python run.py`.
