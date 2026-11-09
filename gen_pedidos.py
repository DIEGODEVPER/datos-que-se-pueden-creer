"""Agrega las tablas de pedidos (ficticias) a meridiano.db.
Los pedidos se trasladaron completos; los clientes no: eso produce huérfanos en el destino.
Ejecutar DESPUÉS de gen_datos.py."""
import sqlite3, random, datetime as dt
rnd = random.Random(11)
con = sqlite3.connect("meridiano.db")
ids = [r[0] for r in con.execute("SELECT id_cliente FROM origen_cliente")]
pedidos = []
for n in range(1, 20001):
    c = rnd.choice(ids)
    f = dt.date(2025, 1, 1) + dt.timedelta(days=rnd.randint(0, 670))
    pedidos.append((n, c, round(rnd.uniform(20, 900), 2), f.isoformat()))
for t in ("origen_pedido", "destino_pedido"):
    con.execute(f"DROP TABLE IF EXISTS {t}")
    con.execute(f"CREATE TABLE {t} (id_pedido INTEGER, id_cliente INTEGER, monto REAL, fecha TEXT)")
    con.executemany(f"INSERT INTO {t} VALUES (?,?,?,?)", pedidos)
con.commit()
for t in ("origen_pedido", "destino_pedido"):
    print(t, con.execute(f"SELECT COUNT(*), ROUND(SUM(monto),2) FROM {t}").fetchone())
