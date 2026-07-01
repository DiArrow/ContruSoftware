import { useState, useEffect, useContext } from 'react';
import { AuthContext } from '../context/AuthContext';
import { apiGet } from '../api/client';

export const DashboardEstudiante = () => {
    const { currentUser } = useContext(AuthContext);
    const [cursos, setCursos] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        if (currentUser?.rol === 'EST') {
            apiGet('cursos/mis-cursos')
                .then((data) => setCursos(data))
                .catch((err) => setError(err.message))
                .finally(() => setLoading(false));
        } else {
            setLoading(false);
        }
    }, [currentUser]);

    if (loading) {
        return (
            <div
                style={{
                    padding: '20px',
                    textAlign: 'center',
                    color: '#6b7280',
                }}
            >
                Cargando...
            </div>
        );
    }

    if (error) {
        return (
            <div
                style={{
                    padding: '20px',
                    textAlign: 'center',
                    color: '#ef4444',
                }}
            >
                {error}
            </div>
        );
    }

    if (!currentUser || currentUser.rol !== 'EST') {
        return (
            <div
                style={{
                    padding: '20px',
                    textAlign: 'center',
                    color: '#6b7280',
                }}
            >
                Sin acceso. Esta sección es exclusiva para estudiantes.
            </div>
        );
    }

    return (
        <div
            style={{
                padding: '20px',
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
                Mis Cursos
            </h2>
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
                    <p>No estás inscrito en ningún curso.</p>
                </div>
            ) : (
                <div
                    style={{
                        display: 'grid',
                        gridTemplateColumns:
                            'repeat(auto-fill, minmax(280px, 1fr))',
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
                            <h3
                                style={{
                                    margin: '0 0 8px 0',
                                    color: '#1f2937',
                                    fontSize: '18px',
                                }}
                            >
                                {curso.nombre}
                            </h3>
                            <p
                                style={{
                                    margin: '0 0 16px 0',
                                    color: '#6b7280',
                                    fontSize: '14px',
                                }}
                            >
                                {curso.semestre_nombre ||
                                    'Semestre no asignado'}
                            </p>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};
