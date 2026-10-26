import sys

from common import emit

# >>> user
import dataprof as dp

report = dp.profile(sys.argv[1])
result = report.check(
    max_null_percentage={"customer_id": 0, "email": 7},  # R1, R6
    require_columns=["order_id", "customer_id", "amount", "email", "country", "status", "created_at"],  # R5 (presence only)
)
# R2, R3, R4, R7: no check() keyword today (#904, #908, none, #1025)
# <<< user

emit(result.passed, [f"{c.code}:{c.column}" for c in result.violations + result.unevaluated], result.verdict)
