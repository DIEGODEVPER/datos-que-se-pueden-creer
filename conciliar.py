"""Concilia origen y destino por clave y por columna, con pandas."""
import sqlite3
import pandas as pd

con = sqlite3.connect("meridiano.db")
o = pd.read_sql("SELECT * FROM origen_cliente", con).set_index("id_cliente")
d = pd.read_sql("SELECT * FROM destino_cliente", con).set_index("id_cliente")

print("Filas origen / destino:", len(o), "/", len(d))
perdidas = o.index.difference(d.index)
sobrantes = d.index.difference(o.index)
print("Perdidas (en origen, no en destino):", len(perdidas))
print("Sobrantes (en destino, no en origen):", len(sobrantes))

comunes = o.index.intersection(d.index)
a, b = o.loc[comunes], d.loc[comunes]
# Una columna 'difiere' si el valor cambió; dos nulos se consideran iguales
for col in o.columns:
    distinto = ~((a[col] == b[col]) | (a[col].isna() & b[col].isna()))
    print(f"{col:18s} filas distintas: {int(distinto.sum())}")
