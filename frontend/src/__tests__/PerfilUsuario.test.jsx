import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { PerfilUsuario } from '../components/PerfilUsuario';
import { AuthContext } from '../context/AuthContext';

vi.mock('../api/client', () => ({
    apiGet: vi.fn(),
    apiPut: vi.fn(),
}));

import { apiPut } from '../api/client';

const renderWithAuth = (component, user) => {
    return render(
        <AuthContext.Provider value={{ currentUser: user }}>
            {component}
        </AuthContext.Provider>
    );
};

describe('PerfilUsuario Component', () => {
    beforeEach(() => {
        vi.clearAllMocks();
    });

    it('muestra el formulario prellenado con los datos del usuario', () => {
        renderWithAuth(
            <PerfilUsuario />,
            {
                id_usuario: '1',
                nombre: 'Juan',
                apellido: 'Pérez',
                email: 'juan@p.com',
                rol: 'EST',
            }
        );

        expect(screen.getByDisplayValue('Juan')).toBeInTheDocument();
        expect(screen.getByDisplayValue('Pérez')).toBeInTheDocument();
        expect(screen.getByDisplayValue('juan@p.com')).toBeInTheDocument();
    });

    it('envía la actualización y muestra mensaje de éxito', async () => {
        apiPut.mockResolvedValue({
            id_usuario: '1',
            nombre: 'Carlos',
            apellido: 'Pérez',
            email: 'juan@p.com',
            rol: 'EST',
        });

        renderWithAuth(
            <PerfilUsuario />,
            {
                id_usuario: '1',
                nombre: 'Juan',
                apellido: 'Pérez',
                email: 'juan@p.com',
                rol: 'EST',
            }
        );

        fireEvent.change(screen.getByDisplayValue('Juan'), {
            target: { value: 'Carlos' },
        });
        fireEvent.click(screen.getByText(/Guardar cambios/i));

        await waitFor(() => {
            expect(screen.getByText(/Perfil actualizado/i)).toBeInTheDocument();
        });

        expect(apiPut).toHaveBeenCalledWith('auth/me', {
            nombre: 'Carlos',
            apellido: 'Pérez',
            email: 'juan@p.com',
        });
    });

    it('muestra error de validación con un correo inválido', async () => {
        renderWithAuth(
            <PerfilUsuario />,
            {
                id_usuario: '1',
                nombre: 'Juan',
                apellido: 'Pérez',
                email: 'juan@p.com',
                rol: 'EST',
            }
        );

        fireEvent.change(screen.getByDisplayValue('juan@p.com'), {
            target: { value: 'no-es-un-email' },
        });
        fireEvent.click(screen.getByText(/Guardar cambios/i));

        await waitFor(() => {
            expect(
                screen.getByText(/correo no es válido/i)
            ).toBeInTheDocument();
        });

        expect(apiPut).not.toHaveBeenCalled();
    });
});
