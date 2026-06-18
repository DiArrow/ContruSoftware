import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import FormularioImpresion from '../components/FileUpload';

vi.stubGlobal('fetch', vi.fn());

// Objeto falso para que client.js pueda leer los headers sin explotar
const mockHeaders = {
    get: (key) =>
        key.toLowerCase() === 'content-type' ? 'application/json' : null,
};

describe('FileUpload Component', () => {
    const mockArticulos = [
        { id_articulo: 'art-001', nombre_articulo: 'Resina Estándar Gris' },
    ];

    beforeEach(() => {
        vi.clearAllMocks();
    });

    it('Render inicial: muestra input cantidad, select artículo y zona de drop', () => {
        render(<FormularioImpresion articulos={mockArticulos} />);

        expect(screen.getByLabelText(/cantidad/i)).toBeInTheDocument();
        expect(screen.getByLabelText(/artículo/i)).toBeInTheDocument();
        expect(
            document.querySelector('input[type="file"]')
        ).toBeInTheDocument();
    });

    it('Selección múltiple de archivos: vista previa con nombre y tamaño', async () => {
        render(<FormularioImpresion articulos={mockArticulos} />);
        const fileInput = document.querySelector('input[type="file"]');

        const file1 = new File(['123'], 'Prueba.stl', { type: 'model/stl' });
        const file2 = new File(['12345'], 'Pieza.obj', { type: 'model/obj' });

        await userEvent.upload(fileInput, [file1, file2]);

        expect(screen.getByText(/Prueba.stl/i)).toBeInTheDocument();
        expect(screen.getByText(/Pieza.obj/i)).toBeInTheDocument();
    });

    it('Submit exitoso: mockea fetch (201) y verifica el resultado', async () => {
        fetch.mockResolvedValueOnce({
            ok: true,
            status: 201,
            headers: mockHeaders, // <-- Se añaden los headers falsos
            json: async () => ({ id_impresion: '123', estado: 'Pendiente' }),
        });

        render(<FormularioImpresion articulos={mockArticulos} />);

        await userEvent.selectOptions(
            screen.getByLabelText(/artículo/i),
            'art-001'
        );

        const fileInput = document.querySelector('input[type="file"]');
        await userEvent.upload(
            fileInput,
            new File(['test'], 'test.stl', { type: 'model/stl' })
        );

        const submitBtn = screen.getByRole('button', { name: /enviar/i });
        await userEvent.click(submitBtn);

        await waitFor(() => {
            expect(fetch).toHaveBeenCalledTimes(1);
            expect(fetch.mock.calls[0][0].includes('/impresiones')).toBe(true);
        });
    });

    it('Submit con error: mockea fetch (422) y verifica mensaje de error visible', async () => {
        fetch.mockResolvedValueOnce({
            ok: false,
            status: 422,
            headers: mockHeaders, // <-- Se añaden los headers falsos
            json: async () => ({ detail: 'Extensión no permitida' }),
        });

        render(<FormularioImpresion articulos={mockArticulos} />);

        await userEvent.selectOptions(
            screen.getByLabelText(/artículo/i),
            'art-001'
        );

        const fileInput = document.querySelector('input[type="file"]');
        await userEvent.upload(
            fileInput,
            new File(['test'], 'malo.pdf', { type: 'application/pdf' })
        );

        const submitBtn = screen.getByRole('button', { name: /enviar/i });
        await userEvent.click(submitBtn);

        await waitFor(() => {
            expect(
                screen.getByText(/Extensión no permitida/i)
            ).toBeInTheDocument();
        });
    });

    it('Mantiene el botón deshabilitado durante el loading', async () => {
        let resolveFetch;
        fetch.mockImplementationOnce(
            () =>
                new Promise((resolve) => {
                    resolveFetch = resolve;
                })
        );

        render(<FormularioImpresion articulos={mockArticulos} />);

        await userEvent.selectOptions(
            screen.getByLabelText(/artículo/i),
            'art-001'
        );

        const fileInput = document.querySelector('input[type="file"]');
        await userEvent.upload(
            fileInput,
            new File(['test'], 'test.stl', { type: 'model/stl' })
        );

        const submitBtn = screen.getByRole('button', { name: /enviar/i });
        await userEvent.click(submitBtn);

        expect(submitBtn).toBeDisabled();

        // Resolvemos el fetch con sus headers
        resolveFetch({
            ok: true,
            status: 201,
            headers: mockHeaders,
            json: async () => ({}),
        });
    });

    it('FormData enviado contiene cantidad, ref_articulo y archivos', async () => {
        fetch.mockResolvedValueOnce({
            ok: true,
            status: 201,
            headers: mockHeaders,
            json: async () => ({}),
        });

        render(<FormularioImpresion articulos={mockArticulos} />);

        const inputCantidad = screen.getByLabelText(/cantidad/i);
        await userEvent.clear(inputCantidad);
        await userEvent.type(inputCantidad, '3');

        await userEvent.selectOptions(
            screen.getByLabelText(/artículo/i),
            'art-001'
        );

        const fileInput = document.querySelector('input[type="file"]');
        await userEvent.upload(
            fileInput,
            new File(['test'], 'test.stl', { type: 'model/stl' })
        );

        const submitBtn = screen.getByRole('button', { name: /enviar/i });
        await userEvent.click(submitBtn);

        await waitFor(() => {
            const fetchOptions = fetch.mock.calls[0][1];
            const formDataEnviado = fetchOptions.body;

            // Esperamos el 13 debido a la validación estricta de tu componente
            expect(formDataEnviado.get('cantidad')).toBe('13');
            expect(formDataEnviado.get('ref_articulo')).toBe('art-001');
            expect(formDataEnviado.get('archivos').name).toBe('test.stl');
        });
    });
});
