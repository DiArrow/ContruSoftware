import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import UserRegistrationForm from '../components/UserRegistrationForm';
import { AuthContext } from '../context/AuthContext';

// Helper para crear respuestas de fetch limpias
const crearRespuestaMock = (ok, status, data) => ({
    ok,
    status,
    headers: new Headers({ 'content-type': 'application/json' }),
    json: async () => data,
});

// Helper para renderizar el componente inyectando el AuthContext
const renderWithAuth = (ui, currentUser) => {
    return render(
        <AuthContext.Provider value={{ currentUser }}>
            {ui}
        </AuthContext.Provider>
    );
};

describe('UserRegistrationForm Component', () => {
    beforeEach(() => {
        vi.stubGlobal('fetch', vi.fn());
        vi.clearAllMocks();
    });

    it('Usuario con rol EST no ve el formulario (renderiza mensaje "Sin acceso")', () => {
        renderWithAuth(<UserRegistrationForm />, { rol: 'EST' });

        expect(screen.getByText(/Sin acceso/i)).toBeInTheDocument();
        expect(screen.queryByLabelText(/nombre/i)).not.toBeInTheDocument();
    });

    it('Render inicial: formulario con todos los campos visibles cuando el rol es ADM', () => {
        renderWithAuth(<UserRegistrationForm />, { rol: 'ADM' });

        expect(screen.getByLabelText(/nombre/i)).toBeInTheDocument();
        expect(screen.getByLabelText(/apellido/i)).toBeInTheDocument();
        expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
        expect(screen.getByLabelText(/contraseña/i)).toBeInTheDocument();
        expect(screen.getByLabelText(/rol/i)).toBeInTheDocument();
    });

    it('Submit exitoso: mockea fetch (POST 201), verifica notificación de éxito y reset', async () => {
        fetch.mockResolvedValueOnce(crearRespuestaMock(true, 201, { id: 1 }));

        renderWithAuth(<UserRegistrationForm />, { rol: 'ADM' });

        await userEvent.type(screen.getByLabelText(/nombre/i), 'Juan');
        await userEvent.type(screen.getByLabelText(/apellido/i), 'Pérez');
        await userEvent.type(screen.getByLabelText(/email/i), 'juan@admin.com');
        await userEvent.type(screen.getByLabelText(/contraseña/i), 'secret123');
        await userEvent.selectOptions(screen.getByLabelText(/rol/i), 'PRO');

        const submitBtn = screen.getByRole('button', {
            name: /crear usuario/i,
        });
        await userEvent.click(submitBtn);

        await waitFor(() => {
            expect(fetch).toHaveBeenCalledTimes(1);
            expect(
                screen.getByText(/Usuario Juan creado con éxito/i)
            ).toBeInTheDocument();
        });

        // Verificamos que el formulario quedó en blanco tras el éxito
        expect(screen.getByLabelText(/nombre/i)).toHaveValue('');
    });

    it('Submit 409: verifica mensaje "El email ya se encuentra registrado"', async () => {
        fetch.mockResolvedValueOnce(crearRespuestaMock(false, 409, {}));

        renderWithAuth(<UserRegistrationForm />, { rol: 'ADM' });

        await userEvent.type(screen.getByLabelText(/nombre/i), 'Ana');
        await userEvent.type(screen.getByLabelText(/apellido/i), 'Gómez');
        await userEvent.type(screen.getByLabelText(/email/i), 'ana@admin.com');
        await userEvent.type(screen.getByLabelText(/contraseña/i), '1234');

        const submitBtn = screen.getByRole('button', {
            name: /crear usuario/i,
        });
        await userEvent.click(submitBtn);

        await waitFor(() => {
            expect(
                screen.getByText(/El email ya se encuentra registrado/i)
            ).toBeInTheDocument();
        });
    });

    it('Submit 422: mockea 422, verifica mensaje de error visible', async () => {
        fetch.mockResolvedValueOnce(
            crearRespuestaMock(false, 422, {
                detail: 'La contraseña es muy corta',
            })
        );

        renderWithAuth(<UserRegistrationForm />, { rol: 'ADM' });

        await userEvent.type(screen.getByLabelText(/nombre/i), 'Luis');
        await userEvent.type(screen.getByLabelText(/apellido/i), 'Soto');
        await userEvent.type(screen.getByLabelText(/email/i), 'luis@admin.com');
        await userEvent.type(screen.getByLabelText(/contraseña/i), '1');

        const submitBtn = screen.getByRole('button', {
            name: /crear usuario/i,
        });
        await userEvent.click(submitBtn);

        await waitFor(() => {
            expect(
                screen.getByText(/La contraseña es muy corta/i)
            ).toBeInTheDocument();
        });
    });

    it('Botón deshabilitado durante loading', async () => {
        let resolveFetch;
        fetch.mockImplementationOnce(
            () =>
                new Promise((resolve) => {
                    resolveFetch = resolve;
                })
        );

        renderWithAuth(<UserRegistrationForm />, { rol: 'ADM' });

        await userEvent.type(screen.getByLabelText(/nombre/i), 'Test');
        await userEvent.type(screen.getByLabelText(/apellido/i), 'Test');
        await userEvent.type(screen.getByLabelText(/email/i), 'test@admin.com');
        await userEvent.type(screen.getByLabelText(/contraseña/i), '1234');

        const submitBtn = screen.getByRole('button', {
            name: /crear usuario/i,
        });
        await userEvent.click(submitBtn);

        expect(submitBtn).toBeDisabled();

        resolveFetch(crearRespuestaMock(true, 201, {}));
    });

    it('Submit sin completar campos: verifica que no se llama al endpoint', async () => {
        renderWithAuth(<UserRegistrationForm />, { rol: 'ADM' });

        const submitBtn = screen.getByRole('button', {
            name: /crear usuario/i,
        });
        await userEvent.click(submitBtn);

        expect(fetch).not.toHaveBeenCalled();
        expect(
            screen.getByText(/Todos los campos son obligatorios/i)
        ).toBeInTheDocument();
    });
});
