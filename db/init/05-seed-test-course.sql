-- ============================================================
-- Seed: curso de prueba para aceptación + estudiante inscrito
-- ============================================================

-- Curso de prueba
INSERT INTO curso (
    id_curso,
    nombre,
    ref_semestre,
    ref_profesor,
    creado_en,
    actualizado_en
) VALUES (
    'b0000001-0000-0000-0000-000000000001',
    'Curso de Prueba Aceptación',
    'a0000001-0000-0000-0000-000000000002',
    '44444444-4444-4444-4444-444444444444',
    NOW(),
    NOW()
);

-- Estudiante de prueba (vinculado al usuario seed EST)
INSERT INTO estudiante (
    id_estudiante,
    nombre,
    apellido,
    correo
) VALUES (
    '22222222-2222-2222-2222-222222222222',
    'Estudiante',
    'Test',
    'est@uc.cl'
) ON CONFLICT (id_estudiante) DO NOTHING;

-- Inscripción del estudiante en el curso de prueba
INSERT INTO grupo_estudiante (
    ref_grupo,
    ref_estudiante
) VALUES (
    'b0000001-0000-0000-0000-000000000001',
    '22222222-2222-2222-2222-222222222222'
) ON CONFLICT (ref_grupo, ref_estudiante) DO NOTHING;
