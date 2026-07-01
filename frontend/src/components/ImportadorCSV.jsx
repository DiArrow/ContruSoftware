import { useState } from 'react';

export const ImportadorCSV = ({ cursoId, onVolver }) => {
    const [isDragging, setIsDragging] = useState(false);
    const [archivo, setArchivo] = useState(null);
    const [errorMsg, setErrorMsg] = useState('');

    // Nuevos estados para la previsualización
    const [previewData, setPreviewData] = useState([]);
    const [totalFilas, setTotalFilas] = useState(0);

    const [isSubmitting, setIsSubmitting] = useState(false);
    const [resultado, setResultado] = useState(null);

    const MAX_SIZE_MB = 5;
    const MAX_SIZE_BYTES = MAX_SIZE_MB * 1024 * 1024;

    const procesarCSV = (file) => {
        const reader = new FileReader();

        reader.onload = (evento) => {
            const texto = evento.target.result;
            // Separamos por saltos de línea y filtramos líneas vacías
            const lineas = texto
                .split(/\r?\n/)
                .map((linea) => linea.trim())
                .filter((linea) => linea !== '');

            if (lineas.length <= 1) {
                setErrorMsg(
                    'El archivo CSV está vacío o solo contiene la fila de encabezados.'
                );
                setPreviewData([]);
                setTotalFilas(0);
                return;
            }

            // Calculamos el total de estudiantes (total de líneas - 1 fila de encabezado)
            setTotalFilas(lineas.length - 1);

            // Tomamos las filas del índice 1 al 5 (máximo 5 elementos para el preview)
            const lineasPreview = lineas.slice(1, 6);

            // Asumimos que las columnas vienen en orden: nombre, apellido, correo
            const datosParseados = lineasPreview.map((linea) => {
                const columnas = linea.split(',');
                return {
                    nombre: columnas[0] ? columnas[0].trim() : '-',
                    apellido: columnas[1] ? columnas[1].trim() : '-',
                    correo: columnas[2] ? columnas[2].trim() : '-',
                };
            });

            setPreviewData(datosParseados);
        };

        reader.onerror = () => {
            setErrorMsg('Hubo un problema al leer el archivo.');
        };

        reader.readAsText(file);
    };

    const validarArchivo = (file) => {
        setErrorMsg('');
        setPreviewData([]); // Limpiamos preview anterior

        if (!file) return false;

        if (file.type !== 'text/csv' && !file.name.endsWith('.csv')) {
            setErrorMsg('Solo se aceptan archivos .csv');
            setArchivo(null);
            return false;
        }

        if (file.size > MAX_SIZE_BYTES) {
            setErrorMsg(`El archivo excede el límite de ${MAX_SIZE_MB}MB`);
            setArchivo(null);
            return false;
        }

        return true;
    };

    const handleDragOver = (e) => {
        e.preventDefault();
        setIsDragging(true);
    };

    const handleDragLeave = (e) => {
        e.preventDefault();
        setIsDragging(false);
    };

    const handleDrop = (e) => {
        e.preventDefault();
        setIsDragging(false);

        const droppedFile = e.dataTransfer.files[0];
        if (validarArchivo(droppedFile)) {
            setArchivo(droppedFile);
            procesarCSV(droppedFile); // ¡Llamamos a la lectura aquí!
        }
    };

    const handleFileSelect = (e) => {
        const selectedFile = e.target.files[0];
        if (validarArchivo(selectedFile)) {
            setArchivo(selectedFile);
            procesarCSV(selectedFile); // ¡Llamamos a la lectura aquí!
        }
    };

    const handleImportar = async () => {
        setIsSubmitting(true);
        setErrorMsg('');

        try {
            const token = localStorage.getItem('token');
            const formData = new FormData();

            // 'file' es el nombre del campo que tu backend FastAPI está esperando
            formData.append('file', archivo);

            const response = await fetch(
                `/api/cursos/${cursoId}/estudiantes/csv`,
                {
                    method: 'POST',
                    headers: {
                        Authorization: `Bearer ${token}`,
                        // Nota: No se pone 'Content-Type' cuando usamos FormData, el navegador lo calcula solo.
                    },
                    body: formData,
                }
            );

            const data = await response.json();

            if (response.ok) {
                setResultado(data);
            } else {
                setErrorMsg(
                    data.detail || `Error del servidor (${response.status})`
                );
            }
        } catch (error) {
            console.error('Error subiendo CSV:', error);
            setErrorMsg('Error de conexión con el servidor.');
        } finally {
            setIsSubmitting(false);
        }
    };

    return (
        <div style={{ maxWidth: '700px', margin: '0 auto', padding: '20px' }}>
            <button
                onClick={onVolver}
                style={{
                    marginBottom: '20px',
                    cursor: 'pointer',
                    background: 'none',
                    border: 'none',
                    color: '#4f46e5',
                    fontWeight: 'bold',
                }}
            >
                &larr; Volver al Dashboard
            </button>

            <h2>Importar Estudiantes por CSV</h2>

            <div
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
                style={{
                    border: isDragging
                        ? '2px dashed #4f46e5'
                        : '2px dashed #d1d5db',
                    backgroundColor: isDragging ? '#eef2ff' : '#f9fafb',
                    padding: '40px',
                    textAlign: 'center',
                    borderRadius: '8px',
                    cursor: 'pointer',
                    transition: 'all 0.2s ease',
                    marginBottom: '20px',
                }}
                onClick={() => document.getElementById('csvInput').click()}
            >
                <input
                    type="file"
                    id="csvInput"
                    data-testid="csv-input"
                    accept=".csv"
                    onChange={handleFileSelect}
                    style={{ display: 'none' }}
                />
                <p style={{ margin: 0, color: '#4b5563', fontWeight: 'bold' }}>
                    {archivo
                        ? `Archivo seleccionado: ${archivo.name}`
                        : 'Arrastra tu archivo CSV aquí o haz clic para buscar'}
                </p>
            </div>

            {errorMsg && (
                <div
                    style={{
                        color: '#b91c1c',
                        backgroundColor: '#fef2f2',
                        border: '1px solid #f87171',
                        padding: '10px',
                        borderRadius: '4px',
                        marginBottom: '20px',
                    }}
                >
                    {errorMsg}
                </div>
            )}

            {/* Renderizado condicional de la tabla Preview */}
            {previewData.length > 0 && (
                <div>
                    <h3 style={{ fontSize: '1.1rem', color: '#374151' }}>
                        Vista Previa (Primeras {previewData.length} filas)
                    </h3>
                    <div style={{ overflowX: 'auto', marginBottom: '20px' }}>
                        <table
                            style={{
                                width: '100%',
                                borderCollapse: 'collapse',
                                textAlign: 'left',
                                border: '1px solid #e5e7eb',
                            }}
                        >
                            <thead style={{ backgroundColor: '#f3f4f6' }}>
                                <tr>
                                    <th
                                        style={{
                                            padding: '12px',
                                            borderBottom: '1px solid #e5e7eb',
                                        }}
                                    >
                                        Nombre
                                    </th>
                                    <th
                                        style={{
                                            padding: '12px',
                                            borderBottom: '1px solid #e5e7eb',
                                        }}
                                    >
                                        Apellido
                                    </th>
                                    <th
                                        style={{
                                            padding: '12px',
                                            borderBottom: '1px solid #e5e7eb',
                                        }}
                                    >
                                        Correo
                                    </th>
                                </tr>
                            </thead>
                            <tbody>
                                {previewData.map((estudiante, index) => (
                                    <tr
                                        key={index}
                                        style={{
                                            borderBottom: '1px solid #e5e7eb',
                                        }}
                                    >
                                        <td style={{ padding: '12px' }}>
                                            {estudiante.nombre}
                                        </td>
                                        <td style={{ padding: '12px' }}>
                                            {estudiante.apellido}
                                        </td>
                                        <td style={{ padding: '12px' }}>
                                            {estudiante.correo}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>

                    <button
                        onClick={handleImportar}
                        disabled={isSubmitting}
                        style={{
                            width: '100%',
                            padding: '12px',
                            backgroundColor: isSubmitting
                                ? '#6b7280'
                                : '#10b981',
                            color: 'white',
                            border: 'none',
                            borderRadius: '6px',
                            cursor: isSubmitting ? 'not-allowed' : 'pointer',
                            fontWeight: 'bold',
                            fontSize: '1rem',
                        }}
                    >
                        {isSubmitting
                            ? 'Importando...'
                            : `Importar ${totalFilas} ${totalFilas === 1 ? 'estudiante' : 'estudiantes'}`}
                    </button>
                </div>
            )}

            {isSubmitting && (
                <div
                    style={{
                        textAlign: 'center',
                        padding: '20px',
                        color: '#6b7280',
                        fontWeight: 'bold',
                    }}
                >
                    Importando...
                </div>
            )}

            {resultado && (
                <div>
                    <div
                        style={{
                            display: 'flex',
                            gap: '12px',
                            marginBottom: '20px',
                            flexWrap: 'wrap',
                        }}
                    >
                        <div
                            style={{
                                flex: 1,
                                minWidth: '120px',
                                padding: '16px',
                                backgroundColor: '#f0fdf4',
                                border: '1px solid #86efac',
                                borderRadius: '8px',
                                textAlign: 'center',
                            }}
                        >
                            <div
                                style={{
                                    fontSize: '1.5rem',
                                    fontWeight: 'bold',
                                    color: '#16a34a',
                                }}
                            >
                                {resultado.imported}
                            </div>
                            <div
                                style={{
                                    fontSize: '0.875rem',
                                    color: '#15803d',
                                }}
                            >
                                Importados
                            </div>
                        </div>
                        <div
                            style={{
                                flex: 1,
                                minWidth: '120px',
                                padding: '16px',
                                backgroundColor: '#fefce8',
                                border: '1px solid #fde047',
                                borderRadius: '8px',
                                textAlign: 'center',
                            }}
                        >
                            <div
                                style={{
                                    fontSize: '1.5rem',
                                    fontWeight: 'bold',
                                    color: '#ca8a04',
                                }}
                            >
                                {resultado.duplicates}
                            </div>
                            <div
                                style={{
                                    fontSize: '0.875rem',
                                    color: '#a16207',
                                }}
                            >
                                Duplicados
                            </div>
                        </div>
                        <div
                            style={{
                                flex: 1,
                                minWidth: '120px',
                                padding: '16px',
                                backgroundColor: '#fef2f2',
                                border: '1px solid #fca5a5',
                                borderRadius: '8px',
                                textAlign: 'center',
                            }}
                        >
                            <div
                                style={{
                                    fontSize: '1.5rem',
                                    fontWeight: 'bold',
                                    color: '#dc2626',
                                }}
                            >
                                {resultado.errors.length}
                            </div>
                            <div
                                style={{
                                    fontSize: '0.875rem',
                                    color: '#b91c1c',
                                }}
                            >
                                Errores
                            </div>
                        </div>
                    </div>

                    {resultado.errors.length > 0 && (
                        <div
                            style={{
                                marginBottom: '20px',
                                padding: '12px',
                                backgroundColor: '#fef2f2',
                                border: '1px solid #fca5a5',
                                borderRadius: '8px',
                            }}
                        >
                            <h4
                                style={{
                                    margin: '0 0 8px 0',
                                    color: '#dc2626',
                                }}
                            >
                                Detalle de errores:
                            </h4>
                            <ul
                                style={{
                                    margin: 0,
                                    paddingLeft: '20px',
                                    color: '#b91c1c',
                                }}
                            >
                                {resultado.errors.map((err, i) => (
                                    <li key={i}>{err}</li>
                                ))}
                            </ul>
                        </div>
                    )}

                    {resultado.passwords && resultado.passwords.length > 0 && (
                        <div style={{ marginBottom: '20px' }}>
                            <h3
                                style={{
                                    fontSize: '1.1rem',
                                    color: '#374151',
                                    marginBottom: '12px',
                                }}
                            >
                                Contraseñas generadas
                            </h3>
                            <div
                                style={{
                                    overflowX: 'auto',
                                    marginBottom: '12px',
                                }}
                            >
                                <table
                                    style={{
                                        width: '100%',
                                        borderCollapse: 'collapse',
                                        textAlign: 'left',
                                        border: '1px solid #e5e7eb',
                                    }}
                                >
                                    <thead
                                        style={{
                                            backgroundColor: '#f3f4f6',
                                        }}
                                    >
                                        <tr>
                                            <th
                                                style={{
                                                    padding: '12px',
                                                    borderBottom:
                                                        '1px solid #e5e7eb',
                                                }}
                                            >
                                                Correo
                                            </th>
                                            <th
                                                style={{
                                                    padding: '12px',
                                                    borderBottom:
                                                        '1px solid #e5e7eb',
                                                }}
                                            >
                                                Contraseña
                                            </th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {resultado.passwords.map(
                                            (entry, index) => (
                                                <tr
                                                    key={index}
                                                    style={{
                                                        borderBottom:
                                                            '1px solid #e5e7eb',
                                                    }}
                                                >
                                                    <td
                                                        style={{
                                                            padding: '12px',
                                                        }}
                                                    >
                                                        {entry.correo}
                                                    </td>
                                                    <td
                                                        style={{
                                                            padding: '12px',
                                                            fontFamily:
                                                                'monospace',
                                                        }}
                                                    >
                                                        {entry.password}
                                                    </td>
                                                </tr>
                                            )
                                        )}
                                    </tbody>
                                </table>
                            </div>
                            <button
                                onClick={() => {
                                    const csv =
                                        'correo,contraseña\n' +
                                        resultado.passwords
                                            .map(
                                                (p) =>
                                                    `${p.correo},${p.password}`
                                            )
                                            .join('\n');
                                    const blob = new Blob([csv], {
                                        type: 'text/csv',
                                    });
                                    const url = URL.createObjectURL(blob);
                                    const a = document.createElement('a');
                                    a.href = url;
                                    a.download =
                                        'contrasenas_estudiantes.csv';
                                    a.click();
                                    URL.revokeObjectURL(url);
                                }}
                                style={{
                                    width: '100%',
                                    padding: '12px',
                                    backgroundColor: '#f59e0b',
                                    color: 'white',
                                    border: 'none',
                                    borderRadius: '6px',
                                    cursor: 'pointer',
                                    fontWeight: 'bold',
                                    fontSize: '1rem',
                                }}
                            >
                                Descargar CSV con contraseñas
                            </button>
                        </div>
                    )}

                    <button
                        onClick={() => {
                            setArchivo(null);
                            setPreviewData([]);
                            setTotalFilas(0);
                            setResultado(null);
                            setErrorMsg('');
                        }}
                        style={{
                            width: '100%',
                            padding: '12px',
                            backgroundColor: '#4f46e5',
                            color: 'white',
                            border: 'none',
                            borderRadius: '6px',
                            cursor: 'pointer',
                            fontWeight: 'bold',
                            fontSize: '1rem',
                        }}
                    >
                        Importar otro archivo
                    </button>
                </div>
            )}
        </div>
    );
};
