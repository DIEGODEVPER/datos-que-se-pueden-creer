import sqlite3, re, sys
archivo = sys.argv[1]; base = sys.argv[2] if len(sys.argv) > 2 else "meridiano.db"
con = sqlite3.connect(base)
for bloque in re.split(r"(?m)^-- @", open(archivo, encoding="utf-8").read())[1:]:
    titulo, _, sql = bloque.partition("\n")
    cur = con.execute(sql.strip().rstrip(";"))
    cols = [d[0] for d in cur.description]
    print(f"\n[{titulo.strip()}]"); print(" | ".join(cols))
    for fila in cur.fetchall(): print(" | ".join(str(x) for x in fila))
