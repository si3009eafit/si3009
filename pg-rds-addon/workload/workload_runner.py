"""
workload_runner.py — Workload OLTP simple para medir TPS y trade-offs (PostgreSQL / RDS)

Qué hace:
- Inserta órdenes y payments para un conjunto de clientes aleatorios
- Ejecuta una consulta tipo dashboard (últimas órdenes) entre inserciones
- Reporta TPS aproximado y latencias promedio

Requisitos:
  pip install psycopg[binary]

Uso:
  python workload_runner.py --host <endpoint> --db labdb --user labuser --password ... --n 10000 --concurrency 4

Notas:
- Para una comparación justa: ejecuta en 3 escenarios (sin índices extra / con FKs / con todo).
- Ejecuta ANALYZE después de grandes cargas.
"""
import argparse, random, time
from concurrent.futures import ThreadPoolExecutor, as_completed

import psycopg

def place_order(conn, order_id, customer_id, n_products, n_items=4):
    # Inserta 1 orden + n_items order_item + 1 pago
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO orders(order_id, customer_id, order_date, status, total_amount) "
            "VALUES (%s, %s, now() - (random()* interval '365 days'), %s, %s)",
            (order_id, customer_id, "PAID", round(random.random()*800+10, 2)),
        )
        # items
        for k in range(n_items):
            item_id = order_id * 10 + k
            product_id = random.randint(1, n_products)
            qty = random.randint(1, 4)
            unit = round(random.random()*400+5, 2)
            cur.execute(
                "INSERT INTO order_item(order_item_id, order_id, product_id, quantity, unit_price) "
                "VALUES (%s,%s,%s,%s,%s)",
                (item_id, order_id, product_id, qty, unit),
            )
        # payment
        cur.execute(
            "INSERT INTO payment(payment_id, order_id, payment_date, payment_method, payment_status) "
            "VALUES (%s,%s, now(), %s, %s)",
            (order_id, order_id, "CARD", "APPROVED"),
        )

def dashboard(conn, customer_id):
    with conn.cursor() as cur:
        cur.execute(
            "SELECT order_id, order_date, status, total_amount "
            "FROM orders WHERE customer_id=%s ORDER BY order_date DESC LIMIT 20",
            (customer_id,),
        )
        cur.fetchall()

def worker(dsn, start_order_id, n_ops, n_customers, n_products):
    lat = []
    with psycopg.connect(dsn, autocommit=False) as conn:
        for i in range(n_ops):
            oid = start_order_id + i
            cid = random.randint(1, n_customers)
            t0 = time.perf_counter()
            place_order(conn, oid, cid, n_products)
            # lectura (dashboard) cada 10 operaciones
            if i % 10 == 0:
                dashboard(conn, cid)
            conn.commit()
            lat.append(time.perf_counter() - t0)
    return lat

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", required=True)
    ap.add_argument("--port", type=int, default=5432)
    ap.add_argument("--db", required=True)
    ap.add_argument("--user", required=True)
    ap.add_argument("--password", required=True)
    ap.add_argument("--n", type=int, default=10000, help="Número total de órdenes (operaciones)")
    ap.add_argument("--concurrency", type=int, default=4)
    ap.add_argument("--customers", type=int, default=200000)
    ap.add_argument("--products", type=int, default=20000)
    ap.add_argument("--order_id_base", type=int, default=900000000, help="Evitar colisiones con dataset cargado")
    args = ap.parse_args()

    dsn = f"host={args.host} port={args.port} dbname={args.db} user={args.user} password={args.password} sslmode=require"

    per_worker = args.n // args.concurrency
    extras = args.n % args.concurrency

    t0 = time.perf_counter()
    futures = []
    with ThreadPoolExecutor(max_workers=args.concurrency) as ex:
        base = args.order_id_base
        for w in range(args.concurrency):
            n_ops = per_worker + (1 if w < extras else 0)
            futures.append(ex.submit(worker, dsn, base + w*10_000_000, n_ops, args.customers, args.products))
        all_lat = []
        for fu in as_completed(futures):
            all_lat.extend(fu.result())
    elapsed = time.perf_counter() - t0

    if not all_lat:
        print("No operations executed.")
        return

    all_lat.sort()
    mean = sum(all_lat)/len(all_lat)
    p95 = all_lat[int(0.95*len(all_lat))-1]
    tps = len(all_lat)/elapsed

    print(f"Ops: {len(all_lat)}  Concurrency: {args.concurrency}")
    print(f"Elapsed: {elapsed:.2f}s  TPS: {tps:.2f}")
    print(f"Latency mean: {mean*1000:.2f} ms  p95: {p95*1000:.2f} ms")

if __name__ == "__main__":
    main()
