import sys

from common import emit

# >>> user
import dataprof as dp

baseline = dp.ProfileReport.load(sys.argv[2])  # saved by the accepted run: report.save("accepted.json")
report = dp.profile(sys.argv[1])
result = report.check(
    baseline=baseline,
    max_null_percentage_increase={"*": 5},
    forbid_removed_columns=True,
    forbid_added_columns=True,
    max_quality_score_drop=5,
)
# <<< user

emit(result.passed, [f"{c.code}:{c.column}" for c in result.violations + result.unevaluated], result.verdict)
