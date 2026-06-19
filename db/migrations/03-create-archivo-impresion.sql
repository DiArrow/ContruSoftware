-- Migración para crear la tabla archivo_impresion

CREATE TABLE IF NOT EXISTS archivo_impresion (
    id_archivo VARCHAR(36) PRIMARY KEY,
    ref_impresion VARCHAR(36) NOT NULL,
    nombre_archivo VARCHAR(255) NOT NULL,
    contenido BYTEA NOT NULL,
    CONSTRAINT fk_archivo_impresion_impresion
    FOREIGN KEY (ref_impresion)
    REFERENCES impresion (id_impresion)
    ON DELETE CASCADE
);
