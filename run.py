"""Run every tool on every file, count the user-authored lines, measure the installs."""

import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).parent
TOOLS = ROOT / "tools"
DATA = ROOT / "data"
DP_DEV = ROOT / "envs" / "dataprof013" / "Scripts" / "python.exe"
JAVA_HOME = "C:/Program Files/Eclipse Adoptium/jdk-17.0.20.101-hotspot"

# (tool, scenario, script, env python, config files, needs baseline arg)
RUNS = [
    ("dataprof", "A rules", "dataprof_rules.py", DP_DEV, [], None),
    ("soda", "A rules", "soda_rules.py", "soda", ["configs/soda/ds.yml", "configs/soda/contract.yml"], None),
    ("pandera", "A rules", "pandera_rules.py", "pandera", [], None),
    ("gx", "A rules", "gx_rules.py", "gx", [], None),
    ("dqx", "A rules", "dqx_rules.py", "dqx", ["configs/dqx/checks.yml"], None),
    ("dataprof", "B learned", "dataprof_learned.py", DP_DEV, [], "work/accepted.json"),
    ("pandera", "B learned", "pandera_learned.py", "pandera", [], "data/accepted.csv"),
    ("dqx", "B learned", "dqx_learned.py", "dqx", [], "data/accepted.csv"),
    ("dataprof", "C zero", "dataprof_zero.py", DP_DEV, [], None),
    ("ydata", "C zero", "ydata_zero.py", "ydata", [], None),
]
FILES = ["accepted", "clean", "today"]


def py(env):
    return str(env) if isinstance(env, Path) else str(ROOT / "envs" / env / "Scripts" / "python.exe")


def code_lines(text):
    return [ln for ln in text.splitlines() if ln.strip() and not ln.strip().startswith("#")]


def user_lines(script, configs):
    src = (TOOLS / script).read_text()
    block = re.search(r"# >>> user\n(.*?)# <<< user", src, re.S)
    assert block, script
    n = len(code_lines(block.group(1)))
    return n + sum(len(code_lines((ROOT / c).read_text())) for c in configs)


def footprint(env):
    site = ROOT / "envs" / env / "Lib" / "site-packages"
    dists = [d for d in site.glob("*.dist-info")]
    size = sum(f.stat().st_size for f in site.rglob("*") if f.is_file())
    return {"packages": len(dists), "mb": round(size / 1e6)}


def main():
    subprocess.run([str(DP_DEV), "-c", f"import dataprof as dp; dp.profile(r'{DATA / 'accepted.csv'}').save(r'{ROOT / 'work' / 'accepted.json'}')"], check=True)
    env = dict(os.environ, JAVA_HOME=JAVA_HOME, PYSPARK_PYTHON=py("dqx"), PYTHONIOENCODING="utf-8")
    out = []
    for tool, scenario, script, envname, configs, base in RUNS:
        for f in FILES:
            args = [py(envname), script, str(DATA / f"{f}.csv")] + ([str(ROOT / base)] if base else [])
            t0 = time.perf_counter()
            p = subprocess.run(args, cwd=TOOLS, env=env, capture_output=True, text=True, encoding="utf-8", errors="replace")
            dt = time.perf_counter() - t0
            line = next((ln for ln in p.stdout.splitlines() if ln.startswith("RESULT ")), None)
            res = json.loads(line[7:]) if line else {"passed": None, "failed": [], "note": (p.stderr or p.stdout)[-600:]}
            out.append({"tool": tool, "scenario": scenario, "file": f, "seconds": round(dt, 1), **res})
            print(f"{tool:9} {scenario:10} {f:9} {dt:5.1f}s passed={res['passed']} {res['failed']}", flush=True)
    meta = {
        "lines": {f"{t}|{s}": user_lines(sc, c) for t, s, sc, _, c, _ in RUNS},
        "footprint": {e: footprint(e) for e in ["dataprof013", "soda", "pandera", "gx", "dqx", "ydata"]},
        "python": sys.version,
    }
    (ROOT / "results.json").write_text(json.dumps({"runs": out, "meta": meta}, indent=1))
    print(json.dumps(meta, indent=1))


if __name__ == "__main__":
    main()
