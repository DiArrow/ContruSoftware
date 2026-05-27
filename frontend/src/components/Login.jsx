import { useState } from 'react';
import { useAuth } from '../context/AuthContext';

const IconLogin = () => (
    <svg
        width="100"
        height="100"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
        color="#5b21b6"
    >
        <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z" />
        <polyline points="3.27 6.96 12 12.01 20.73 6.96" />
        <line x1="12" y1="22.08" x2="12" y2="12" />
    </svg>
);

export default function Login() {
    const { login } = useAuth();
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [isLoading, setIsLoading] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');

        if (!email.trim() || !password.trim()) {
            setError('Por favor complete todos los campos');
            return;
        }

        setIsLoading(true);
        try {
            await login(email, password);
        } catch (err) {
            setError(err.message || 'Error de conexión');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div
            style={{
                height: '100vh',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                backgroundColor: '#f3f4f6',
                fontFamily: 'Inter, sans-serif',
            }}
        >
            <form
                onSubmit={handleSubmit}
                style={{
                    backgroundColor: '#ffffff',
                    padding: '40px',
                    borderRadius: '24px',
                    boxShadow: '0 10px 25px rgba(0,0,0,0.1)',
                    textAlign: 'center',
                    width: '350px',
                    height: '400px',
                    display: 'flex',
                    flexDirection: 'column',
                    justifyContent: 'center',
                }}
            >
                <h1 style={{ color: '#5b21b6', marginBottom: '-50px' }}>
                    <IconLogin />
                </h1>
                <h2
                    style={{
                        color: '#5b21b6',
                        marginBottom: '-10px',
                        fontSize: '50px',
                    }}
                >
                    MakerBox
                </h2>
                <h3 style={{ color: '#5b21b6', marginBottom: '20px' }}>
                    Iniciar Sesión
                </h3>
                <input
                    type="email"
                    placeholder="Correo electrónico"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    style={inputStyle}
                    disabled={isLoading}
                    data-testid="email-input"
                />
                <input
                    type="password"
                    placeholder="Contraseña"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    style={inputStyle}
                    disabled={isLoading}
                    data-testid="password-input"
                />
                {error && (
                    <p
                        style={{
                            color: '#dc2626',
                            fontSize: '14px',
                            marginBottom: '10px',
                            marginTop: 0,
                        }}
                        data-testid="login-error"
                    >
                        {error}
                    </p>
                )}
                <button
                    type="submit"
                    disabled={isLoading}
                    style={{
                        width: '100%',
                        padding: '12px',
                        backgroundColor: '#5b21b6',
                        color: 'white',
                        border: 'none',
                        borderRadius: '12px',
                        cursor: isLoading ? 'not-allowed' : 'pointer',
                        fontWeight: '600',
                        opacity: isLoading ? 0.7 : 1,
                    }}
                >
                    {isLoading ? 'Cargando...' : 'Acceder'}
                </button>
            </form>
        </div>
    );
}

const inputStyle = {
    width: '100%',
    padding: '12px',
    marginBottom: '15px',
    borderRadius: '8px',
    border: '1px solid #ddd',
    boxSizing: 'border-box',
};
