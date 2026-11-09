# Datos que se pueden creer: código del libro

Código de *Datos que se pueden creer*, de Diego Salas: cómo verificar la calidad de los datos antes y después de moverlos, con SQL, Python y los roles de Grupo Meridiano.

Grupo Meridiano, sus clientes, sus pedidos y todas las cifras son ficticios. Los datos los genera `gen_datos.py` con una semilla fija (2026), así que obtienes los mismos números que ves en el libro.

## Requisitos

- Python 3.10 o superior (SQLite ya viene incluido)
- `pip install -r requirements.txt`

## Cómo ejecutarlo

Desde una carpeta con estos archivos:

```
./ejecutar_todo.sh
```

o, uno por uno, en este orden:

| Orden | Archivo | Parte del libro | Qué hace |
| --- | --- | --- | --- |
| 1 | `gen_datos.py` | 2 | Crea `meridiano.db` con `origen_cliente` y `destino_cliente` |
| 2 | `gen_pedidos.py` | 3 | Agrega `origen_pedido` y `destino_pedido` |
| 3 | `perfilar.py` | 2 | Perfil de todas las columnas (`python3 perfilar.py origen_cliente`) |
| 4 | `correr_sql.py` + `perfilamiento.sql` | 2 | Ocho verificaciones SQL de perfilamiento |
| 5 | `correr_sql.py` + `conciliacion.sql` | 3 | Siete consultas de conciliación origen-destino |
| 6 | `conciliar.py` | 3 | Compara origen y destino por clave y por columna |
| 7 | `disparador_demo.py` | 3 | Muestra cómo un disparador no migrado congela `ESTADO_FIN` |
| 8 | `reglas_dq.py` | 4 | Evalúa seis reglas contra un umbral y genera avisos |
| 9 | `control_spc.py` | 4 | Carta de control semanal (`carta_control.png`) |
| 10 | `causa_raiz.py` | 5 | Pareto de hallazgos y tasa por trimestre (después del paso 8) |
| 11 | `controles.py` | 5 | Registro de asuntos, control de entrada, cortafuegos y fusión de duplicados |
| 12 | `calidad_ia.py` | 7 | Edad, índice de estabilidad (PSI) y guarda previa al entrenamiento |
| 13 | `matriz_roles.py` | 6 | Matriz de responsabilidades con verificación |

## Aviso

El código es material educativo y se ofrece sin garantía. Pruébalo en tu entorno antes de usarlo con datos reales. Las consultas están escritas para SQLite; el Anexo D del libro da las equivalencias habituales para PostgreSQL y SQL Server.

*) Al ejecutar los scripts se crea el archivo meridiano.db. No se sube al repositorio (está en .gitignore) porque cualquiera lo regenera con gen_datos.py.
