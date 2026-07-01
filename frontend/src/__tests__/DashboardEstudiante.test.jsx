import { render, screen, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { DashboardEstudiante } from '../components/DashboardEstudiante';
import { AuthContext } from '../context/AuthContext';

vi.mock('../api/client', () => ({
    apiGet: vi.fn(),
}));

import { apiGet } from '../api/client';

const renderWithAuth = (component) => {
    return render(
        <AuthContext.Provider value={{ currentUser: { rol: 'EST' } }}>
            {component}
        </AuthContext.Provider>
    );
};

describe('DashboardEstudiante Component', () => {
    beforeEach(() => {
        vi.clearAllMocks();
    });

    it('muestra spinner mientras carga', () => {
        apiGet.mockImplementation(() => new Promise(() => {}));
        renderWithAuth(<DashboardEstudiante />);
        expect(screen.getByText(/cargando/i)).toBeInTheDocument();
    });

    it('muestra tarjetas de cursos con nombre, semestre y créditos', async () => {
        apiGet.mockResolvedValue([
            {
                id_curso: '1',
                nombre: 'Matemáticas',
                semestre_nombre: '2026-1',
                creditos: 4,
            },
            {
                id_curso: '2',
                nombre: 'Física',
                semestre_nombre: '2026-1',
                creditos: 3,
            },
        ]);

        renderWithAuth(<DashboardEstudiante />);

        await waitFor(() => {
            expect(screen.getByText('Matemáticas')).toBeInTheDocument();
        });
        expect(screen.getByText('Física')).toBeInTheDocument();
        expect(screen.getAllByText('2026-1')).toHaveLength(2);
        expect(screen.getByText(/4 créditos/i)).toBeInTheDocument();
        expect(screen.getByText(/3 créditos/i)).toBeInTheDocument();
    });

    it('muestra mensaje cuando no hay cursos', async () => {
        apiGet.mockResolvedValue([]);

        renderWithAuth(<DashboardEstudiante />);

        await waitFor(() => {
            expect(
                screen.getByText(/No estás inscrito en ningún curso/i)
            ).toBeInTheDocument();
        });
    });
});
