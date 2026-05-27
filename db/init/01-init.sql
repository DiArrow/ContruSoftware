-- ============================================================
-- init.sql — Esquema completo de la base de datos
-- 14 tablas en orden de dependencias (sin FKs primero)
-- Idempotente: DROP CASCADE + CREATE
-- ============================================================

-- ============================================================
-- DROP TABLES (orden inverso de dependencias)
-- ============================================================

DROP TABLE IF EXISTS bloque_reservado CASCADE;
DROP TABLE IF EXISTS reserva CASCADE;
DROP TABLE IF EXISTS uso_impresora CASCADE;
DROP TABLE IF EXISTS inscripcion_ayudantia CASCADE;
DROP TABLE IF EXISTS ayudantia CASCADE;
DROP TABLE IF EXISTS movimiento_stock CASCADE;
DROP TABLE IF EXISTS impresion CASCADE;
DROP TABLE IF EXISTS grupo_estudiante CASCADE;
DROP TABLE IF EXISTS curso CASCADE;
DROP TABLE IF EXISTS bloque_horario CASCADE;
DROP TABLE IF EXISTS articulo CASCADE;
DROP TABLE IF EXISTS estudiante CASCADE;
DROP TABLE IF EXISTS semestre CASCADE;
DROP TABLE IF EXISTS usuario CASCADE;

-- ============================================================
-- CREATE TABLES — sin dependencias (5 tablas)
-- ============================================================

CREATE TABLE usuario (
    id_usuario VARCHAR(36) NOT NULL,
    nombre VARCHAR(255),
    apellido VARCHAR(255),
    correo VARCHAR(255),
    email VARCHAR(255) UNIQUE,
    rol VARCHAR(50),
    estado BOOLEAN DEFAULT true,
    creado_en TIMESTAMP,
    actualizado_en TIMESTAMP,
    CONSTRAINT pk_usuario PRIMARY KEY (id_usuario)
);

CREATE TABLE semestre (
    id_semestre VARCHAR(36) NOT NULL,
    nombre VARCHAR(255),
    fecha_inicio DATE,
    fecha_fin DATE,
    estado BOOLEAN,
    creado_en TIMESTAMP,
    actualizado_en TIMESTAMP,
    CONSTRAINT pk_semestre PRIMARY KEY (id_semestre)
);

CREATE TABLE estudiante (
    id_estudiante VARCHAR(36) NOT NULL,
    nombre VARCHAR(255),
    apellido VARCHAR(255),
    correo VARCHAR(255),
    CONSTRAINT pk_estudiante PRIMARY KEY (id_estudiante)
);

CREATE TABLE articulo (
    id_articulo VARCHAR(36) NOT NULL,
    nombre_articulo VARCHAR(255),
    stock_actual INTEGER,
    stock_minimo INTEGER,
    alerta_stock BOOLEAN,
    actualizado_en TIMESTAMP,
    CONSTRAINT pk_articulo PRIMARY KEY (id_articulo)
);

CREATE TABLE bloque_horario (
    id_bloque_horario VARCHAR(36) NOT NULL,
    dia_semana VARCHAR(20),
    hora_inicio TIME,
    hora_fin TIME,
    CONSTRAINT pk_bloque_horario PRIMARY KEY (id_bloque_horario)
);

-- ============================================================
-- CREATE TABLES — dependencias de un nivel (4 tablas)
-- ============================================================

CREATE TABLE curso (
    id_curso VARCHAR(36) NOT NULL,
    nombre VARCHAR(255),
    ref_semestre VARCHAR(36),
    bloque_id VARCHAR(36),
    creado_en TIMESTAMP,
    actualizado_en TIMESTAMP,
    CONSTRAINT pk_curso PRIMARY KEY (id_curso),
    CONSTRAINT fk_curso_semestre FOREIGN KEY (ref_semestre)
    REFERENCES semestre (id_semestre)
);

CREATE TABLE grupo_estudiante (
    ref_grupo VARCHAR(36) NOT NULL,
    ref_estudiante VARCHAR(36) NOT NULL,
    CONSTRAINT pk_grupo_estudiante PRIMARY KEY (ref_grupo, ref_estudiante),
    CONSTRAINT fk_grupo_est_estudiante FOREIGN KEY (ref_estudiante)
    REFERENCES estudiante (id_estudiante)
);

