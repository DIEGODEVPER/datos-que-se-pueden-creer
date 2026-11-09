-- @1 Nulos y valores por defecto en fecha_nacimiento, solo clientes nuevos (últimos 12 meses)
SELECT COUNT(*) AS clientes_nuevos,
       SUM(CASE WHEN fecha_nacimiento IS NULL OR fecha_nacimiento = '1900-01-01' THEN 1 ELSE 0 END) AS vacios_o_1900,
       ROUND(100.0 * SUM(CASE WHEN fecha_nacimiento IS NULL OR fecha_nacimiento = '1900-01-01' THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct
FROM origen_cliente
WHERE fecha_alta >= date('2026-11-02', '-12 months');

-- @2 Mínimo y máximo: busca valores fuera de rango
SELECT MIN(fecha_nacimiento) AS min_nac, MAX(fecha_nacimiento) AS max_nac,
       MIN(fecha_alta) AS min_alta, MAX(fecha_alta) AS max_alta
FROM origen_cliente;

-- @3 Longitudes: el documento debe tener 8 dígitos
SELECT LENGTH(documento) AS longitud, COUNT(*) AS filas
FROM origen_cliente GROUP BY LENGTH(documento) ORDER BY filas DESC;  -- longitud vacía = documento nulo

-- @4 Distribución de frecuencias de estado_fin
SELECT estado_fin, COUNT(*) AS filas, ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM origen_cliente), 1) AS pct
FROM origen_cliente GROUP BY estado_fin ORDER BY filas DESC;

-- @5 Formato: correos que no cumplen un patrón mínimo (algo@algo.algo)
SELECT COUNT(*) AS correos_invalidos,
       ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM origen_cliente), 1) AS pct
FROM origen_cliente
WHERE email IS NULL OR email = '' OR email NOT GLOB '*?@?*.?*';

-- @6 Unicidad: mismo documento registrado más de una vez
SELECT COUNT(*) AS documentos_repetidos, SUM(c) AS filas_involucradas
FROM (SELECT documento, COUNT(*) AS c FROM origen_cliente WHERE documento IS NOT NULL GROUP BY documento HAVING COUNT(*) > 1);

-- @7 Entre columnas: se pagó antes de comprar
SELECT COUNT(*) AS pago_antes_de_compra FROM origen_cliente WHERE ultimo_pago < ultima_compra;

-- @8 Completitud del documento de identidad
SELECT COUNT(*) AS filas, SUM(documento IS NULL) AS documentos_vacios,
       ROUND(100.0 * (COUNT(*) - SUM(documento IS NULL)) / COUNT(*), 1) AS completo_pct
FROM origen_cliente;
