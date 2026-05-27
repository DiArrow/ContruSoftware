import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { AuthProvider, useAuth } from '../context/AuthContext';

vi.mock('../api/client', () => ({
    apiGet: vi.fn(),
    apiPost: vi.fn(),
}));

import { apiGet, apiPost } from '../api/client';

function TestConsumer() {
    const { currentUser, isAuthenticated, isLoading, login, logout } =
        useAuth();
    return (
        <div>
            <div data-testid="loading">{isLoading ? 'loading' : 'ready'}</div>
            <div data-testid="auth">{isAuthenticated ? 'yes' : 'no'}</div>
            <div data-testid="user">
                {currentUser ? currentUser.nombre : 'none'}
            </div>
            <button
                onClick={async () => {
                    try {
                        await login('a@b.cl', 'pw');
                    } catch {
                        // errors are expected in failure tests
                    }
                }}
                data-testid="login-btn"
            >
                Login
            </button>
            <button onClick={logout} data-testid="logout-btn">
                Logout
            </button>
        </div>
    );
}

describe('AuthContext', () => {
    beforeEach(() => {
        localStorage.clear();
        vi.clearAllMocks();
    });

    it('login success stores token and sets currentUser', async () => {
        apiPost.mockResolvedValue({ access_token: 'tok123' });
        apiGet.mockResolvedValue({
            id_usuario: '1',
            nombre: 'Ana',
            apellido: 'Lopez',
            email: 'a@b.cl',
            rol: 'admin',
        });

        render(
            <AuthProvider>
                <TestConsumer />
            </AuthProvider>
        );

        await waitFor(() =>
            expect(screen.getByTestId('loading').textContent).toBe('ready')
        );

        screen.getByTestId('login-btn').click();
        await waitFor(() =>
            expect(screen.getByTestId('auth').textContent).toBe('yes')
        );
        expect(screen.getByTestId('user').textContent).toBe('Ana');
        expect(localStorage.getItem('token')).toBe('tok123');
    });

    it('login failure does not store token', async () => {
        apiPost.mockRejectedValue(new Error('Credenciales inválidas'));

        render(
            <AuthProvider>
                <TestConsumer />
            </AuthProvider>
        );

        await waitFor(() =>
            expect(screen.getByTestId('loading').textContent).toBe('ready')
        );

        screen.getByTestId('login-btn').click();
        await waitFor(() =>
            expect(screen.getByTestId('auth').textContent).toBe('no')
        );
        expect(localStorage.getItem('token')).toBeNull();
    });

    it('logout clears localStorage and currentUser', async () => {
        localStorage.setItem('token', 'tok123');
        apiGet.mockResolvedValue({
            id_usuario: '1',
            nombre: 'Ana',
            apellido: 'Lopez',
            email: 'a@b.cl',
            rol: 'admin',
        });

        render(
            <AuthProvider>
                <TestConsumer />
            </AuthProvider>
        );

        await waitFor(() =>
            expect(screen.getByTestId('auth').textContent).toBe('yes')
        );

        screen.getByTestId('logout-btn').click();
        await waitFor(() =>
            expect(screen.getByTestId('auth').textContent).toBe('no')
        );
        expect(localStorage.getItem('token')).toBeNull();
    });

    it('page reload with valid token restores user', async () => {
        localStorage.setItem('token', 'tok123');
        apiGet.mockResolvedValue({
            id_usuario: '1',
            nombre: 'Carlos',
            apellido: 'Perez',
            email: 'c@d.cl',
            rol: 'user',
        });

        render(
            <AuthProvider>
                <TestConsumer />
            </AuthProvider>
        );

        await waitFor(() =>
            expect(screen.getByTestId('auth').textContent).toBe('yes')
        );
        expect(screen.getByTestId('user').textContent).toBe('Carlos');
    });

    it('expired token on reload clears storage and user', async () => {
        localStorage.setItem('token', 'oldtok');
        apiGet.mockRejectedValue(new Error('Token inválido o expirado'));

        render(
            <AuthProvider>
                <TestConsumer />
            </AuthProvider>
        );

        await waitFor(() =>
            expect(screen.getByTestId('auth').textContent).toBe('no')
        );
        expect(localStorage.getItem('token')).toBeNull();
    });
});
