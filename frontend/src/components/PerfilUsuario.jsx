import { useState, useContext } from 'react';
import { AuthContext } from '../context/AuthContext';
import { apiPut } from '../api/client';

function esEmailValido(email) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

const PerfilUsuarioForm = ({ currentUser }) => {
    const [form, setForm] = useState({
        nombre: currentUser?.nombre || '',
        apellido: currentUser?.apellido || '',
        email: currentUser?.email || '',
    });
    const [guardando, setGuardando] = useState(false);
    const [mensaje, setMensaje] = useState('');
    const [error, setError] = useState('');

    const handleChange = (e) => {
        const { name, value } = e.target;
        setForm((prev) => ({ ...prev, [name]: value }));
        setMensaje('');
        setError('');
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setMensaje('');
        setError('');

        if (!esEmailValido(form.email)) {
            setError('El correo no es válido.');
            return;
        }

        setGuardando(true);
        try {
            await apiPut('auth/me', form);
            setMensaje('Perfil actualizado correctamente.');
        } catch (err) {
            setError(err.message || 'No se pudo actualizar el perfil.');
        } finally {
            setGuardando(false);
        }
    };

    if (!currentUser) {
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

    return (
        <div
            style={{
                padding: '20px',
                fontFamily: 'Inter, sans-serif',
                maxWidth: '480px',
            }}
        >
            <h2
                style={{
                    color: '#374151',
                    marginBottom: '24px',
                    fontWeight: 600,
                }}
            >
                Mi Perfil
            </h2>

            <form onSubmit={handleSubmit} noValidate>
                <div style={{ marginBottom: '16px' }}>
                    <label
                        htmlFor="nombre"
                        style={{
                            display: 'block',
                            marginBottom: '6px',
                            fontSize: '14px',
                            fontWeight: 500,
                            color: '#374151',
                        }}
                    >
                        Nombre
                    </label>
                    <input
                        id="nombre"
                        name="nombre"
                        type="text"
                        value={form.nombre}
                        onChange={handleChange}
                        style={{
                            width: '100%',
                            padding: '10px 12px',
                            borderRadius: '10px',
                            border: '1px solid #d1d5db',
                            fontSize: '14px',
                            boxSizing: 'border-box',
                        }}
                    />
                </div>

                <div style={{ marginBottom: '16px' }}>
                    <label
                        htmlFor="apellido"
                        style={{
                            display: 'block',
                            marginBottom: '6px',
                            fontSize: '14px',
                            fontWeight: 500,
                            color: '#374151',
                        }}
                    >
                        Apellido
                    </label>
                    <input
                        id="apellido"
                        name="apellido"
                        type="text"
                        value={form.apellido}
                        onChange={handleChange}
                        style={{
                            width: '100%',
                            padding: '10px 12px',
                            borderRadius: '10px',
                            border: '1px solid #d1d5db',
                            fontSize: '14px',
                            boxSizing: 'border-box',
                        }}
                    />
                </div>

                <div style={{ marginBottom: '24px' }}>
                    <label
                        htmlFor="email"
                        style={{
                            display: 'block',
                            marginBottom: '6px',
                            fontSize: '14px',
                            fontWeight: 500,
                            color: '#374151',
                        }}
                    >
                        Correo electrónico
                    </label>
                    <input
                        id="email"
                        name="email"
                        type="email"
                        value={form.email}
                        onChange={handleChange}
                        style={{
                            width: '100%',
                            padding: '10px 12px',
                            borderRadius: '10px',
                            border: '1px solid #d1d5db',
                            fontSize: '14px',
                            boxSizing: 'border-box',
                        }}
                    />
                </div>

                <button
                    type="submit"
                    disabled={guardando}
                    style={{
                        padding: '10px 20px',
                        backgroundColor: guardando ? '#c4b5fd' : '#5b21b6',
                        color: '#ffffff',
                        border: 'none',
                        borderRadius: '10px',
                        fontSize: '14px',
                        fontWeight: 600,
                        cursor: guardando ? 'not-allowed' : 'pointer',
                    }}
                >
                    {guardando ? 'Guardando...' : 'Guardar cambios'}
                </button>

                {mensaje && (
                    <p
                        style={{
                            marginTop: '16px',
                            color: '#166534',
                            fontSize: '14px',
                        }}
                    >
                        {mensaje}
                    </p>
                )}

                {error && (
                    <p
                        style={{
                            marginTop: '16px',
                            color: '#991b1b',
                            fontSize: '14px',
                        }}
                    >
                        {error}
                    </p>
                )}
            </form>
        </div>
    );
};

export const PerfilUsuario = () => {
    const { currentUser } = useContext(AuthContext);
    return (
        <PerfilUsuarioForm
            key={currentUser?.id || 'no-user'}
            currentUser={currentUser}
        />
    );
};
