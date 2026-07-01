import { useState } from 'react';
import { apiPost } from '../api/client';
import { useAuth } from '../context/AuthContext';

export default function SemestreFrom({ onCreated }) {
    const { currentUser } = useAuth();
    const [form, setForm] = useState({
        nombre: '',
        fecha_inicio: '',
        fecha_fin: '',
    });
    const [error, setError] = useState(null);
    const [submitting, setSubmitting] = useState(false);

    const puedeCrear = currentUser && ['ADM', 'AYU'].includes(currentUser.rol);

    if (!puedeCrear) {
        return (
            <p className="alert alert-warning">
                No tienes permisos para crear semestres.
            </p>
        );
    }

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError(null);
        setSubmitting(true);
        try {
            const nuevo = await apiPost('semestres', form);
            onCreated?.(nuevo);
            setForm({ nombre: '', fecha_inicio: '', fecha_fin: '' });
        } catch (err) {
            setError(err.message || 'Error al crear el semestre');
        } finally {
            setSubmitting(false);
        }
    };
    return (
        <div className="card p-3 mb-4">
            <h3>Crear Nuevo Semestre</h3>
            <form onSubmit={handleSubmit} data-testid="semestre-form">
                <div className="mb-3">
                    <label className="form-label">Nombre del Semestre</label>
                    <input
                        className="form-control"
                        placeholder="Nombre (ej: 2026-1)"
                        value={form.nombre}
                        onChange={(e) =>
                            setForm({ ...form, nombre: e.target.value })
                        }
                        required
                    />
                </div>
                <div className="mb-3">
                    <label className="form-label">Fecha de Inicio</label>
                    <input
                        type="date"
                        className="form-control"
                        value={form.fecha_inicio}
                        onChange={(e) =>
                            setForm({ ...form, fecha_inicio: e.target.value })
                        }
                        required
                    />
                </div>
                <div className="mb-3">
                    <label className="form-label">Fecha de Término</label>
                    <input
                        type="date"
                        className="form-control"
                        value={form.fecha_fin}
                        onChange={(e) =>
                            setForm({ ...form, fecha_fin: e.target.value })
                        }
                        required
                    />
                </div>
                {error && (
                    <p className="text-danger" data-testid="form-error">
                        {error}
                    </p>
                )}
                <button
                    type="submit"
                    className="btn btn-primary"
                    disabled={submitting}
                >
                    {submitting ? 'Creando...' : 'Crear semestre'}
                </button>
            </form>
        </div>
    );
}
