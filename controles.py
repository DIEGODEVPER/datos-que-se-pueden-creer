"""Registro de asuntos, control de entrada, 'cortafuegos' de datos y corrección dirigida de duplicados."""
import re, sqlite3, unicodedata, difflib
import pandas as pd

con = sqlite3.connect("meridiano.db")

# 1) Registro de asuntos (incidentes): qué pasó, por qué, qué se decidió y quién responde
con.execute("DROP TABLE IF EXISTS asunto")
con.execute("""CREATE TABLE asunto (id INTEGER PRIMARY KEY, regla TEXT, descripcion TEXT,
               causa_raiz TEXT, decision TEXT, responsable TEXT, prioridad TEXT, estado TEXT)""")
con.execute("INSERT INTO asunto (regla, descripcion, causa_raiz, decision, responsable, prioridad, estado) VALUES (?,?,?,?,?,?,?)",
            ("R1", "62,3 % de clientes nuevos con fecha de nacimiento válida",
             "Desde nov-2025 el formulario de alta pide 14 campos y mide al vendedor solo por ventas por hora",
             "Pedir 5 campos al alta, completar el resto en la segunda compra y medir también la calidad de captura",
             "Dueño de Cliente", "Alta", "Abierto"))
con.commit()
print(con.execute("SELECT id, regla, prioridad, estado, responsable FROM asunto").fetchall())

# 2) Control de entrada: la base rechaza el dato inválido en lugar de aceptarlo
con.execute("DROP TABLE IF EXISTS cliente_nuevo")
con.execute("""CREATE TABLE cliente_nuevo (id_cliente INTEGER PRIMARY KEY, nombre TEXT NOT NULL,
               fecha_nacimiento TEXT NOT NULL
               CHECK (fecha_nacimiento <> '1900-01-01' AND fecha_nacimiento BETWEEN '1920-01-01' AND '2008-12-31'))""")
for fila in [(1, "Ana Rojas", "1985-04-12"), (2, "Luis Paz", "1900-01-01")]:
    try:
        con.execute("INSERT INTO cliente_nuevo VALUES (?,?,?)", fila); print("aceptado:", fila)
    except sqlite3.IntegrityError as e:
        print("rechazado:", fila, "->", e)

# 3) 'Cortafuegos' de datos: reglas de calidad aplicadas antes de cargar; lo que falla va a cuarentena
EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
def cortafuegos(df):
    ok = (df.fecha_nacimiento.notna() & (df.fecha_nacimiento != "1900-01-01")
          & df.email.fillna("").str.match(EMAIL) & df.documento.fillna("").str.fullmatch(r"\d{8}"))
    return df[ok], df[~ok]
nuevos = pd.read_sql("SELECT * FROM origen_cliente WHERE fecha_alta >= date('2026-11-02','-12 months')", con)
aceptados, cuarentena = cortafuegos(nuevos)
print(f"Lote de {len(nuevos)} clientes nuevos: {len(aceptados)} aceptados, {len(cuarentena)} a cuarentena")

# 4) Corrección dirigida por confianza: fusiona duplicados con alta similitud, el resto va al steward
def norm(s):
    s = unicodedata.normalize("NFD", s)
    return "".join(c for c in s if unicodedata.category(c) != "Mn").upper().strip()
todos = pd.read_sql("SELECT id_cliente, nombre, documento FROM origen_cliente", con)
rep = todos[todos.documento.notna() & todos.duplicated("documento", keep=False)].sort_values(["documento", "id_cliente"])
auto = revision = 0
for _, g in rep.groupby("documento"):
    a, b = g.nombre.iloc[0], g.nombre.iloc[1]
    score = difflib.SequenceMatcher(None, norm(a), norm(b)).ratio()
    if score >= 0.95: auto += 1
    else: revision += 1
print(f"Pares con el mismo documento: {auto + revision}; fusión automática (confianza >= 0,95): {auto}; a revisión del steward: {revision}")
