"""Conciliación por bloques: cuando la tabla es muy grande, se compara una huella por bloque de claves y columna,
y solo se baja al detalle en los bloques cuya huella difiere. Requiere meridiano.db (gen_datos.py)."""
import hashlib, sqlite3
import pandas as pd

TAM = 100                                   # claves por bloque (id_cliente // 100)
con = sqlite3.connect("meridiano.db")
o = pd.read_sql("SELECT * FROM origen_cliente", con).set_index("id_cliente")
d = pd.read_sql("SELECT * FROM destino_cliente", con).set_index("id_cliente")

def huellas(df, col):
    """Una huella MD5 por bloque: cuenta de filas y valores de la columna, en orden de clave."""
    out = {}
    for bloque, g in df.groupby(df.index // TAM):
        texto = "|".join(f"{i}:{v}" for i, v in g[col].items())
        out[bloque] = (len(g), hashlib.md5(texto.encode()).hexdigest())
    return pd.Series(out)

comunes = o.index.intersection(d.index)           # claves que llegaron: la pérdida de filas se mide aparte
oc, dc = o.loc[comunes], d.loc[comunes]
bloques = len(set(oc.index // TAM))
print(f"Bloques de {TAM} claves comparadas: {bloques}")
for col in o.columns:
    h1, h2 = huellas(oc, col), huellas(dc, col)
    distintos = int((h1 != h2).sum())
    print(f"{col:18s} bloques con huella distinta: {distintos:3d} de {bloques}")
