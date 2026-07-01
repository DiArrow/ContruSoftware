import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, test, expect, vi, beforeEach } from 'vitest';
import { ImportadorCSV } from '../components/ImportadorCSV';

describe('Pruebas unitarias y de integración para ImportadorCSV', () => {
    const mockOnVolver = vi.fn();
    const cursoId = '42';

    beforeEach(() => {
        vi.clearAllMocks();
        // Simulación del token de sesión para las cabeceras HTTP
        Storage.prototype.getItem = vi.fn(() => 'token-valido-test');

        vi.spyOn(window.FileReader.prototype, 'readAsText').mockImplementation(
            function (file) {
                let contenidoSimulado =
                    'Nombre,Apellido,Correo\nAna,García,ana.garcia@utalca.cl\nDiego,Soto,dsoto@utalca.cl\nValentina,Rojas,vrojas@utalca.cl';

                // Si simulamos escenarios vacíos o erróneos reducidos
                if (file.name === 'vacio.csv')
                    contenidoSimulado = 'Nombre,Apellido,Correo';

                // Ejecutamos de forma síncrona el callback onload para evitar problemas de tiempos en el test
                if (this.onload) {
                    this.onload({ target: { result: contenidoSimulado } });
                }
            }
        );
    });

    test('Render inicial: muestra zona de drop con texto esperado y oculta controles avanzados', () => {
        render(<ImportadorCSV cursoId={cursoId} onVolver={mockOnVolver} />);

        expect(
            screen.getByText(/Arrastra tu archivo CSV aquí/i)
        ).toBeInTheDocument();
        // Criterio: Sin archivo el botón de importar no debe ser visible
        expect(
            screen.queryByRole('button', { name: /Importar/i })
        ).not.toBeInTheDocument();
    });

    test('Archivo CSV válido: procesa mediante FileReader y muestra preview con tabla estructurada', async () => {
        render(<ImportadorCSV cursoId={cursoId} onVolver={mockOnVolver} />);

        const file = new File([''], 'Estudiante_Pruebas.csv', {
            type: 'text/csv',
        });
        const input = screen.getByTestId('csv-input');

        fireEvent.change(input, { target: { files: [file] } });

        // Verifica que renderice la tabla y el preview de las primeras filas
        await waitFor(() => {
            expect(screen.getByText('Ana')).toBeInTheDocument();
            expect(screen.getByText('Diego')).toBeInTheDocument();
            expect(screen.getByText('Valentina')).toBeInTheDocument();
        });

        // El botón dinámico debe habilitarse con la cantidad exacta extraída
        expect(
            screen.getByRole('button', { name: /Importar 3 estudiantes/i })
        ).toBeInTheDocument();
    });

    test('Submit exitoso: emite la petición Multipart y muestra reporte de resultados con contraseñas', async () => {
        // Mock del fetch exitoso del servidor — incluye passwords
        window.fetch = vi.fn().mockResolvedValue({
            ok: true,
            status: 200,
            json: async () => ({
                imported: 3,
                duplicates: 0,
                errors: [],
                passwords: [
                    { correo: 'ana.garcia@utalca.cl', password: 'abc123xyz' },
                    { correo: 'dsoto@utalca.cl', password: 'def456uvw' },
                    { correo: 'vrojas@utalca.cl', password: 'ghi789rst' },
                ],
            }),
        });

        render(<ImportadorCSV cursoId={cursoId} onVolver={mockOnVolver} />);

        const file = new File([''], 'Estudiante_Pruebas.csv', {
            type: 'text/csv',
        });
        const input = screen.getByTestId('csv-input');
        fireEvent.change(input, { target: { files: [file] } });

        const botonSubmit = await screen.findByRole('button', {
            name: /Importar 3 estudiantes/i,
        });
        fireEvent.click(botonSubmit);

        // Verificamos que se llame al endpoint correcto mediante FormData
        expect(window.fetch).toHaveBeenCalledWith(
            `/api/cursos/${cursoId}/estudiantes/csv`,
            expect.any(Object)
        );

        // Verifica el reporte de resultados final en verde/colores
        await waitFor(() => {
            expect(screen.getByText('Importados')).toBeInTheDocument();
            expect(screen.getByText('3')).toBeInTheDocument();
            expect(screen.getByText('Duplicados')).toBeInTheDocument();
            expect(screen.getByText('Errores')).toBeInTheDocument();
        });

        // Verifica que la tabla de contraseñas se renderiza
        expect(screen.getByText('Contraseñas generadas')).toBeInTheDocument();
        expect(screen.getByText('abc123xyz')).toBeInTheDocument();
        expect(screen.getByText('def456uvw')).toBeInTheDocument();
        expect(screen.getByText('ghi789rst')).toBeInTheDocument();
    });

    test('Submit con errores parciales: renderiza resumen y lista detallada de cada falla', async () => {
        window.fetch = vi.fn().mockResolvedValue({
            ok: true,
            status: 200,
            json: async () => ({
                imported: 1,
                duplicates: 1,
                errors: [
                    'Fila 3: El correo es obligatorio',
                    'Fila 4: Formato de correo inválido',
                ],
            }),
        });

        render(<ImportadorCSV cursoId={cursoId} onVolver={mockOnVolver} />);

        const file = new File([''], 'Estudiantes_Mixto.csv', {
            type: 'text/csv',
        });
        const input = screen.getByTestId('csv-input');
        fireEvent.change(input, { target: { files: [file] } });

        const botonSubmit = await screen.findByRole('button', {
            name: /Importar/i,
        });
        fireEvent.click(botonSubmit);

        // Validamos la inyección del bloque detallado de errores (tarjeta roja secundaria)
        await waitFor(() => {
            expect(screen.getByText('Detalle de errores:')).toBeInTheDocument();
            expect(
                screen.getByText('Fila 3: El correo es obligatorio')
            ).toBeInTheDocument();
            expect(
                screen.getByText('Fila 4: Formato de correo inválido')
            ).toBeInTheDocument();
        });
    });

    test('Error 422 del backend: captura la falla de validación estructural e informa al usuario', async () => {
        window.fetch = vi.fn().mockResolvedValue({
            ok: false,
            status: 422,
            json: async () => ({
                detail: 'Estructura de columnas inválida. Se requiere: Nombre, Apellido, Correo.',
            }),
        });

        render(<ImportadorCSV cursoId={cursoId} onVolver={mockOnVolver} />);

        const file = new File([''], 'Invalido.csv', { type: 'text/csv' });
        const input = screen.getByTestId('csv-input');
        fireEvent.change(input, { target: { files: [file] } });

        const botonSubmit = await screen.findByRole('button', {
            name: /Importar/i,
        });
        fireEvent.click(botonSubmit);

        await waitFor(() => {
            expect(
                screen.getByText(
                    'Estructura de columnas inválida. Se requiere: Nombre, Apellido, Correo.'
                )
            ).toBeInTheDocument();
        });
    });

    test('Archivo malicioso (.exe): bloquea la lectura, levanta error y deniega el envío', () => {
        render(<ImportadorCSV cursoId={cursoId} onVolver={mockOnVolver} />);

        const file = new File(['binary'], 'script.exe', {
            type: 'application/x-msdownload',
        });
        const input = screen.getByTestId('csv-input');

        fireEvent.change(input, { target: { files: [file] } });

        expect(
            screen.getByText('Solo se aceptan archivos .csv')
        ).toBeInTheDocument();
        expect(screen.queryByRole('table')).not.toBeInTheDocument();
    });

    test('Archivo mayor a 5MB: interrumpe el flujo y expone alerta de sobrepeso', () => {
        render(<ImportadorCSV cursoId={cursoId} onVolver={mockOnVolver} />);

        const filePesado = new File([''], 'Datos_Gigantes.csv', {
            type: 'text/csv',
        });
        // Redefinimos el peso de forma artificial para simular el exceso de tamaño
        Object.defineProperty(filePesado, 'size', { value: 6 * 1024 * 1024 });

        const input = screen.getByTestId('csv-input');
        fireEvent.change(input, { target: { files: [filePesado] } });

        expect(
            screen.getByText('El archivo excede el límite de 5MB')
        ).toBeInTheDocument();
        expect(screen.queryByRole('table')).not.toBeInTheDocument();
    });

    test('Estado de carga (loading): deshabilita el botón de acción y renderiza texto dinámico', async () => {
        // Hacemos que la promesa del fetch no se resuelva de inmediato para mantener el componente colgado en el envío
        window.fetch = vi.fn().mockReturnValue(new Promise(() => {}));

        render(<ImportadorCSV cursoId={cursoId} onVolver={mockOnVolver} />);

        const file = new File([''], 'Estudiante_Pruebas.csv', {
            type: 'text/csv',
        });
        const input = screen.getByTestId('csv-input');
        fireEvent.change(input, { target: { files: [file] } });

        const botonSubmit = await screen.findByRole('button', {
            name: /Importar/i,
        });
        fireEvent.click(botonSubmit);

        // El botón debe congelarse para mitigar el doble submit accidental
        expect(botonSubmit).toBeDisabled();
        expect(screen.getAllByText('Importando...').length).toBe(2);
    });

    test('Descarga de CSV con contraseñas: genera blob y dispara descarga con contenido correcto', async () => {
        const mockUrl = 'blob:test-url';
        const createObjectURLSpy = vi.fn().mockReturnValue(mockUrl);
        const revokeObjectURLSpy = vi.fn();
        URL.createObjectURL = createObjectURLSpy;
        URL.revokeObjectURL = revokeObjectURLSpy;

        // Espiamos createElement para capturar el click del anchor
        const anchorClickSpy = vi.fn();
        const originalCreateElement = document.createElement.bind(document);
        vi.spyOn(document, 'createElement').mockImplementation((tag) => {
            const element = originalCreateElement(tag);
            if (tag === 'a') {
                element.click = anchorClickSpy;
                // jsdom no soporta href assignment nativo, lo emulamos
                let _href = '';
                let _download = '';
                Object.defineProperty(element, 'href', {
                    get: () => _href,
                    set: (v) => {
                        _href = v;
                    },
                });
                Object.defineProperty(element, 'download', {
                    get: () => _download,
                    set: (v) => {
                        _download = v;
                    },
                });
            }
            return element;
        });

        window.fetch = vi.fn().mockResolvedValue({
            ok: true,
            status: 200,
            json: async () => ({
                imported: 2,
                duplicates: 0,
                errors: [],
                passwords: [
                    { correo: 'a@test.cl', password: 'p4ssA' },
                    { correo: 'b@test.cl', password: 'p4ssB' },
                ],
            }),
        });

        render(<ImportadorCSV cursoId={cursoId} onVolver={mockOnVolver} />);

        const file = new File([''], 'Estudiante_Pruebas.csv', {
            type: 'text/csv',
        });
        const input = screen.getByTestId('csv-input');
        fireEvent.change(input, { target: { files: [file] } });

        const botonSubmit = await screen.findByRole('button', {
            name: /Importar/i,
        });
        fireEvent.click(botonSubmit);

        const botonDescarga = await screen.findByRole('button', {
            name: /Descargar CSV con contraseñas/i,
        });

        fireEvent.click(botonDescarga);

        // Verificamos que se creó un Blob con el CSV correcto
        expect(createObjectURLSpy).toHaveBeenCalledTimes(1);
        const blobArg = createObjectURLSpy.mock.calls[0][0];
        expect(blobArg.type).toBe('text/csv');
        const csvText = await blobArg.text();
        expect(csvText).toBe(
            'correo,contraseña\na@test.cl,p4ssA\nb@test.cl,p4ssB'
        );

        // Verificamos que se disparó el click para descargar
        expect(anchorClickSpy).toHaveBeenCalledTimes(1);

        // Limpiamos el spy para no afectar otros tests
        vi.restoreAllMocks();
    });
});
