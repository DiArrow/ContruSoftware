-- ============================================================
-- Seed: usuarios de prueba determinísticos por rol
-- ============================================================

INSERT INTO usuario (id_usuario, nombre, apellido, correo, email, rol, estado, password_hash, creado_en, actualizado_en) VALUES
('11111111-1111-1111-1111-111111111111', 'Solicitante', 'Test', 'sol@uc.cl', 'sol@uc.cl', 'SOL', true, '$2b$12$mfVES./yx3ugwK366xrJBeEZ30uCAZJ6e1mpey8YH2WRNHY8azUXO', NOW(), NOW()),
('22222222-2222-2222-2222-222222222222', 'Estudiante', 'Test', 'est@uc.cl', 'est@uc.cl', 'EST', true, '$2b$12$kIEUgfcPSoigNIU1awrLz.6eiXIDbxqLig6AeCUX7mmZnqB.ILNzW', NOW(), NOW()),
('33333333-3333-3333-3333-333333333333', 'Ayudante', 'Test', 'ayu@uc.cl', 'ayu@uc.cl', 'AYU', true, '$2b$12$moZepdWEYIvc81hQI/iUwuWVfGKK8h9qpxIxdQEDXpRcW812TdTny', NOW(), NOW()),
('44444444-4444-4444-4444-444444444444', 'Profesor', 'Test', 'pro@uc.cl', 'pro@uc.cl', 'PRO', true, '$2b$12$slVzj90A7CxEj9v1.gxJiuqvlgpXSFpIBJ4sIPVf54RQnb66dLxki', NOW(), NOW()),
('55555555-5555-5555-5555-555555555555', 'Admin', 'Test', 'adm@uc.cl', 'adm@uc.cl', 'ADM', true, '$2b$12$Bq2ZJ8phT6WrK.LWLadiMOjOEX892ac9J4r/yFDNMZILZAxEd0Gr.', NOW(), NOW());
