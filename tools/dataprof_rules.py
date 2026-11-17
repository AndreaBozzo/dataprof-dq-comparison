import sys

from common import emit

# >>> user
import dataprof as dp

report = dp.profile(sys.argv[1])
result = report.check(
    max_null_count={"customer_id": 0},  # R1, exact count
    unique_columns=["order_id"],  # R2
    max_null_percentage={"email": 7},  # R6
    require_columns=["order_id", "customer_id", "amount", "email", "country", "status", "created_at"],  # R5 (presence only)
    forbid_findings=["locale_numbers"],  # R7 through the finding; no type rule (#1025)
)
# R3, R4: no check() keyword today (#908, none)
# <<< user

emit(result.passed, [f"{c.code}:{c.column}" for c in result.violations + result.unevaluated], result.verdict)
