"""Carta de control (para proporciones) de la fecha de nacimiento faltante, por semana de alta."""
import sqlite3, math
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

con = sqlite3.connect("meridiano.db")
df = pd.read_sql("SELECT fecha_alta, fecha_nacimiento FROM origen_cliente", con, parse_dates=["fecha_alta"])
df = df[df.fecha_alta >= "2024-11-04"].copy()
df["falla"] = df.fecha_nacimiento.isna() | (df.fecha_nacimiento == "1900-01-01")
df["semana"] = df.fecha_alta.dt.to_period("W-SUN").dt.start_time
sem = df.groupby("semana").agg(n=("falla", "size"), fallos=("falla", "sum")).reset_index()
sem["p"] = sem.fallos / sem.n

LINEA_BASE = 40                      # primeras 40 semanas: el proceso estable
base = sem.iloc[:LINEA_BASE]
p_bar = base.fallos.sum() / base.n.sum()
n_med = sem.n.mean()
sigma = math.sqrt(p_bar * (1 - p_bar) / n_med)
ucl, lcl = p_bar + 3 * sigma, max(0.0, p_bar - 3 * sigma)
sem["fuera"] = (sem.p > ucl) | (sem.p < lcl)

print(f"Semanas: {len(sem)}  clientes por semana (promedio): {n_med:.1f}")
print(f"Línea central: {p_bar:.1%}   límite superior: {ucl:.1%}   límite inferior: {lcl:.1%}")
primera = sem[(sem.index >= LINEA_BASE) & sem.fuera].head(1)
print("Primera semana fuera de control:", primera.semana.dt.date.iloc[0],
      f"con {primera.p.iloc[0]:.1%}")
print("Semanas fuera de control en la línea base:", int(base.assign(f=(base.p > ucl) | (base.p < lcl)).f.sum()))
print("Semanas fuera de control después:", int(sem.iloc[LINEA_BASE:].fuera.sum()), "de", len(sem) - LINEA_BASE)

fig, ax = plt.subplots(figsize=(8, 3.6), dpi=200)
ax.plot(sem.semana, sem.p * 100, color="#2557ff", lw=1.2, marker="o", ms=2.5)
ax.axhline(p_bar * 100, color="#0b1d3a", lw=1); ax.axhline(ucl * 100, color="#c0392b", ls="--", lw=1)
ax.axhline(lcl * 100, color="#c0392b", ls="--", lw=1)
ax.scatter(sem[sem.fuera].semana, sem[sem.fuera].p * 100, color="#c0392b", s=14, zorder=3)
ax.axvline(sem.semana.iloc[LINEA_BASE], color="#999", lw=.8, ls=":")
ax.set_ylabel("% sin fecha de nacimiento válida"); ax.set_xlabel("Semana de alta del cliente")
ax.text(sem.semana.iloc[-1], ucl * 100 - 3.2, "Límite superior", color="#c0392b", fontsize=7, ha="right")
ax.text(sem.semana.iloc[-1], p_bar * 100 + 1.2, "Línea central", color="#0b1d3a", fontsize=7, ha="right")
ax.text(sem.semana.iloc[LINEA_BASE] , 63, " fin de la línea base", color="#666", fontsize=7)
for s in ("top", "right"): ax.spines[s].set_visible(False)
fig.tight_layout(); fig.savefig("carta_control.png"); print("guardado carta_control.png")
