import { useState, useEffect, useContext } from 'react';
import { AuthContext } from '../context/AuthContext'; // Revisa que la ruta sea correcta

export const DashboardDocente = ({ setActiveTab, setCursoSeleccionadoId }) => {
    const { currentUser } = useContext(AuthContext);

    const [cursos, setCursos] = useState([]);
    const [semestres, setSemestres] = useState([]);
    const [loadingSemestres, setLoadingSemestres] = useState(true);
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [errorMsg, setErrorMsg] = useState('');

    const [nombreCurso, setNombreCurso] = useState('');
    const [semestreId, setSemestreId] = useState('');

    useEffect(() => {
        if (currentUser && ['PRO', 'AYU'].includes(currentUser.rol)) {
            // Obtenemos el token (asumiendo que lo guardas en localStorage al hacer login)
            const token = localStorage.getItem('token');
            const opcionesFetch = {
                headers: {
                    Authorization: `Bearer ${token}`,
                    'Content-Type': 'application/json',
                },
            };

            Promise.all([
                fetch('/api/semestres', opcionesFetch).then((res) =>
                    res.ok ? res.json() : []
                ),
                fetch('/api/cursos', opcionesFetch).then((res) =>
                    res.ok ? res.json() : []
                ),
            ])
                .then(([dataSemestres, dataCursos]) => {
                    setSemestres(dataSemestres);
                    setCursos(dataCursos);
                })
                .catch((error) => console.error('Error cargando datos:', error))
                .finally(() => setLoadingSemestres(false));
        }
    }, [currentUser]);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setIsSubmitting(true);
        setErrorMsg('');

        try {
            // 1. Obtenemos el token de tu LocalStorage
            const token = localStorage.getItem('token');

            const response = await fetch('/api/cursos', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    // 2. Agregamos el token a los headers
                    Authorization: `Bearer ${token}`,
                },
                body: JSON.stringify({
                    nombre: nombreCurso,
                    ref_semestre: semestreId,
                }),
            });

            if (response.status === 201) {
                const nuevoCurso = await response.json();
                setCursos([...cursos, nuevoCurso]);
                setNombreCurso('');
                setSemestreId('');
            } else if (response.status === 422) {
                setErrorMsg('Datos inválidos. Verifica el formulario.');
            } else {
                setErrorMsg('Ocurrió un error al crear el curso.');
            }
        } catch (error) {
            console.error('Error en petición POST:', error); // Ahora sí usamos la variable
            setErrorMsg('Error de conexión con el servidor.');
        } finally {
            setIsSubmitting(false);
        }
    };

    const handleVerEstudiantes = (idCurso) => {
        setCursoSeleccionadoId(idCurso);
        setActiveTab(1);
    };

    const handleImportarCSV = (cursoId) => {
        setCursoSeleccionadoId(cursoId);
        setActiveTab(1);
    };

    // Estilos reutilizables (Paleta MakerBox)
    const btnStyle = {
        padding: '8px 16px',
        borderRadius: '8px',
        border: 'none',
        backgroundColor: '#ede9fe',
        color: '#5b21b6',
        fontWeight: '600',
        cursor: 'pointer',
        transition: 'all 0.2s',
        fontSize: '14px',
    };

    if (!currentUser || !['PRO', 'AYU'].includes(currentUser.rol)) {
        return (
            <div
                style={{
                    padding: '20px',
                    textAlign: 'center',
                    color: '#6b7280',
                }}
            >
                <p>
                    Sin acceso. Esta sección es exclusiva para profesores y
                    ayudantes.
                </p>
            </div>
        );
    }

    return (
        <div
            style={{
                padding: '20px',
                width: '100%',
                boxSizing: 'border-box',
                fontFamily: 'Inter, sans-serif',
            }}
        >
            <h2
                style={{
                    color: '#374151',
                    marginBottom: '24px',
                    fontWeight: 600,
                }}
            >
                Gestión de Cursos
            </h2>

            <div
                style={{
                    display: 'flex',
                    gap: '24px',
                    alignItems: 'flex-start',
                }}
            >
                {/* Panel Izquierdo: Crear Curso */}
                <section
                    style={{
                        flex: 1,
                        padding: '24px',
                        backgroundColor: '#f9fafb',
                        borderRadius: '16px',
                        border: '1px solid #e5e7eb',
                    }}
                >
                    <h3
                        style={{
                            margin: '0 0 16px 0',
                            fontSize: '18px',
                            color: '#1f2937',
                        }}
                    >
                        Crear Nuevo Curso
                    </h3>
                    {errorMsg && (
                        <p
                            style={{
                                color: '#ef4444',
                                fontSize: '14px',
                                marginBottom: '16px',
                            }}
                            role="alert"
                        >
                            {errorMsg}
                        </p>
                    )}

                    <form
                        onSubmit={handleSubmit}
                        style={{
                            display: 'flex',
                            flexDirection: 'column',
                            gap: '16px',
                        }}
                    >
                        <div>
                            <label
                                htmlFor="nombre"
                                style={{
                                    display: 'block',
                                    marginBottom: '6px',
                                    fontSize: '14px',
                                    color: '#4b5563',
                                    fontWeight: 500,
                                }}
                            >
                                Nombre del curso:{' '}
                            </label>
                            <input
                                id="nombre"
                                type="text"
                                value={nombreCurso}
                                onChange={(e) => setNombreCurso(e.target.value)}
                                required
                                style={{
                                    width: '100%',
                                    padding: '10px',
                                    borderRadius: '8px',
                                    border: '1px solid #d1d5db',
                                    boxSizing: 'border-box',
                                }}
                            />
                        </div>

                        <div>
                            <label
                                htmlFor="semestre"
                                style={{
                                    display: 'block',
                                    marginBottom: '6px',
                                    fontSize: '14px',
                                    color: '#4b5563',
                                    fontWeight: 500,
                                }}
                            >
                                Semestre:{' '}
                            </label>
                            <select
                                id="semestre"
                                value={semestreId}
                                onChange={(e) => setSemestreId(e.target.value)}
                                required
                                style={{
                                    width: '100%',
                                    padding: '10px',
                                    borderRadius: '8px',
                                    border: '1px solid #d1d5db',
                                    boxSizing: 'border-box',
                                    backgroundColor: 'white',
                                }}
                            >
                                <option value="">Selecciona un semestre</option>
                                {loadingSemestres ? (
                                    <option disabled>Cargando...</option>
                                ) : (
                                    semestres.map((sem) => (
                                        <option
                                            key={sem.id_semestre}
                                            value={sem.id_semestre}
                                        >
                                            {sem.nombre}
                                        </option>
                                    ))
                                )}
                            </select>
                        </div>

                        <button
                            type="submit"
                            disabled={isSubmitting}
                            style={{
                                ...btnStyle,
                                backgroundColor: '#5b21b6',
                                color: 'white',
                                marginTop: '8px',
                            }}
                            onMouseEnter={(e) =>
                                (e.target.style.backgroundColor = '#4c1d95')
                            }
                            onMouseLeave={(e) =>
                                (e.target.style.backgroundColor = '#5b21b6')
                            }
                        >
                            {isSubmitting ? 'Creando...' : 'Crear curso'}
                        </button>
                    </form>
                </section>

                {/* Panel Derecho: Lista de Cursos */}
                <section style={{ flex: 2 }}>
                    <h3
                        style={{
                            margin: '0 0 16px 0',
                            fontSize: '18px',
                            color: '#1f2937',
                        }}
                    >
                        Mis Cursos
                    </h3>
                    {cursos.length === 0 ? (
                        <div
                            style={{
                                padding: '32px',
                                textAlign: 'center',
                                backgroundColor: '#f9fafb',
                                borderRadius: '16px',
                                border: '1px dashed #d1d5db',
                                color: '#6b7280',
                            }}
                        >
                            <p style={{ margin: 0 }}>
                                No hay cursos asignados actualmente.
                            </p>
                        </div>
                    ) : (
                        <div
                            style={{
                                display: 'grid',
                                gridTemplateColumns:
                                    'repeat(auto-fill, minmax(300px, 1fr))',
                                gap: '16px',
                            }}
                        >
                            {cursos.map((curso) => (
                                <div
                                    key={curso.id_curso}
                                    style={{
                                        padding: '20px',
                                        backgroundColor: '#ffffff',
                                        borderRadius: '16px',
                                        border: '1px solid #e5e7eb',
                                        boxShadow: '0 1px 3px rgba(0,0,0,0.05)',
                                    }}
                                >
                                    <h4
                                        style={{
                                            margin: '0 0 4px 0',
                                            color: '#1f2937',
                                            fontSize: '16px',
                                        }}
                                    >
                                        {curso.nombre}
                                    </h4>
                                    <p
                                        style={{
                                            margin: '0 0 16px 0',
                                            color: '#6b7280',
                                            fontSize: '13px',
                                        }}
                                    >
                                        {curso.semestre_nombre ||
                                            'Semestre asignado'}
                                    </p>

                                    <div
                                        style={{ display: 'flex', gap: '8px' }}
                                    >
                                        <button
                                            onClick={() =>
                                                handleVerEstudiantes(curso.id)
                                            }
                                            style={btnStyle}
                                        >
                                            Ver estudiantes
                                        </button>
                                        <button
                                            onClick={() =>
                                                handleImportarCSV(
                                                    curso.id_curso
                                                )
                                            }
                                            style={{
                                                ...btnStyle,
                                                backgroundColor: '#f3f4f6',
                                                color: '#4b5563',
                                            }}
                                        >
                                            Importar CSV
                                        </button>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </section>
            </div>
        </div>
    );
};
