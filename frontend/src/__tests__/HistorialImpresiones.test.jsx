import { render, screen, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { HistorialImpresiones } from '../components/HistorialImpresiones';
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

describe('HistorialImpresiones Component', () => {
    beforeEach(() => {
        vi.clearAllMocks();
    });

    it('muestra spinner mientras carga', () => {
        apiGet.mockImplementation(() => new Promise(() => {}));
        renderWithAuth(<HistorialImpresiones />);
        expect(screen.getByText(/cargando/i)).toBeInTheDocument();
    });

    it('renderiza tabla con archivo, estado y fecha', async () => {
        apiGet.mockResolvedValue([
            {
                id_impresion: '1',
                nombre_archivo: 'pieza.stl',
                estado: 'Completada',
                fecha_solicitud: '2025-06-15T12:00:00',
            },
            {
                id_impresion: '2',
                nombre_archivo: 'modelo.obj',
                estado: 'Pendiente',
                fecha_solicitud: '2025-06-14T10:00:00',
            },
        ]);

        renderWithAuth(<HistorialImpresiones />);

        await waitFor(() => {
            expect(screen.getByText('pieza.stl')).toBeInTheDocument();
        });
        expect(screen.getByText('modelo.obj')).toBeInTheDocument();
        expect(screen.getByText('Completada')).toBeInTheDocument();
        expect(screen.getByText('Pendiente')).toBeInTheDocument();
        expect(screen.getByText('15/06/2025')).toBeInTheDocument();
        expect(screen.getByText('14/06/2025')).toBeInTheDocument();
    });

    it('muestra mensaje cuando no hay solicitudes', async () => {
        apiGet.mockResolvedValue([]);

        renderWithAuth(<HistorialImpresiones />);

        await waitFor(() => {
            expect(
                screen.getByText(/Sin solicitudes de impresión/i)
            ).toBeInTheDocument();
        });
    });

    it('asigna colores correctos a los badges de estado', async () => {
        apiGet.mockResolvedValue([
            {
                id_impresion: '1',
                nombre_archivo: 'completada.stl',
                estado: 'Completada',
                fecha_solicitud: '2025-06-15T12:00:00',
            },
            {
                id_impresion: '2',
                nombre_archivo: 'pendiente.obj',
                estado: 'Pendiente',
                fecha_solicitud: '2025-06-14T10:00:00',
            },
            {
                id_impresion: '3',
                nombre_archivo: 'rechazada.gcode',
                estado: 'Rechazada',
                fecha_solicitud: '2025-06-13T09:00:00',
            },
        ]);

        renderWithAuth(<HistorialImpresiones />);

        await waitFor(() => {
            expect(screen.getByText('Completada')).toBeInTheDocument();
        });

        expect(screen.getByText('Completada')).toHaveStyle(
            'background-color: rgb(220, 252, 231)'
        );
        expect(screen.getByText('Pendiente')).toHaveStyle(
            'background-color: rgb(254, 249, 195)'
        );
        expect(screen.getByText('Rechazada')).toHaveStyle(
            'background-color: rgb(254, 226, 226)'
        );
    });
});
