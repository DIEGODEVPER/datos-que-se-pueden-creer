"""Genera datos sintéticos de Grupo Meridiano (ficticios) con defectos conocidos.
Crea meridiano.db (SQLite) con: origen_cliente, destino_cliente."""
import sqlite3, random, datetime as dt, os
random.seed(2026)
HOY = dt.date(2026, 11, 2)
N = 10000
NOMBRES = ["María","José","Luis","Carmen","Juan","Rosa","Carlos","Ana","Pedro","Lucía","Miguel","Elena","Jorge","Sofía","Víctor","Patricia"]
APELL = ["Quispe","Flores","Rojas","Huamán","Torres","Vargas","Mendoza","Castillo","Ramos","Paredes","Salazar","Chávez","Cruz","Díaz"]
def fecha(a, b): return a + dt.timedelta(days=random.randint(0, (b - a).days))
filas = []
for i in range(1, N + 1):
    alta = fecha(dt.date(2019, 1, 1), HOY)
    nuevo = alta >= HOY - dt.timedelta(days=365)
    nac = fecha(dt.date(1950, 1, 1), dt.date(2003, 12, 31)).isoformat()
    # defecto: fecha de nacimiento vacía o 1900-01-01
    p = 0.38 if nuevo else 0.02
    r = random.random()
    if r < p: nac = None if random.random() < 0.5 else "1900-01-01"
    nombre = f"{random.choice(NOMBRES)} {random.choice(APELL)} {random.choice(APELL)}"
    doc = f"{random.randint(10000000, 79999999)}"
    mail = f"{nombre.split()[0].lower()}{i}@correo.pe" if random.random() > 0.06 else random.choice([f"{nombre.split()[0].lower()}{i}correo.pe", f"{i}@", ""])
    ult_compra = fecha(HOY - dt.timedelta(days=800), HOY)
    ult_pago = ult_compra + dt.timedelta(days=random.randint(0, 120))
    if ult_pago > HOY: ult_pago = None
    estado = random.choices(["AL_DIA", "MORA_30", "MORA_90"], [0.8, 0.14, 0.06])[0]
    filas.append([i, nombre, doc, mail, nac, alta.isoformat(), ult_compra.isoformat(), ult_pago.isoformat() if ult_pago else None, estado])
# defecto: duplicados (4,1 %) con el nombre escrito de otra forma
dup = random.sample(range(N), int(N * 0.041))
sig = N + 1
for k in dup:
    f = filas[k][:]
    f[0] = sig; sig += 1
    f[1] = f[1].upper().replace("Á","A").replace("É","E").replace("Í","I").replace("Ó","O").replace("Ú","U")
    filas.append(f)
random.shuffle(filas)
# defecto: documento de identidad vacío en el 3 % de los clientes (solo en filas sin duplicado,
# con un generador aparte para no alterar el resto de las cifras)
from collections import Counter
cuenta = Counter(f[2] for f in filas)
candidatas = [i for i, f in enumerate(filas) if cuenta[f[2]] == 1]
for i in random.Random(5).sample(candidatas, round(len(filas) * 0.03)):
    filas[i][2] = None
if os.path.exists("meridiano.db"): os.remove("meridiano.db")
con = sqlite3.connect("meridiano.db")
cols = "id_cliente INTEGER, nombre TEXT, documento TEXT, email TEXT, fecha_nacimiento TEXT, fecha_alta TEXT, ultima_compra TEXT, ultimo_pago TEXT, estado_fin TEXT"
con.execute(f"CREATE TABLE origen_cliente ({cols})")
con.executemany("INSERT INTO origen_cliente VALUES (?,?,?,?,?,?,?,?,?)", filas)
# destino: traslado con defectos (pérdida de filas, truncado de nombre, estado_fin congelado)
con.execute(f"CREATE TABLE destino_cliente ({cols})")
destino = []
perdidas = set(random.sample(range(len(filas)), 31))
for idx, f in enumerate(filas):
    if idx in perdidas: continue
    g = f[:]
    g[1] = g[1][:24]                       # nombre truncado a 24 caracteres
    if random.random() < 0.07:             # el disparador no se movió: el estado queda congelado
        g[8] = "AL_DIA" if g[8] != "AL_DIA" else "MORA_30"
    destino.append(g)
con.executemany("INSERT INTO destino_cliente VALUES (?,?,?,?,?,?,?,?,?)", destino)
con.commit()
for t in ("origen_cliente", "destino_cliente"):
    print(t, con.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0])
