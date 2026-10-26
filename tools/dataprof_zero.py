import sys

from common import emit

# >>> user
import dataprof as dp

findings = dp.profile(sys.argv[1]).findings()
# <<< user

emit(True, [f"{f.severity}:{f.code}:{f.column}" for f in findings])