CREATE TABLE impresion (
    id_impresion VARCHAR(36) NOT NULL,
    ref_usuario VARCHAR(36),
    ref_articulo VARCHAR(36),
    cantidad INTEGER,
    fecha_impresion TIMESTAMP,
    estado_impresion VARCHAR(50),
    CONSTRAINT pk_impresion PRIMARY KEY (id_impresion),
    CONSTRAINT fk_imp_usuario FOREIGN KEY (ref_usuario)
    REFERENCES usuario (id_usuario),
    CONSTRAINT fk_imp_articulo FOREIGN KEY (ref_articulo)
    REFERENCES articulo (id_articulo)
);

CREATE TABLE movimiento_stock (
    id_movimiento VARCHAR(36) NOT NULL,
    ref_articulo VARCHAR(36),
    tipo_movimiento VARCHAR(50),
    cantidad INTEGER,
    fecha_movimiento TIMESTAMP,
    CONSTRAINT pk_movimiento_stock PRIMARY KEY (id_movimiento),
    CONSTRAINT fk_mov_articulo FOREIGN KEY (ref_articulo)
    REFERENCES articulo (id_articulo)
);

-- ============================================================
-- CREATE TABLES — dependencias multi-nivel (5 tablas)
-- ============================================================

CREATE TABLE ayudantia (
    id_ayudantia VARCHAR(36) NOT NULL,
    nombre_ayudantia VARCHAR(255),
    ref_curso VARCHAR(36),
    ref_grupo VARCHAR(36),
    ref_ayudante VARCHAR(36),
    estado VARCHAR(50),
    CONSTRAINT pk_ayudantia PRIMARY KEY (id_ayudantia),
    CONSTRAINT fk_ayudantia_curso FOREIGN KEY (ref_curso)
    REFERENCES curso (id_curso)
);

CREATE TABLE inscripcion_ayudantia (
    ref_ayudantia VARCHAR(36) NOT NULL,
    ref_estudiante VARCHAR(36) NOT NULL,
    fecha_inscripcion TIMESTAMP,
    estado_inscripcion VARCHAR(50),
    CONSTRAINT pk_inscripcion PRIMARY KEY (ref_ayudantia, ref_estudiante),
    CONSTRAINT fk_ins_ayudantia FOREIGN KEY (ref_ayudantia)
    REFERENCES ayudantia (id_ayudantia),
    CONSTRAINT fk_ins_estudiante FOREIGN KEY (ref_estudiante)
    REFERENCES estudiante (id_estudiante)
);

CREATE TABLE uso_impresora (
    id_uso_impresora VARCHAR(36) NOT NULL,
    ref_impresora VARCHAR(36),
    ref_estudiante VARCHAR(36),
    ref_ayudantia VARCHAR(36),
    fecha_uso TIMESTAMP,
    CONSTRAINT pk_uso_impresora PRIMARY KEY (id_uso_impresora),
    CONSTRAINT fk_uso_estudiante FOREIGN KEY (ref_estudiante)
    REFERENCES estudiante (id_estudiante),
    CONSTRAINT fk_uso_ayudantia FOREIGN KEY (ref_ayudantia)
    REFERENCES ayudantia (id_ayudantia)
);

CREATE TABLE reserva (
    id_reserva VARCHAR(36) NOT NULL,
    fecha_reserva DATE,
    estado_reserva VARCHAR(50),
    ref_usuario VARCHAR(36),
    ref_ayudantia VARCHAR(36),
    CONSTRAINT pk_reserva PRIMARY KEY (id_reserva),
    CONSTRAINT fk_res_usuario FOREIGN KEY (ref_usuario)
    REFERENCES usuario (id_usuario),
    CONSTRAINT fk_res_ayudantia FOREIGN KEY (ref_ayudantia)
    REFERENCES ayudantia (id_ayudantia)
);

CREATE TABLE bloque_reservado (
    bloque_id VARCHAR(36) NOT NULL,
    reserva_id VARCHAR(36) NOT NULL,
    CONSTRAINT pk_bloque_reservado PRIMARY KEY (bloque_id, reserva_id),
    CONSTRAINT fk_br_bloque FOREIGN KEY (bloque_id)
    REFERENCES bloque_horario (id_bloque_horario),
    CONSTRAINT fk_br_reserva FOREIGN KEY (reserva_id)
    REFERENCES reserva (id_reserva)
);
