"""Qué le hace el valor 1900-01-01 a una variable de un modelo, y una guarda de calidad previa al entrenamiento."""
import sqlite3
import numpy as np, pandas as pd
HOY = pd.Timestamp("2026-11-02")
con = sqlite3.connect("meridiano.db")
df = pd.read_sql("SELECT id_cliente, fecha_alta, fecha_nacimiento FROM origen_cliente", con,
                 parse_dates=["fecha_alta"])
df["nac"] = pd.to_datetime(df.fecha_nacimiento, errors="coerce")
df["edad"] = ((HOY - df.nac).dt.days / 365.25)
df["nuevo"] = df.fecha_alta >= HOY - pd.Timedelta(days=365)

print("Edad máxima:", round(df.edad.max(), 1), "años; clientes con edad > 100:", int((df.edad > 100).sum()))
for etiqueta, g in df.groupby("nuevo"):
    print(("nuevos" if etiqueta else "antiguos"), "edad media:", round(g.edad.mean(), 1),
          "| sin edad:", int(g.edad.isna().sum()), "| con edad > 100:", int((g.edad > 100).sum()))

def psi(esperado, real, cortes=10):
    """Índice de estabilidad de población: compara dos distribuciones. >0,25 suele considerarse un cambio fuerte."""
    q = np.unique(np.quantile(esperado.dropna(), np.linspace(0, 1, cortes + 1)))
    q[0], q[-1] = -np.inf, np.inf
    e = np.histogram(esperado.dropna(), q)[0] / esperado.notna().sum()
    r = np.histogram(real.dropna(), q)[0] / real.notna().sum()
    e, r = np.clip(e, 1e-6, None), np.clip(r, 1e-6, None)
    return float(((r - e) * np.log(r / e)).sum())

ant, nue = df[~df.nuevo], df[df.nuevo]
print("PSI de la edad, clientes nuevos contra antiguos (datos tal cual):", round(psi(ant.edad, nue.edad), 3))
limpio = nue.edad.where(nue.edad <= 100)
print("PSI de la edad, nuevos tras tratar 1900 como faltante:", round(psi(ant.edad.where(ant.edad <= 100), limpio), 3))

def guarda(df, columna="edad", max_faltante=0.05, max_inverosimil=0.02, tope=100):
    """Devuelve (aprobado, motivos). Se ejecuta antes de entrenar o reentrenar."""
    motivos = []
    falt = df[columna].isna().mean()
    inver = (df[columna] > tope).mean()
    if falt > max_faltante: motivos.append(f"{columna}: {falt:.1%} faltante (máx. {max_faltante:.0%})")
    if inver > max_inverosimil: motivos.append(f"{columna}: {inver:.1%} con valores > {tope}")
    return (not motivos), motivos

for nombre, g in (("antiguos", ant), ("nuevos", nue)):
    ok, m = guarda(g); print("Guarda", nombre, "->", "APROBADO" if ok else "RECHAZADO", m)

# Qué pasa si simplemente se descartan las filas sin edad válida (una "limpieza" frecuente)
valido = df.edad.notna() & (df.edad <= 100)
print("Clientes nuevos en la base completa:", f"{df.nuevo.mean():.1%}",
      "| en la base tras descartar edades inválidas:", f"{df[valido].nuevo.mean():.1%}")
print("Clientes nuevos descartados:", int((df.nuevo & ~valido).sum()), "de", int(df.nuevo.sum()),
      f"({(df.nuevo & ~valido).sum() / df.nuevo.sum():.1%})",
      "| antiguos descartados:", f"{((~df.nuevo) & ~valido).sum() / (~df.nuevo).sum():.1%}")
