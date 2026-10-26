import os
import sys

from common import emit

HERE = os.path.dirname(os.path.abspath(__file__))

# >>> user
from unittest.mock import MagicMock  # DQEngine pings a Databricks workspace on construction

import yaml
from databricks.labs.dqx.engine import DQEngine
from pyspark.sql import SparkSession

spark = SparkSession.builder.master("local[2]").getOrCreate()
df = spark.read.csv(sys.argv[1], header=True, inferSchema=True)
checks = yaml.safe_load(open(os.path.join(HERE, "..", "configs", "dqx", "checks.yml")))
engine = DQEngine(MagicMock(), spark)
valid, invalid = engine.apply_checks_by_metadata_and_split(df, checks)
# <<< user

rows = invalid.select("_errors").collect()
names = {e["name"] for r in rows for e in (r["_errors"] or [])}
emit(not names, names, f"{len(rows)} invalid rows")
