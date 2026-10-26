import sys

from common import emit

# >>> user
import pandas as pd
import pandera.pandas as pa

schema = pa.infer_schema(pd.read_csv(sys.argv[2], parse_dates=["created_at"]))  # usually saved: schema.to_yaml()
try:
    schema.validate(pd.read_csv(sys.argv[1], parse_dates=["created_at"]), lazy=True)
    errors = None
except pa.errors.SchemaErrors as e:
    errors = e.failure_cases
# <<< user

if errors is None:
    emit(True, [])
else:
    emit(False, [f"{r.column}:{r.check}" for r in errors[["column", "check"]].drop_duplicates().itertuples()])
