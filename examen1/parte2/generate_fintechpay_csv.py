import argparse
import csv
import os
import random
from datetime import datetime, timedelta, timezone

COUNTRIES = ["CO","MX","AR","CL","PE","BR","US","ES","EC","PA"]
EVENTS = [
    "TX_CREATED","RISK_CHECK","3DS_CHALLENGE","PAYMENT_AUTH","PAYMENT_CAPTURE",
    "SETTLEMENT","REFUND","DISPUTE_OPENED","DISPUTE_CLOSED","TX_UPDATED"
]

def iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).isoformat()

def rand_dt_years(years: int) -> datetime:
    now = datetime.now(timezone.utc)
    start = now - timedelta(days=365*years)
    delta = now - start
    return start + timedelta(seconds=random.randint(0, int(delta.total_seconds())-1))

def write_users(path: str, n: int):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        for uid in range(1, n+1):
            w.writerow([
                uid,
                f"user{uid}@fintechpay.test",
                random.choice(COUNTRIES),
                iso(rand_dt_years(5)),
            ])

def write_transactions(path: str, n_tx: int, n_users: int):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        for tx_id in range(1, n_tx+1):
            r = random.random()
            status = "APPROVED" if r < 0.75 else ("PENDING" if r < 0.90 else ("REJECTED" if r < 0.98 else "CHARGEBACK"))
            w.writerow([
                tx_id,
                random.randint(1, n_users),
                f"{round(random.random()*5000 + 1, 2):.2f}",
                status,
                iso(rand_dt_years(3)),
            ])

def write_audit(path: str, n_logs: int, n_tx: int):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        for i in range(1, n_logs+1):
            w.writerow([
                i,
                random.randint(1, n_tx),
                random.choice(EVENTS),
                iso(rand_dt_years(3)),
            ])

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True, help="Directorio de salida")
    ap.add_argument("--users", type=int, default=2_000_000)
    ap.add_argument("--tx", type=int, default=30_000_000)
    ap.add_argument("--audit", type=int, default=120_000_000)
    args = ap.parse_args()

    os.makedirs(args.out, exist_ok=True)

    print("Writing users.csv ...")
    write_users(os.path.join(args.out, "users.csv"), args.users)

    print("Writing transactions.csv ...")
    write_transactions(os.path.join(args.out, "transactions.csv"), args.tx, args.users)

    print("Writing audit_log.csv ...")
    write_audit(os.path.join(args.out, "audit_log.csv"), args.audit, args.tx)

    print("Done.")

if __name__ == "__main__":
    main()
