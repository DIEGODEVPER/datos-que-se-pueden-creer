-- @1 Conteo de filas en origen y destino
SELECT (SELECT COUNT(*) FROM origen_cliente)  AS filas_origen,
       (SELECT COUNT(*) FROM destino_cliente) AS filas_destino;

-- @2 Filas que están en el origen y no llegaron al destino
SELECT COUNT(*) AS filas_perdidas
FROM origen_cliente o
LEFT JOIN destino_cliente d ON d.id_cliente = o.id_cliente
WHERE d.id_cliente IS NULL;

-- @3 Nombres que llegaron truncados
SELECT COUNT(*) AS nombres_truncados, MAX(LENGTH(d.nombre)) AS largo_maximo_destino
FROM origen_cliente o
JOIN destino_cliente d ON d.id_cliente = o.id_cliente
WHERE d.nombre <> o.nombre;

-- @4 Estado financiero distinto entre origen y destino
SELECT COUNT(*) AS estados_distintos
FROM origen_cliente o
JOIN destino_cliente d ON d.id_cliente = o.id_cliente
WHERE d.estado_fin <> o.estado_fin;

-- @5 Cómo cambió la distribución del estado financiero
SELECT 'origen' AS lado, estado_fin, COUNT(*) AS n FROM origen_cliente GROUP BY estado_fin
UNION ALL
SELECT 'destino', estado_fin, COUNT(*) FROM destino_cliente GROUP BY estado_fin
ORDER BY 1, 2;

-- @6 Pedidos huérfanos en el destino (cliente que no existe)
SELECT COUNT(*) AS pedidos_huerfanos, ROUND(SUM(p.monto), 2) AS monto_huerfano
FROM destino_pedido p
LEFT JOIN destino_cliente c ON c.id_cliente = p.id_cliente
WHERE c.id_cliente IS NULL;

-- @7 Totales de control de pedidos: filas y suma de montos
SELECT 'origen' AS lado, COUNT(*) AS filas, ROUND(SUM(monto), 2) AS monto FROM origen_pedido
UNION ALL
SELECT 'destino', COUNT(*), ROUND(SUM(monto), 2) FROM destino_pedido;
