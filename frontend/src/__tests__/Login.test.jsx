import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import Login from '../components/Login';
import { useAuth } from '../context/AuthContext';

vi.mock('../context/AuthContext', () => ({
    useAuth: vi.fn(),
}));

describe('Login component', () => {
    const loginMock = vi.fn();

    beforeEach(() => {
        vi.clearAllMocks();
        useAuth.mockReturnValue({ login: loginMock });
    });

    it('renders login form correctly', () => {
        render(<Login />);
        expect(screen.getByText(/Iniciar Sesión/i)).toBeInTheDocument();
        expect(screen.getByTestId('email-input')).toBeInTheDocument();
        expect(screen.getByTestId('password-input')).toBeInTheDocument();
        expect(screen.getByText(/Acceder/i)).toBeInTheDocument();
    });

    it('controlled inputs update state', () => {
        render(<Login />);
        const emailInput = screen.getByTestId('email-input');
        const passwordInput = screen.getByTestId('password-input');

        fireEvent.change(emailInput, { target: { value: 'test@utalca.cl' } });
        fireEvent.change(passwordInput, { target: { value: 'secret123' } });

        expect(emailInput.value).toBe('test@utalca.cl');
        expect(passwordInput.value).toBe('secret123');
    });

    it('shows validation error for empty fields', async () => {
        render(<Login />);
        fireEvent.click(screen.getByText(/Acceder/i));
        await waitFor(() =>
            expect(screen.getByTestId('login-error')).toHaveTextContent(
                'Por favor complete todos los campos'
            )
        );
    });

    it('calls login with email and password on submit', async () => {
        loginMock.mockResolvedValue({});
        render(<Login />);

        fireEvent.change(screen.getByTestId('email-input'), {
            target: { value: 'test@utalca.cl' },
        });
        fireEvent.change(screen.getByTestId('password-input'), {
            target: { value: 'secret123' },
        });
        fireEvent.click(screen.getByText(/Acceder/i));

        await waitFor(() =>
            expect(loginMock).toHaveBeenCalledWith(
                'test@utalca.cl',
                'secret123'
            )
        );
    });

    it('displays error message on failed login', async () => {
        loginMock.mockRejectedValue(new Error('Credenciales inválidas'));
        render(<Login />);

        fireEvent.change(screen.getByTestId('email-input'), {
            target: { value: 'test@utalca.cl' },
        });
        fireEvent.change(screen.getByTestId('password-input'), {
            target: { value: 'wrong' },
        });
        fireEvent.click(screen.getByText(/Acceder/i));

        await waitFor(() =>
            expect(screen.getByTestId('login-error')).toHaveTextContent(
                'Credenciales inválidas'
            )
        );
    });

    it('disables button and shows loading state during login', async () => {
        let resolveLogin;
        loginMock.mockImplementation(
            () =>
                new Promise((resolve) => {
                    resolveLogin = resolve;
                })
        );
        render(<Login />);

        fireEvent.change(screen.getByTestId('email-input'), {
            target: { value: 'test@utalca.cl' },
        });
        fireEvent.change(screen.getByTestId('password-input'), {
            target: { value: 'secret123' },
        });
        fireEvent.click(screen.getByText(/Acceder/i));

        await waitFor(() =>
            expect(screen.getByText(/Cargando.../i)).toBeInTheDocument()
        );
        expect(screen.getByText(/Cargando.../i)).toBeDisabled();

        resolveLogin({});
        await waitFor(() =>
            expect(screen.getByText(/Acceder/i)).toBeInTheDocument()
        );
    });

    it('displays connection error on network failure', async () => {
        loginMock.mockRejectedValue(new Error('Error de conexión'));
        render(<Login />);

        fireEvent.change(screen.getByTestId('email-input'), {
            target: { value: 'test@utalca.cl' },
        });
        fireEvent.change(screen.getByTestId('password-input'), {
            target: { value: 'secret123' },
        });
        fireEvent.click(screen.getByText(/Acceder/i));

        await waitFor(() =>
            expect(screen.getByTestId('login-error')).toHaveTextContent(
                'Error de conexión'
            )
        );
    });
});
