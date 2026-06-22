"""Tests extendidos para el modelo Curso — relación con profesor.

Valida que la relación ``profesor`` en Curso y ``cursos_profesor`` en
Usuario funcionen correctamente con datos reales en PostgreSQL.
"""

import pytest
from sqlalchemy.orm import joinedload

from models.curso import Curso
from models.usuario import Usuario


class TestCursoProfesorRelationship:
    """Verifica la relación entre Curso y Usuario (PRO) a nivel BD."""

    @pytest.mark.integration
    def test_asignar_profesor_a_curso(self, db_session):
        """Un usuario con rol PRO debe poder asignarse como profesor de un curso."""
        profesor = Usuario(
            id_usuario="00000000-0000-0000-0000-000000000001",
            nombre="Juan",
            apellido="Profe",
            correo="juan.profe@uc.cl",
            email="juan.profe@uc.cl",
            rol="PRO",
        )
        db_session.add(profesor)
        db_session.flush()

        curso = Curso(
            id_curso="00000000-0000-0000-0000-000000000010",
            nombre="Matemáticas",
            bloque_id="B1",
        )
        curso.profesor = profesor
        db_session.add(curso)
        db_session.flush()

        assert curso.profesor is profesor
        assert curso.profesor.rol == "PRO"

    @pytest.mark.integration
    def test_relacion_inversa_cursos_profesor(self, db_session):
        """Un usuario PRO debe poder listar sus cursos desde ``cursos_profesor``."""
        profesor = Usuario(
            id_usuario="00000000-0000-0000-0000-000000000002",
            nombre="Maria",
            apellido="Docente",
            correo="maria.docente@uc.cl",
            email="maria.docente@uc.cl",
            rol="PRO",
        )
        db_session.add(profesor)
        db_session.flush()

        curso1 = Curso(
            id_curso="00000000-0000-0000-0000-000000000020",
            nombre="Física",
            bloque_id="B2",
            ref_profesor=profesor.id_usuario,
        )
        curso2 = Curso(
            id_curso="00000000-0000-0000-0000-000000000021",
            nombre="Química",
            bloque_id="B3",
            ref_profesor=profesor.id_usuario,
        )
        db_session.add_all([curso1, curso2])
        db_session.flush()
        db_session.expire_all()

        # Volver a cargar con la relación
        prof = (
            db_session.query(Usuario)
            .options(joinedload(Usuario.cursos_profesor))
            .filter(Usuario.id_usuario == profesor.id_usuario)
            .one()
        )
        ids = {c.id_curso for c in prof.cursos_profesor}
        assert ids == {curso1.id_curso, curso2.id_curso}

    @pytest.mark.integration
    def test_curso_sin_profesor_es_none(self, db_session):
        """Un curso sin profesor debe tener ``profesor = None``."""
        curso = Curso(
            id_curso="00000000-0000-0000-0000-000000000030",
            nombre="Sin Profesor",
            bloque_id="B4",
        )
        db_session.add(curso)
        db_session.flush()

        assert curso.profesor is None

    @pytest.mark.integration
    def test_validacion_rol_pro_al_asignar_profesor(self, db_session):
        """Asignar un usuario sin rol PRO como profesor debe lanzar ValueError."""
        estudiante = Usuario(
            id_usuario="00000000-0000-0000-0000-000000000003",
            nombre="Alumno",
            apellido="Test",
            correo="alumno.test@uc.cl",
            email="alumno.test@uc.cl",
            rol="EST",
        )
        db_session.add(estudiante)
        db_session.flush()

        curso = Curso(
            id_curso="00000000-0000-0000-0000-000000000040",
            nombre="Curso con Estudiante",
            bloque_id="B5",
        )
        db_session.add(curso)
        db_session.flush()

        with pytest.raises(ValueError, match="El profesor debe tener rol PRO"):
            curso.profesor = estudiante
            db_session.flush()

    @pytest.mark.integration
    def test_asignar_profesor_existente_por_ref_directa(self, db_session):
        """Asignar profesor mediante ref_profesor debe funcionar y ser navegable."""
        profesor = Usuario(
            id_usuario="00000000-0000-0000-0000-000000000004",
            nombre="Carlos",
            apellido="Profe",
            correo="carlos.profe@uc.cl",
            email="carlos.profe@uc.cl",
            rol="PRO",
        )
        db_session.add(profesor)
        db_session.flush()

        curso = Curso(
            id_curso="00000000-0000-0000-0000-000000000050",
            nombre="Programación",
            bloque_id="B6",
            ref_profesor=profesor.id_usuario,
        )
        db_session.add(curso)
        db_session.flush()
        db_session.expire_all()

        # La relación se debe poder navegar aunque se asignó por FK directa
        curs = db_session.get(Curso, curso.id_curso)
        assert curs.profesor is not None
        assert curs.profesor.id_usuario == profesor.id_usuario
        assert curs.profesor.rol == "PRO"
