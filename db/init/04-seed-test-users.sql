-- ============================================================
-- Seed: usuarios de prueba determinísticos por rol
-- ============================================================

INSERT INTO usuario (id_usuario, nombre, apellido, correo, email, rol, estado, creado_en, actualizado_en) VALUES
('11111111-1111-1111-1111-111111111111', 'Solicitante', 'Test', 'sol@uc.cl', 'sol@uc.cl', 'SOL', true, NOW(), NOW()),
('22222222-2222-2222-2222-222222222222', 'Estudiante', 'Test', 'est@uc.cl', 'est@uc.cl', 'EST', true, NOW(), NOW()),
('33333333-3333-3333-3333-333333333333', 'Ayudante', 'Test', 'ayu@uc.cl', 'ayu@uc.cl', 'AYU', true, NOW(), NOW()),
('44444444-4444-4444-4444-444444444444', 'Profesor', 'Test', 'pro@uc.cl', 'pro@uc.cl', 'PRO', true, NOW(), NOW()),
('55555555-5555-5555-5555-555555555555', 'Admin', 'Test', 'adm@uc.cl', 'adm@uc.cl', 'ADM', true, NOW(), NOW());
