-- Migration: agrega columna ref_profesor a curso
ALTER TABLE curso ADD COLUMN IF NOT EXISTS ref_profesor VARCHAR(36);
CREATE INDEX IF NOT EXISTS idx_curso_ref_profesor ON curso (ref_profesor);
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'fk_curso_profesor'
    ) THEN
        ALTER TABLE curso ADD CONSTRAINT fk_curso_profesor
            FOREIGN KEY (ref_profesor) REFERENCES usuario (id_usuario);
    END IF;
END $$;
