import sys

from common import emit

# >>> user
from unittest.mock import MagicMock  # DQEngine pings a Databricks workspace on construction

from databricks.labs.dqx.engine import DQEngine
from databricks.labs.dqx.profiler.generator import DQGenerator
from databricks.labs.dqx.profiler.profiler import DQProfiler
from pyspark.sql import SparkSession

spark = SparkSession.builder.master("local[2]").getOrCreate()
ws = MagicMock()
read = lambda p: spark.read.csv(p, header=True, inferSchema=True)
_, profiles = DQProfiler(ws, spark).profile(read(sys.argv[2]))
checks = DQGenerator(ws, spark).generate_dq_rules(profiles)  # usually saved to YAML
valid, invalid = DQEngine(ws, spark).apply_checks_by_metadata_and_split(read(sys.argv[1]), checks)
# <<< user

rows = invalid.select("_errors").collect()
names = {e["name"] for r in rows for e in (r["_errors"] or [])}
emit(not names, names, f"{len(checks)} rules: " + "; ".join(f"{c['check']['function']}({c['check']['arguments']})" for c in checks)[:900])
