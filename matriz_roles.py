"""Matriz de responsabilidades de las verificaciones de calidad y comprobación de que cada fila tiene un solo responsable (A)."""
import pandas as pd

ROLES = ["Dueño del dato", "Steward", "Analista de calidad", "Ingeniero de datos", "DBA", "Gerente de calidad"]
# R = hace, A = responde (uno solo por fila), C = consultado, I = informado, "" = no participa
MATRIZ = {
 "Perfilar antes de mover":            ["I", "C", "A", "R", "R", "I"],
 "Conciliar origen y destino":         ["I", "C", "R", "A", "C", "I"],
 "Inventariar lógica escondida":       ["C", "C", "C", "R", "A", "I"],
 "Fijar reglas y umbrales":            ["A", "R", "R", "C", "",  "C"],
 "Programar y correr las reglas":      ["I", "I", "R", "A", "C", ""],
 "Vigilar la carta de control":        ["I", "C", "A", "R", "",  "I"],
 "Atender avisos y causa raíz":        ["C", "R", "A", "R", "C", "I"],
 "Decidir la remediación":             ["A", "R", "C", "C", "C", "I"],
 "Corregir datos":                     ["I", "A", "C", "R", "R", ""],
 "Cortafuegos y controles de entrada": ["C", "C", "R", "A", "R", "I"],
 "Registro de asuntos y reporte":      ["I", "C", "R", "C", "",  "A"],
 "Política de calidad":                ["R", "C", "C", "",  "",  "A"],
}
df = pd.DataFrame(MATRIZ, index=ROLES).T
print(df.to_string())
for actividad, fila in df.iterrows():
    n = int((fila == "A").sum())
    assert n == 1, f"'{actividad}' tiene {n} responsables (A); debe tener exactamente uno"
print("\nControl: cada actividad tiene exactamente un responsable (A).")
print("Actividades por rol (A):", (df == "A").sum().to_dict())
