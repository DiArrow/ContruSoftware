-- ============================================================
-- Seed: usuarios de prueba determinísticos por rol
-- SOL: sol123, EST: est123, AYU: ayu123, PRO: pro123, ADM: adm123
-- ============================================================

INSERT INTO usuario (
    id_usuario, nombre, apellido, correo, email, rol, estado, password_hash, creado_en, actualizado_en
) VALUES
(
    '11111111-1111-1111-1111-111111111111',
    'Solicitante',
    'Test',
    'sol@uc.cl',
    'sol@uc.cl',
    'SOL',
    true,
    '$2b$12$NzODyh/yOXJ3DqKB6C/0aeaowSgy/E71YYIVP5y3e3uRHPI5V6eOe',
    NOW(),
    NOW()
),
(
    '22222222-2222-2222-2222-222222222222',
    'Estudiante',
    'Test',
    'est@uc.cl',
    'est@uc.cl',
    'EST',
    true,
    '$2b$12$J12hG1Us7bRqf1swwGYJ5u4ise/.H8dySRNzq9.90OSY781pcz96e',
    NOW(),
    NOW()
),
(
    '33333333-3333-3333-3333-333333333333',
    'Ayudante',
    'Test',
    'ayu@uc.cl',
    'ayu@uc.cl',
    'AYU',
    true,
    '$2b$12$cIlYuQSNRK8IuiGvsxnHeeYvaVhyKMvvA2WuEIcP/UI9VisN7hYAG',
    NOW(),
    NOW()
),
(
    '44444444-4444-4444-4444-444444444444',
    'Profesor',
    'Test',
    'pro@uc.cl',
    'pro@uc.cl',
    'PRO',
    true,
    '$2b$12$P833NTXpyENa6ol9eCOBU.EWN4qZS8Pe8xrKsT.jI8SBI3n0b8lNC',
    NOW(),
    NOW()
),
(
    '55555555-5555-5555-5555-555555555555',
    'Admin',
    'Test',
    'adm@uc.cl',
    'adm@uc.cl',
    'ADM',
    true,
    '$2b$12$T04y1O1OiTAzNG7kEcmBuel.XCxGDcpg2biTqB/RX98fv1gxO8dP2',
    NOW(),
    NOW()
);
