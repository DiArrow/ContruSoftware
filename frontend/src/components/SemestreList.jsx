import { useEffect, useState } from 'react';
import { apiGet } from '../api/client';

export default function SemestreList({
    asSelect,
    value,
    onChange,
    refreshTrigger,
}) {
    const [semestres, setSemestres] = useState([]);
    const [error, setError] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        apiGet('semestres')
            .then(setSemestres)
            .catch((e) => setError(e.message))
            .finally(() => setLoading(false));
    }, [refreshTrigger]);

    if (loading) return <p aria-label="cargando">Cargando semestres...</p>;
    if (error) return <p>Error: {error}</p>;

    if (asSelect) {
        return (
            <select
                value={value}
                onChange={onChange}
                required
                data-testid="semestre-select"
            >
                <option value="">Selecciona un semestre</option>
                {semestres.map((s) => (
                    <option key={s.id_semestre} value={s.id_semestre}>
                        {s.nombre} ({s.fecha_inicio} → {s.fecha_fin})
                    </option>
                ))}
            </select>
        );
    }

    return (
        <div className="table-responsive">
            <table className="table">
                <thead>
                    <tr>
                        <th>Nombre</th>
                        <th>Inicio</th>
                        <th>Fin</th>
                        <th>Estado</th>
                    </tr>
                </thead>
                <tbody>
                    {semestres.length === 0 ? (
                        <tr>
                            <td colSpan="4" style={{ textAlign: 'center' }}>
                                No hay semestres registrados
                            </td>
                        </tr>
                    ) : (
                        semestres.map((s) => (
                            <tr key={s.id_semestre} data-testid="semestre-row">
                                <td>{s.nombre}</td>
                                <td>{s.fecha_inicio}</td>
                                <td>{s.fecha_fin}</td>
                                <td>
                                    <span
                                        className={`badge ${s.estado ? 'bg-success' : 'bg-secondary'}`}
                                    >
                                        {s.estado ? 'Activo' : 'Inactivo'}
                                    </span>
                                </td>
                            </tr>
                        ))
                    )}
                </tbody>
            </table>
        </div>
    );
}
