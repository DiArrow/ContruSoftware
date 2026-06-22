-- Migration: agrega columna ref_profesor a curso
ALTER TABLE curso ADD COLUMN IF NOT EXISTS ref_profesor VARCHAR(36);
ALTER TABLE curso ADD CONSTRAINT IF NOT EXISTS fk_curso_profesor
    FOREIGN KEY (ref_profesor) REFERENCES usuario (id_usuario);
CREATE INDEX IF NOT EXISTS idx_curso_ref_profesor ON curso (ref_profesor);
