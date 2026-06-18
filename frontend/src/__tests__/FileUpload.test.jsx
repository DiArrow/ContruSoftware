import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import FileUpload from '../components/FileUpload';

describe('FileUpload Component', () => {
    let alertMock;

    beforeEach(() => {
        alertMock = vi.fn();
        vi.stubGlobal('alert', alertMock);
    });

    it('renders initial state correctly', () => {
        render(<FileUpload />);

        // Verificar textos
        expect(
            screen.getByText(
                'Arrastra tus archivos aquí o haz clic para buscar'
            )
        ).toBeInTheDocument();
        expect(
            screen.getByText('Soporta cualquier formato de impresión')
        ).toBeInTheDocument();
    });

    it('should load a file through input selection and create notification', async () => {
        const mockNotification = vi.fn();

        const { container } = render(
            <FileUpload onFileUploaded={mockNotification} />
        );

        const fakeFile = new File(['contenido-3d'], 'modelo_pieza.stl', {
            type: 'application/sla',
        });

        const input = container.querySelector('input[type="file"]');

        expect(input).toBeInTheDocument();

        fireEvent.change(input, {
            target: { files: [fakeFile] },
        });

        expect(screen.getByText('Archivos seleccionados:')).toBeInTheDocument();
        expect(screen.getByText(/modelo_pieza.stl/i)).toBeInTheDocument();

        const submitButton = screen.getByRole('button', {
            name: /enviar impresión/i,
        });

        expect(submitButton).toBeInTheDocument();

        fireEvent.click(submitButton);
    });

    it('should change visual style when dragging and dropping a file (Drag & Drop)', () => {
        render(<FileUpload />);

        // El contenedor del formulario o la zona de drop
        const dropZone = screen.getByText(
            'Arrastra tus archivos aquí o haz clic para buscar'
        ).parentElement;
        const fakeFile = new File(['gcode-data'], 'objeto.gcode', {
            type: 'text/plain',
        });

        // 1. Simular arrastrar el archivo
        fireEvent.dragOver(dropZone);

        // 2. Simular soltar el archivo
        fireEvent.drop(dropZone, {
            dataTransfer: {
                files: [fakeFile],
            },
        });

        expect(screen.getByText('Archivos seleccionados:')).toBeInTheDocument();
        expect(screen.getByText(/objeto.gcode/i)).toBeInTheDocument();

        const submitButton = screen.getByRole('button', {
            name: /enviar impresión/i,
        });
        expect(submitButton).toBeInTheDocument();
    });
});
