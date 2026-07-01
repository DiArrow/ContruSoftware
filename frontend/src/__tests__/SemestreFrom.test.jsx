import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import SemestreForm from '../components/SemestreForm';
import { useAuth } from '../context/AuthContext';
import * as client from '../api/client';

vi.mock('../context/AuthContext', () => ({
    useAuth: vi.fn(),
}));

vi.mock('../api/client', () => ({
    apiPost: vi.fn(),
}));

describe('SemestreForm Component', () => {
    beforeEach(() => {
        vi.clearAllMocks();
    });
    it('no debe permitir acceso a usuarios sin rol ADM o AYU', () => {
        useAuth.mockReturnValue({ currentUser: { rol: 'EST' } }); // Usuario con rol no permitido

        render(<SemestreForm onCreated={() => {}} />);
        expect(
            screen.getByText('No tienes permisos para crear semestres.')
        ).toBeInTheDocument();
        expect(screen.queryByTestId('semestre-form')).not.toBeInTheDocument();
    });

    it('debe permitir enviar el formulario con datos válidos para ADM', async () => {
        useAuth.mockReturnValue({ currentUser: { rol: 'ADM' } });
        const mockOnCreated = vi.fn();
        client.apiPost.mockResolvedValue({ id_semestre: 3, nombre: '2026-2' });

        render(<SemestreForm onCreated={mockOnCreated} />);

        fireEvent.change(screen.getByPlaceholderText('Nombre (ej: 2026-1)'), {
            target: { value: '2026-2' },
        });
        const dateInputs = document.querySelectorAll('input[type="date"]');
        fireEvent.change(dateInputs[0], { target: { value: '2026-08-01' } });
        fireEvent.change(dateInputs[1], { target: { value: '2026-12-15' } });

        fireEvent.submit(screen.getByTestId('semestre-form'));

        await waitFor(() => {
            expect(client.apiPost).toHaveBeenCalledWith('semestres', {
                nombre: '2026-2',
                fecha_inicio: '2026-08-01',
                fecha_fin: '2026-12-15',
            });
            expect(mockOnCreated).toHaveBeenCalled();
        });
    });

    it('debe mostrar un mensaje de error si la creación falla en la API', async () => {
        useAuth.mockReturnValue({ currentUser: { rol: 'AYU' } });
        client.apiPost.mockRejectedValue(
            new Error('fecha_fin debe ser mayor a fecha_inicio')
        );

        render(<SemestreForm onCreated={() => {}} />);

        fireEvent.change(screen.getByPlaceholderText('Nombre (ej: 2026-1)'), {
            target: { value: 'Erroneo' },
        });
        fireEvent.submit(screen.getByTestId('semestre-form'));

        await waitFor(() => {
            expect(screen.getByTestId('form-error')).toHaveTextContent(
                'fecha_fin debe ser mayor a fecha_inicio'
            );
        });
    });
});
