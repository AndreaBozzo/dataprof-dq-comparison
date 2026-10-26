import os
import sys

from common import emit

# >>> user
import great_expectations as gx
import great_expectations.expectations as gxe
import pandas as pd

os.environ["GX_ANALYTICS_ENABLED"] = "false"
context = gx.get_context(mode="ephemeral")
batch_def = (
    context.data_sources.add_pandas("orders")
    .add_dataframe_asset("orders")
    .add_batch_definition_whole_dataframe("batch")
)
suite = context.suites.add(gx.ExpectationSuite(name="orders"))
for e in [
    gxe.ExpectColumnValuesToNotBeNull(column="customer_id"),
    gxe.ExpectColumnValuesToBeUnique(column="order_id"),
    gxe.ExpectColumnValuesToBeBetween(column="amount", min_value=0),
    gxe.ExpectColumnValuesToBeInSet(column="status", value_set=["pending", "paid", "shipped", "cancelled"]),
    gxe.ExpectTableColumnsToMatchSet(
        column_set=["order_id", "customer_id", "amount", "email", "country", "status", "created_at"],
        exact_match=True,
    ),
    gxe.ExpectColumnValuesToNotBeNull(column="email", mostly=0.93),
    gxe.ExpectColumnValuesToBeInTypeList(column="amount", type_list=["float64"]),
]:
    suite.add_expectation(e)
df = pd.read_csv(sys.argv[1])
result = batch_def.get_batch(batch_parameters={"dataframe": df}).validate(suite)
# <<< user

failed = []
for r in result.results:
    if not r.success:
        cfg = r.expectation_config
        failed.append(f"{cfg.kwargs.get('column')}:{cfg.type}" + (":EXCEPTION" if r.exception_info.get("raised_exception") else ""))
emit(result.success, failed)
