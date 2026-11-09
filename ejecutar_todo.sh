#!/usr/bin/env bash
# Ejecuta los 13 pasos del libro en orden. Requiere Python 3.10+ y: pip install -r requirements.txt
set -e
python3 gen_datos.py
python3 gen_pedidos.py
python3 perfilar.py origen_cliente
python3 correr_sql.py perfilamiento.sql
python3 correr_sql.py conciliacion.sql
python3 conciliar.py
python3 disparador_demo.py
python3 reglas_dq.py
python3 control_spc.py
python3 causa_raiz.py
python3 controles.py
python3 calidad_ia.py
python3 matriz_roles.py
