"""Deterministic orders data: an accepted day and a today batch with planted defects.

Planted in today.csv (and absent from accepted.csv):
  D1 key_duplicates   5 order_ids repeat with different other fields (not whole-row dupes)
  D2 key_nulls        30 rows with empty customer_id
  D3 negative_amount  4 rows with amount < 0
  D4 bad_status       15 rows with status 'shiped' (outside the allowed set)
  D5 email_null_jump  email null rate 2% -> ~15%
  D6 added_column     a new column coupon_code
  D7 locale_numbers   40 amounts written '12,50' instead of '12.50'
"""

import csv
import random
from datetime import datetime, timedelta
from pathlib import Path

OUT = Path(__file__).parent / "data"
N = 10_000
STATUSES = ["pending", "paid", "shipped", "cancelled"]
COUNTRIES = ["IT", "DE", "FR", "ES", "US"]


def base_rows(rng, day, email_null_rate, first_id):
    start = datetime.fromisoformat(day)
    rows = []
    for i in range(first_id, first_id + N):
        rows.append(
            {
                "order_id": i,
                "customer_id": rng.randint(1000, 9999),
                "amount": f"{rng.uniform(1, 500):.2f}",
                "email": "" if rng.random() < email_null_rate else f"user{rng.randint(1, 99999)}@example.com",
                "country": rng.choice(COUNTRIES),
                "status": rng.choice(STATUSES),
                "created_at": (start + timedelta(seconds=rng.randint(0, 86_399))).isoformat(),
            }
        )
    return rows


def write(path, rows, fields):
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def main():
    OUT.mkdir(exist_ok=True)
    fields = ["order_id", "customer_id", "amount", "email", "country", "status", "created_at"]

    accepted = base_rows(random.Random(23), "2026-10-20", 0.02, 1)
    write(OUT / "accepted.csv", accepted, fields)

    rng = random.Random(24)
    today = base_rows(rng, "2026-10-21", 0.15, N + 1)  # D5
    picks = rng.sample(range(100, N), 5 + 30 + 4 + 15 + 40)
    dup, nulls, neg, status, locale = picks[:5], picks[5:35], picks[35:39], picks[39:54], picks[54:]
    for k, i in enumerate(dup):  # D1
        today[i]["order_id"] = today[k]["order_id"]
    for i in nulls:  # D2
        today[i]["customer_id"] = ""
    for i in neg:  # D3
        today[i]["amount"] = f"-{rng.uniform(1, 50):.2f}"
    for i in status:  # D4
        today[i]["status"] = "shiped"
    for i in locale:  # D7
        today[i]["amount"] = today[i]["amount"].replace(".", ",")
    for row in today:  # D6
        row["coupon_code"] = rng.choice(["", "", "", "WELCOME10", "BF2026"])
    write(OUT / "today.csv", today, fields + ["coupon_code"])
    # A clean next day: no defects, ids continue. Learned rules must pass it.
    write(OUT / "clean.csv", base_rows(random.Random(25), "2026-10-22", 0.02, 2 * N + 1), fields)
    print("wrote", OUT / "accepted.csv", OUT / "today.csv", OUT / "clean.csv")


if __name__ == "__main__":
    main()
