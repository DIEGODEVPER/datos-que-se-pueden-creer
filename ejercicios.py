"""Soluciones de los ejercicios del Anexo F. Requiere meridiano.db (gen_datos.py y gen_pedidos.py)."""
import math, sqlite3
con = sqlite3.connect("meridiano.db")
q = lambda sql: con.execute(sql).fetchall()

print("--- Ejercicio 1: correos con formato inválido")
total, = q("SELECT COUNT(*) FROM origen_cliente WHERE email NOT GLOB '*?@?*.?*'")[0]
vacios, = q("SELECT COUNT(*) FROM origen_cliente WHERE email = ''")[0]
print("inválidos:", total, "| vacíos:", vacios, "| con formato roto:", total - vacios)

print("--- Ejercicio 2: fecha de nacimiento faltante por año de alta")
for anio, n, pct in q("""SELECT strftime('%Y', fecha_alta), COUNT(*),
        ROUND(100.0 * SUM(fecha_nacimiento IS NULL OR fecha_nacimiento = '1900-01-01') / COUNT(*), 1)
        FROM origen_cliente GROUP BY 1 ORDER BY 1"""):
    print(anio, n, pct)

print("--- Ejercicio 3: documentos vacíos y repetidos")
print("vacíos:", q("SELECT COUNT(*) FROM origen_cliente WHERE documento IS NULL")[0][0],
      "| repetidos:", q("SELECT COUNT(documento) - COUNT(DISTINCT documento) FROM origen_cliente")[0][0])

print("--- Ejercicio 4: último pago vacío")
print("sin pago registrado:", q("SELECT COUNT(*) FROM origen_cliente WHERE ultimo_pago IS NULL")[0][0],
      "de", q("SELECT COUNT(*) FROM origen_cliente")[0][0])

print("--- Ejercicio 5: límite de la carta de control para 25 clientes por semana y p = 2,3 %")
p, n = 0.023, 25
ucl = p + 3 * math.sqrt(p * (1 - p) / n)
print(f"límite superior: {100 * ucl:.1f} %  | 2 de 25 = {100 * 2 / 25:.0f} %  | 3 de 25 = {100 * 3 / 25:.0f} %")

print("--- Ejercicio 6: clientes perdidos con pedidos")
print("perdidos:", q("""SELECT COUNT(*) FROM origen_cliente o LEFT JOIN destino_cliente d USING (id_cliente)
                       WHERE d.id_cliente IS NULL""")[0][0],
      "| con pedidos en el destino huérfano:", q("""SELECT COUNT(DISTINCT id_cliente) FROM destino_pedido
                       WHERE id_cliente NOT IN (SELECT id_cliente FROM destino_cliente)""")[0][0])
