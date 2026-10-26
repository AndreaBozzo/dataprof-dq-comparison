import sys

from common import emit

# >>> user
import pandas as pd
from ydata_profiling import ProfileReport

alerts = ProfileReport(pd.read_csv(sys.argv[1]), progress_bar=False).get_description().alerts
# <<< user

emit(True, [f"{a.alert_type.name}:{a.column_name}" for a in alerts])
