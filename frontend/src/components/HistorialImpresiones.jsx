import { useState, useEffect, useContext } from 'react';
import { AuthContext } from '../context/AuthContext';
import { apiGet } from '../api/client';

const ESTADO_COLORES = {
    Completada: { backgroundColor: '#dcfce7', color: '#166534' },
    Pendiente: { backgroundColor: '#fef9c3', color: '#854d0e' },
    Rechazada: { backgroundColor: '#fee2e2', color: '#991b1b' },
    'En proceso': { backgroundColor: '#dbeafe', color: '#1e40af' },
};

function formatearFecha(fecha) {
    if (!fecha) return '—';
    const date = new Date(fecha);
    if (Number.isNaN(date.getTime())) return fecha;
    const dia = String(date.getDate()).padStart(2, '0');
    const mes = String(date.getMonth() + 1).padStart(2, '0');
    const anio = date.getFullYear();
    return `${dia}/${mes}/${anio}`;
}

export const HistorialImpresiones = () => {
    const { currentUser } = useContext(AuthContext);
    const [impresiones, setImpresiones] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        if (currentUser?.rol === 'EST' || currentUser?.rol === 'SOL') {
            apiGet('impresiones/mias')
                .then((data) => setImpresiones(data))
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

    if (!currentUser || (currentUser.rol !== 'EST' && currentUser.rol !== 'SOL')) {
        return (
            <div
                style={{
                    padding: '20px',
                    textAlign: 'center',
                    color: '#6b7280',
                }}
            >
                Sin acceso. Esta sección es exclusiva para estudiantes y solicitantes.
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
                Historial de Impresiones
            </h2>
            {impresiones.length === 0 ? (
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
                    <p>Sin solicitudes de impresión.</p>
                </div>
            ) : (
                <div
                    style={{
                        overflowX: 'auto',
                        backgroundColor: '#ffffff',
                        borderRadius: '16px',
                        border: '1px solid #e5e7eb',
                        boxShadow: '0 1px 3px rgba(0,0,0,0.05)',
                    }}
                >
                    <table
                        style={{
                            width: '100%',
                            borderCollapse: 'collapse',
                        }}
                    >
                        <thead>
                            <tr
                                style={{
                                    backgroundColor: '#f9fafb',
                                    borderBottom: '1px solid #e5e7eb',
                                }}
                            >
                                <th
                                    style={{
                                        padding: '16px',
                                        textAlign: 'left',
                                        fontSize: '14px',
                                        fontWeight: 600,
                                        color: '#6b7280',
                                    }}
                                >
                                    Archivo
                                </th>
                                <th
                                    style={{
                                        padding: '16px',
                                        textAlign: 'left',
                                        fontSize: '14px',
                                        fontWeight: 600,
                                        color: '#6b7280',
                                    }}
                                >
                                    Estado
                                </th>
                                <th
                                    style={{
                                        padding: '16px',
                                        textAlign: 'left',
                                        fontSize: '14px',
                                        fontWeight: 600,
                                        color: '#6b7280',
                                    }}
                                >
                                    Fecha
                                </th>
                            </tr>
                        </thead>
                        <tbody>
                            {impresiones.map((imp) => {
                                const estilo =
                                    ESTADO_COLORES[imp.estado] || {
                                        backgroundColor: '#f3f4f6',
                                        color: '#374151',
                                    };
                                return (
                                    <tr
                                        key={imp.id_impresion}
                                        style={{
                                            borderBottom:
                                                '1px solid #f3f4f6',
                                        }}
                                    >
                                        <td
                                            style={{
                                                padding: '16px',
                                                fontSize: '14px',
                                                color: '#1f2937',
                                            }}
                                        >
                                            {imp.nombre_archivo || '—'}
                                        </td>
                                        <td style={{ padding: '16px' }}>
                                            <span
                                                style={{
                                                    display: 'inline-block',
                                                    padding:
                                                        '6px 12px',
                                                    borderRadius: '9999px',
                                                    fontSize: '12px',
                                                    fontWeight: 600,
                                                    ...estilo,
                                                }}
                                            >
                                                {imp.estado}
                                            </span>
                                        </td>
                                        <td
                                            style={{
                                                padding: '16px',
                                                fontSize: '14px',
                                                color: '#6b7280',
                                            }}
                                        >
                                            {formatearFecha(
                                                imp.fecha_solicitud
                                            )}
                                        </td>
                                    </tr>
                                );
                            })}
                        </tbody>
                    </table>
                </div>
            )}
        </div>
    );
};
