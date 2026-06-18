-- ============================================================
-- Seed: artículos de prueba (coinciden con mock del frontend)
-- ============================================================

INSERT INTO articulo (id_articulo, nombre_articulo, stock_actual, stock_minimo, alerta_stock, actualizado_en)
VALUES
('art-001', 'Filamento PLA Morado', 50, 10, false, NOW()),
('art-002', 'Resina Estándar Gris', 30, 5, false, NOW()),
('art-003', 'Filamento ABS Negro', 40, 8, false, NOW());
