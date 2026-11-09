"""Evalúa reglas de calidad contra un umbral y guarda el resultado (tabla dq_resultado)."""
import sqlite3, datetime as dt

HOY = "2026-11-02"
# (id, dimensión, descripción, SQL que devuelve total y fallos, mínimo aceptable de datos correctos %)
REGLAS = [
 ("R1", "Completitud", "Fecha de nacimiento informada y distinta de 1900 (clientes nuevos)",
  f"""SELECT COUNT(*), SUM(fecha_nacimiento IS NULL OR fecha_nacimiento='1900-01-01')
      FROM origen_cliente WHERE fecha_alta >= date('{HOY}','-12 months')""", 98.0),
 ("R2", "Validez", "Correo con formato válido",
  "SELECT COUNT(*), SUM(email IS NULL OR email='' OR email NOT GLOB '*?@?*.?*') FROM origen_cliente", 99.0),
 ("R3", "Unicidad", "Un solo registro por documento",
  """SELECT COUNT(documento), COUNT(documento) - COUNT(DISTINCT documento) FROM origen_cliente""", 100.0),
 ("R4", "Consistencia", "Estado financiero igual en origen y destino",
  """SELECT COUNT(*), SUM(d.estado_fin <> o.estado_fin)
      FROM origen_cliente o JOIN destino_cliente d USING (id_cliente)""", 100.0),
 ("R5", "Integridad", "Todo pedido del destino tiene cliente en el destino",
  """SELECT COUNT(*), SUM(c.id_cliente IS NULL)
      FROM destino_pedido p LEFT JOIN destino_cliente c USING (id_cliente)""", 100.0),
 ("R6", "Completitud", "Todo cliente del origen llegó al destino",
  """SELECT COUNT(*), SUM(d.id_cliente IS NULL)
      FROM origen_cliente o LEFT JOIN destino_cliente d USING (id_cliente)""", 100.0),
]

def evaluar(con):
    con.execute("DROP TABLE IF EXISTS dq_resultado")
    con.execute("""CREATE TABLE dq_resultado (regla TEXT, dimension TEXT, descripcion TEXT,
                   total INT, fallos INT, correcto_pct REAL, minimo_pct REAL, estado TEXT)""")
    for rid, dim, desc, sql, minimo in REGLAS:
        total, fallos = con.execute(sql).fetchone()
        fallos = fallos or 0
        ok = round(100.0 * (total - fallos) / total, 1)
        estado = "Aceptable" if ok >= minimo else "Inaceptable"
        con.execute("INSERT INTO dq_resultado VALUES (?,?,?,?,?,?,?,?)",
                    (rid, dim, desc, total, fallos, ok, minimo, estado))
    con.commit()

# A quién se avisa cuando una regla no llega al mínimo (el SLA de calidad lo define con nombre propio)
RESPONSABLE = {"R1": "Steward de Comercial", "R2": "Steward de Comercial", "R3": "Steward de Cliente",
               "R4": "Dueño de Cliente", "R5": "Ingeniería de datos", "R6": "Ingeniería de datos"}

def alertas(con):
    """Una línea de aviso por cada regla Inaceptable, con el responsable que debe actuar."""
    filas = con.execute("""SELECT regla, descripcion, correcto_pct, minimo_pct
                           FROM dq_resultado WHERE estado = 'Inaceptable' ORDER BY regla""").fetchall()
    return [f"[{r}] {d}: {c:.1f} % correcto (mínimo {m:.0f} %) -> avisar a {RESPONSABLE[r]}"
            for r, d, c, m in filas]

if __name__ == "__main__":
    con = sqlite3.connect("meridiano.db")
    evaluar(con)
    for r in con.execute("SELECT regla, dimension, total, fallos, correcto_pct, minimo_pct, estado FROM dq_resultado"):
        print(" | ".join(str(x) for x in r))
    print()
    print("\n".join(alertas(con)))
