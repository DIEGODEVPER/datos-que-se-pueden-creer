"""Demuestra por qué una regla escondida en un disparador se pierde al cargar en bloque.
Usa una base en memoria; no toca meridiano.db."""
import sqlite3
con = sqlite3.connect(":memory:")
con.executescript("""
CREATE TABLE cliente (id INTEGER PRIMARY KEY, ultimo_pago TEXT, estado_fin TEXT);
-- La regla vive aquí, en el sistema de origen, y no en ningún documento:
CREATE TRIGGER t_estado AFTER UPDATE OF ultimo_pago ON cliente
BEGIN
  UPDATE cliente SET estado_fin =
    CASE WHEN julianday('2026-11-02') - julianday(NEW.ultimo_pago) > 90 THEN 'MORA_90'
         WHEN julianday('2026-11-02') - julianday(NEW.ultimo_pago) > 30 THEN 'MORA_30'
         ELSE 'AL_DIA' END
  WHERE id = NEW.id;
END;
""")
# 1) Inventario: cómo descubrir lógica escondida en la base de origen
for nombre, tabla in con.execute("SELECT name, tbl_name FROM sqlite_master WHERE type='trigger'"):
    print("Disparador encontrado:", nombre, "sobre la tabla", tabla)

# 2) En el sistema de origen, un pago actualiza la fecha y el disparador recalcula el estado
con.execute("INSERT INTO cliente VALUES (1, '2026-10-20', 'AL_DIA')")
con.execute("UPDATE cliente SET ultimo_pago = '2026-07-01' WHERE id = 1")
print("Origen, tras actualizar el pago :", con.execute("SELECT * FROM cliente").fetchall())

# 3) En el destino no existe el disparador: se carga la fila ya hecha y el estado queda congelado
con.execute("CREATE TABLE cliente_destino (id INTEGER PRIMARY KEY, ultimo_pago TEXT, estado_fin TEXT)")
con.execute("INSERT INTO cliente_destino VALUES (1, '2026-10-20', 'AL_DIA')")
con.execute("UPDATE cliente_destino SET ultimo_pago = '2026-07-01' WHERE id = 1")
print("Destino, tras la misma actualización:", con.execute("SELECT * FROM cliente_destino").fetchall())
