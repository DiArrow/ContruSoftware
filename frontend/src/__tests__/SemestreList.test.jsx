import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import SemestreList from '../components/SemestreList';
import * as client from '../api/client';

vi.mock('../api/client', () => ({
    apiGet: vi.fn(),
}));

describe('SemestreList Component', () => {
    const mockSemestres = [
        {
            id_semestre: 1,
            nombre: '2026-1',
            fecha_inicio: '2026-03-01',
            fecha_fin: '2026-07-15',
            estado: true,
        },
        {
            id_semestre: 2,
            nombre: '2025-2',
            fecha_inicio: '2025-08-01',
            fecha_fin: '2026-12-20',
            estado: false,
        },
    ];

    beforeEach(() => {
        vi.clearAllMocks();
    });
    it('debe renderizar cargando inicialmente y luego la tabla de semestres', async () => {
        client.apiGet.mockResolvedValue(mockSemestres);

        render(<SemestreList asSelect={false} />);

        expect(screen.getByText(/Cargando semestres.../i)).toBeInTheDocument();

        await waitFor(() => {
            expect(screen.getByText('2026-1')).toBeInTheDocument();
            expect(screen.getByText('2025-2')).toBeInTheDocument();
        });

        const rows = screen.getAllByTestId('semestre-row');
        expect(rows).toHaveLength(2);
        expect(screen.getByText('Activo')).toBeInTheDocument();
        expect(screen.getByText('Inactivo')).toBeInTheDocument();
    });

    it('debe renderizar en modo select cuando asSelect es true', async () => {
        client.apiGet.mockResolvedValue(mockSemestres);

        render(<SemestreList asSelect={true} value="" onChange={() => {}} />);

        await waitFor(() => {
            const select = screen.getByTestId('semestre-select');
            expect(select).toBeInTheDocument();
        });

        expect(screen.getByText('Selecciona un semestre')).toBeInTheDocument();
        expect(
            screen.getByText('2026-1 (2026-03-01 → 2026-07-15)')
        ).toBeInTheDocument();
    });

    it('debe manejar errores de la API correctamente', async () => {
        client.apiGet.mockRejectedValue(new Error('Conexión rechazada'));

        render(<SemestreList />);

        await waitFor(() => {
            expect(
                screen.getByText('Error: Conexión rechazada')
            ).toBeInTheDocument();
        });
    });
});
