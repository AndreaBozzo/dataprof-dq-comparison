import sys

from common import emit

# >>> user
import pandas as pd
import pandera.pandas as pa

schema = pa.DataFrameSchema(
    {
        "order_id": pa.Column(int, unique=True),
        "customer_id": pa.Column(int, nullable=False),
        "amount": pa.Column(float, pa.Check.ge(0)),
        "email": pa.Column(str, pa.Check(lambda s: s.isna().mean() < 0.07, ignore_na=False), nullable=True),
        "country": pa.Column(str),
        "status": pa.Column(str, pa.Check.isin(["pending", "paid", "shipped", "cancelled"])),
        "created_at": pa.Column(pa.DateTime),
    },
    strict=True,
)
df = pd.read_csv(sys.argv[1], parse_dates=["created_at"])
try:
    schema.validate(df, lazy=True)
    errors = None
except pa.errors.SchemaErrors as e:
    errors = e.failure_cases
# <<< user

if errors is None:
    emit(True, [])
else:
    emit(False, [f"{r.column}:{r.check}" for r in errors[["column", "check"]].drop_duplicates().itertuples()])
