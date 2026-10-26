import json


def emit(passed, failed, note=None):
    print("RESULT " + json.dumps({"passed": bool(passed), "failed": sorted(set(map(str, failed))), "note": note}))
