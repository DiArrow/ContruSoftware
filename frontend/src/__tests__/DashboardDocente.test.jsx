import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { DashboardDocente } from '../components/DashboardDocente';
import { AuthContext } from '../context/AuthContext';

// Mock de fetch global
globalThis.fetch = vi.fn();

const renderWithAuth = (component, rol) => {
    return render(
        <AuthContext.Provider value={{ currentUser: { rol } }}>
            {component}
        </AuthContext.Provider>
    );
};

describe('DashboardDocente Component', () => {
    beforeEach(() => {
        fetch.mockClear();
    });

    it('EST ven mensaje de "sin acceso"', () => {
        // Usa tu utilidad renderWithAuth pasándole el rol EST
        renderWithAuth(<DashboardDocente />, 'EST');
        expect(screen.getByText(/sin acceso/i)).toBeInTheDocument();
    });

    it('PRO ve la vista y "No hay cursos" si la lista está vacía', async () => {
        // Mockeamos respuestas vacías
        fetch.mockResolvedValueOnce({ ok: true, json: async () => [] }); // Semestres
        fetch.mockResolvedValueOnce({ ok: true, json: async () => [] }); // Cursos

        renderWithAuth(<DashboardDocente />, 'PRO');

        await waitFor(() => {
            expect(screen.getByText(/no hay cursos/i)).toBeInTheDocument();
        });
    });

    it('Selector de semestre muestra "Cargando..." mientras resuelve', async () => {
        // Dejamos la promesa pendiente intencionalmente
        fetch.mockImplementation(() => new Promise(() => {}));

        renderWithAuth(<DashboardDocente />, 'AYU');
        expect(screen.getByText(/cargando.../i)).toBeInTheDocument();
    });

    it('Submit exitoso agrega curso a la lista', async () => {
        // 1. Mock de carga inicial
        fetch.mockResolvedValueOnce({
            ok: true,
            json: async () => [{ id_semestre: '1', nombre: '2026-1' }],
        });
        fetch.mockResolvedValueOnce({ ok: true, json: async () => [] });

        renderWithAuth(<DashboardDocente />, 'PRO');

        // 2. Esperamos que el form esté listo
        await screen.findByRole('option', { name: '2026-1' });

        // 3. Deferred promise para el POST (para verificar estado "Creando...")
        let resolvePost;
        fetch.mockImplementationOnce(
            () =>
                new Promise((resolve) => {
                    resolvePost = resolve;
                })
        );

        // 4. Interacción
        await userEvent.type(
            screen.getByLabelText(/nombre del curso/i),
            'Matemáticas'
        );
        await userEvent.selectOptions(screen.getByLabelText(/semestre/i), '1');
        await userEvent.click(
            screen.getByRole('button', { name: /crear curso/i })
        );

        // 5. Verificamos que el botón cambia a "Creando..." (mientras la promesa está pendiente)
        expect(
            screen.getByRole('button', { name: /creando.../i })
        ).toBeInTheDocument();

        // 6. Resolvemos la promesa del POST
        resolvePost({
            status: 201,
            json: async () => ({
                id_curso: '10',
                nombre: 'Matemáticas',
                semestre_nombre: '2026-1',
            }),
        });

        // 7. Ahora el curso debe aparecer en la lista
        await waitFor(() => {
            expect(screen.getByText('Matemáticas')).toBeInTheDocument();
        });
    });
});
