import { useState, useContext } from 'react';
import { AuthContext } from '../context/AuthContext';

export default function UserRegistrationForm() {
    // 1. Cambia aquí para obtener 'currentUser'
    const { currentUser } = useContext(AuthContext);

    // 2. Si quieres usar 'user' como variable interna para el resto del código, asígnalo así:
    const user = currentUser;

    const [formData, setFormData] = useState({
        nombre: '',
        apellido: '',
        email: '',
        password: '',
        rol: 'EST',
    });

    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [success, setSuccess] = useState(null);

    // AGREGA ESTA LÍNEA AQUÍ:
    console.log('Datos del usuario:', user);

    // Criterio de Seguridad: Si no existe el usuario o no es ADM, bloqueamos el renderizado
    if (!user || user.rol !== 'ADM') {
        return (
            <div
                style={{
                    padding: '20px',
                    textAlign: 'center',
                    color: '#6b7280',
                }}
            >
                <p>
                    Sin acceso. Esta sección es exclusiva para administradores.
                </p>
            </div>
        );
    }

    const handleChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value,
        });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();

        // Validación en cliente: todos los campos obligatorios
        if (
            !formData.nombre.trim() ||
            !formData.apellido.trim() ||
            !formData.email.trim() ||
            !formData.password.trim() ||
            !formData.rol
        ) {
            setError('Todos los campos son obligatorios');
            setSuccess(null);
            return;
        }

        setLoading(true);
        setError(null);
        setSuccess(null);

        try {
            const token = localStorage.getItem('token') || '';
            const response = await fetch('/api/admin/usuarios', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    Authorization: `Bearer ${token}`,
                },
                body: JSON.stringify(formData),
            });

            // Intentamos extraer detalles (como hace FastAPI en sus errores de validación)
            let data = {};
            try {
                data = await response.json();
            } catch (jsonErr) {
                console.error('Error al parsear JSON:', jsonErr);
            }

            // Manejo de códigos HTTP según los criterios de aceptación
            if (response.status === 201 || response.ok) {
                setSuccess(`Usuario ${formData.nombre} creado con éxito`);
                setFormData({
                    nombre: '',
                    apellido: '',
                    email: '',
                    password: '',
                    rol: 'EST',
                });
            } else if (response.status === 409) {
                setError('El email ya se encuentra registrado');
            } else if (response.status === 422) {
                setError(
                    data.detail || 'Error de validación en los datos enviados'
                );
            } else {
                setError(
                    data.detail ||
                        'Error inesperado al intentar crear el usuario'
                );
            }
        } catch (err) {
            console.error('Error de conexión:', err); // <--- Ahora sí la usas
            setError('Error de conexión con el servidor.');
        } finally {
            setLoading(false);
        }
    };

    const inputStyle = {
        width: '100%',
        padding: '8px 12px',
        borderRadius: '8px',
        border: '1px solid #ddd',
        boxSizing: 'border-box',
        marginTop: '4px',
    };
    const labelStyle = {
        display: 'block',
        fontSize: '13px',
        fontWeight: '600',
        color: '#374151',
    };

    return (
        <div
            style={{
                maxWidth: '460px',
                margin: '20px auto',
                padding: '30px',
                border: '1px solid #e5e7eb',
                borderRadius: '16px',
                backgroundColor: '#fafafa',
            }}
        >
            <h2
                style={{
                    marginTop: 0,
                    marginBottom: '20px',
                    color: '#111827',
                    fontSize: '20px',
                }}
            >
                Registrar Nuevo Usuario
            </h2>

            {error && (
                <div
                    style={{
                        color: '#dc2626',
                        backgroundColor: '#fee2e2',
                        padding: '10px',
                        borderRadius: '8px',
                        marginBottom: '15px',
                        fontSize: '14px',
                        fontWeight: 500,
                    }}
                >
                    {error}
                </div>
            )}

            {success && (
                <div
                    style={{
                        color: '#16a34a',
                        backgroundColor: '#dcfce7',
                        padding: '10px',
                        borderRadius: '8px',
                        marginBottom: '15px',
                        fontSize: '14px',
                        fontWeight: 500,
                    }}
                >
                    {success}
                </div>
            )}

            <form
                onSubmit={handleSubmit}
                noValidate
                style={{
                    display: 'flex',
                    flexDirection: 'column',
                    gap: '15px',
                }}
            >
                <div>
                    <label htmlFor="nombre" style={labelStyle}>
                        Nombre
                    </label>
                    <input
                        type="text"
                        id="nombre"
                        name="nombre"
                        value={formData.nombre}
                        onChange={handleChange}
                        style={inputStyle}
                    />
                </div>

                <div>
                    <label htmlFor="apellido" style={labelStyle}>
                        Apellido
                    </label>
                    <input
                        type="text"
                        id="apellido"
                        name="apellido"
                        value={formData.apellido}
                        onChange={handleChange}
                        style={inputStyle}
                    />
                </div>

                <div>
                    <label htmlFor="email" style={labelStyle}>
                        Email
                    </label>
                    <input
                        type="email"
                        id="email"
                        name="email"
                        value={formData.email}
                        onChange={handleChange}
                        style={inputStyle}
                        required
                    />
                </div>

                <div>
                    <label htmlFor="password" style={labelStyle}>
                        Contraseña
                    </label>
                    <input
                        type="password"
                        id="password"
                        name="password"
                        value={formData.password}
                        onChange={handleChange}
                        style={inputStyle}
                    />
                </div>

                <div>
                    <label htmlFor="rol" style={labelStyle}>
                        Rol
                    </label>
                    <select
                        id="rol"
                        name="rol"
                        value={formData.rol}
                        onChange={handleChange}
                        style={{ ...inputStyle, backgroundColor: '#fff' }}
                    >
                        <option value="EST">Estudiante (EST)</option>
                        <option value="PRO">Profesor (PRO)</option>
                        <option value="AYU">Ayudante (AYU)</option>
                        <option value="ADM">Administrador (ADM)</option>
                    </select>
                </div>

                <button
                    type="submit"
                    disabled={loading}
                    style={{
                        marginTop: '10px',
                        padding: '10px 20px',
                        backgroundColor: loading ? '#9ca3af' : '#5b21b6',
                        color: 'white',
                        border: 'none',
                        borderRadius: '8px',
                        cursor: loading ? 'not-allowed' : 'pointer',
                        fontWeight: '600',
                        width: '100%',
                        transition: 'background-color 0.2s',
                    }}
                >
                    {loading ? 'Creando usuario...' : 'Crear Usuario'}
                </button>
            </form>
        </div>
    );
}
