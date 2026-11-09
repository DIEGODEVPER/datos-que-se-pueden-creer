"""Pareto de hallazgos y búsqueda de cuándo empezó el problema de la fecha de nacimiento."""
import sqlite3
import pandas as pd
con = sqlite3.connect("meridiano.db")

# 1) Pareto: filas afectadas por tipo de hallazgo
hallazgos = pd.read_sql("""
SELECT descripcion AS hallazgo, fallos AS filas_afectadas FROM dq_resultado ORDER BY fallos DESC""", con)
hallazgos["%"] = (100 * hallazgos.filas_afectadas / hallazgos.filas_afectadas.sum()).round(1)
hallazgos["% acumulado"] = hallazgos["%"].cumsum().round(1)
print(hallazgos.to_string(index=False))

# 2) ¿Desde cuándo? Tasa de fecha de nacimiento faltante por trimestre de alta
q = pd.read_sql("""
SELECT strftime('%Y', fecha_alta) || '-T' || ((CAST(strftime('%m', fecha_alta) AS INT) + 2) / 3) AS trimestre,
       COUNT(*) AS clientes,
       ROUND(100.0 * SUM(fecha_nacimiento IS NULL OR fecha_nacimiento = '1900-01-01') / COUNT(*), 1) AS sin_fecha_pct
FROM origen_cliente WHERE fecha_alta >= '2024-01-01'
GROUP BY trimestre ORDER BY trimestre""", con)
print(); print(q.to_string(index=False))
