-- ============================================================
-- Migración: agrega columnas email y estado a la tabla usuario
-- ============================================================

ALTER TABLE usuario ADD COLUMN IF NOT EXISTS email VARCHAR(255);
ALTER TABLE usuario ADD COLUMN IF NOT EXISTS estado BOOLEAN DEFAULT true;
CREATE UNIQUE INDEX IF NOT EXISTS idx_usuario_email ON usuario(email);
