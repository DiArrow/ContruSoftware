import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import App from '../App';

vi.mock('../api/client', () => ({
    apiGet: vi.fn(),
    apiPost: vi.fn(),
}));

import { apiGet, apiPost } from '../api/client';

describe('App with auth', () => {
    beforeEach(() => {
        localStorage.clear();
        vi.clearAllMocks();
    });

    it('shows login page when unauthenticated', () => {
        render(<App />);
        expect(screen.getByText(/Iniciar Sesión/i)).toBeInTheDocument();
    });

    it('shows dashboard after successful login', async () => {
        apiPost.mockResolvedValue({ access_token: 'tok123' });
        apiGet.mockResolvedValue({
            id_usuario: '1',
            nombre: 'María',
            apellido: 'Gómez',
            email: 'maria@utalca.cl',
            rol: 'user',
        });

        render(<App />);

        fireEvent.change(screen.getByTestId('email-input'), {
            target: { value: 'maria@utalca.cl' },
        });
        fireEvent.change(screen.getByTestId('password-input'), {
            target: { value: 'secret123' },
        });
        fireEvent.click(screen.getByText(/Acceder/i));

        await waitFor(() =>
            expect(
                screen.getByText(/Bienvenid@ a MakerBox/i)
            ).toBeInTheDocument()
        );
        expect(screen.getByText(/María/i)).toBeInTheDocument();
    });

    it('shows error on invalid credentials', async () => {
        apiPost.mockRejectedValue(new Error('Credenciales inválidas'));

        render(<App />);

        fireEvent.change(screen.getByTestId('email-input'), {
            target: { value: 'bad@utalca.cl' },
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

    it('sidebar navigation works after login', async () => {
        apiPost.mockResolvedValue({ access_token: 'tok123' });
        apiGet.mockResolvedValue({
            id_usuario: '1',
            nombre: 'Carlos',
            apellido: 'Pérez',
            email: 'carlos@utalca.cl',
            rol: 'admin',
        });

        render(<App />);

        fireEvent.change(screen.getByTestId('email-input'), {
            target: { value: 'carlos@utalca.cl' },
        });
        fireEvent.change(screen.getByTestId('password-input'), {
            target: { value: 'admin123' },
        });
        fireEvent.click(screen.getByText(/Acceder/i));

        await waitFor(() =>
            expect(
                screen.getByText(/Bienvenid@ a MakerBox/i)
            ).toBeInTheDocument()
        );

        const items = [
            'Dashboard',
            'Students',
            'Inventory',
            'Reports',
            'Courses',
            'Settings',
        ];
        items.forEach((label) => {
            const button = screen.getByTitle(label);
            fireEvent.click(button);
            expect(button).toHaveStyle('background-color: rgb(237, 233, 254)');
        });
    });
});

describe('Logout button', () => {
    beforeEach(() => {
        localStorage.clear();
        vi.clearAllMocks();
    });

    it('renders logout button in Topbar when authenticated', async () => {
        localStorage.setItem('token', 'tok123');
        apiGet.mockResolvedValue({
            id_usuario: '1',
            nombre: 'Ana',
            apellido: 'Lopez',
            email: 'ana@utalca.cl',
            rol: 'user',
        });

        render(<App />);

        await waitFor(() =>
            expect(
                screen.getByText(/Bienvenid@ a MakerBox/i)
            ).toBeInTheDocument()
        );

        expect(screen.getByTitle('Cerrar sesión')).toBeInTheDocument();
    });

    it('clicking logout clears token and shows login view', async () => {
        localStorage.setItem('token', 'tok123');
        apiGet.mockResolvedValue({
            id_usuario: '1',
            nombre: 'Ana',
            apellido: 'Lopez',
            email: 'ana@utalca.cl',
            rol: 'user',
        });

        render(<App />);

        await waitFor(() =>
            expect(
                screen.getByText(/Bienvenid@ a MakerBox/i)
            ).toBeInTheDocument()
        );

        fireEvent.click(screen.getByTitle('Cerrar sesión'));

        await waitFor(() =>
            expect(screen.getByText(/Iniciar Sesión/i)).toBeInTheDocument()
        );
        expect(localStorage.getItem('token')).toBeNull();
    });
});
