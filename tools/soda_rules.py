import os
import sys

from common import emit

HERE = os.path.dirname(os.path.abspath(__file__))
CFG = os.path.join(HERE, "..", "configs", "soda")
os.makedirs(os.path.join(HERE, "..", "work"), exist_ok=True)

# >>> user
import duckdb
from soda_core.contracts import verify_contract_locally

os.environ["SODA_CORE_TELEMETRY_ENABLED"] = "false"
with duckdb.connect("C:/dev/dataprof-dq-comparison/work/orders.duckdb") as con:
    con.execute("CREATE OR REPLACE TABLE orders AS SELECT * FROM read_csv(?)", [sys.argv[1]])

result = verify_contract_locally(
    data_source_file_path=os.path.join(CFG, "ds.yml"),
    contract_file_path=os.path.join(CFG, "contract.yml"),
)
# <<< user

failed = []
for cvr in result.contract_verification_results:
    for cr in cvr.check_results:
        if cr.outcome.name != "PASSED":
            failed.append(f"{cr.outcome.name}:{getattr(cr.check, 'column_name', None)}:{cr.check.type}")
emit(result.is_passed and not result.has_errors, failed, result.get_errors_str()[:400] or None)
