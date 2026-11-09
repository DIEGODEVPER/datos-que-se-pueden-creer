"""Perfilamiento de una tabla: nulos, distintos, mínimo/máximo, longitud y patrón de formato."""
import re, sqlite3, sys
import pandas as pd

def patron(v):
    """Convierte un valor en su patrón: letras -> A, dígitos -> 9, el resto se conserva."""
    if v is None or (isinstance(v, float) and pd.isna(v)): return "<nulo>"
    s = re.sub(r"[A-Za-zÁÉÍÓÚáéíóúÑñ]", "A", str(v))
    return re.sub(r"\d", "9", s)

def perfilar(df, valores_por_defecto=("", "1900-01-01")):
    filas = []
    n = len(df)
    for c in df.columns:
        s = df[c]
        txt = s.dropna().astype(str)
        pat = s.map(patron).value_counts()
        filas.append({
            "columna": c,
            "nulos_%": round(100 * s.isna().mean(), 1),
            "por_defecto_%": round(100 * s.isin(valores_por_defecto).mean(), 1),
            "distintos": s.nunique(),
            "min": txt.min() if len(txt) else None,
            "max": txt.max() if len(txt) else None,
            "long_min": int(txt.str.len().min()) if len(txt) else None,
            "long_max": int(txt.str.len().max()) if len(txt) else None,
            "patron_top": pat.index[0],
            "patron_top_%": round(100 * pat.iloc[0] / n, 1),
        })
    return pd.DataFrame(filas)

if __name__ == "__main__":
    tabla = sys.argv[1] if len(sys.argv) > 1 else "origen_cliente"
    con = sqlite3.connect("meridiano.db")
    df = pd.read_sql(f"SELECT * FROM {tabla}", con)
    pd.set_option("display.width", 200); pd.set_option("display.max_columns", 20)
    print(f"Tabla {tabla}: {len(df)} filas")
    print(perfilar(df).to_string(index=False))
