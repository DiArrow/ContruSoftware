import { useState, useRef } from 'react';
import { apiPostFormData } from '../api/client';

// NOTA: Recuerda importar aquí tu IconUpload

export default function FileUpload({ articulos = [], onFileUploaded }) {
    const [cantidad, setCantidad] = useState(1);
    const [articuloSeleccionado, setArticuloSeleccionado] = useState('');
    const [archivos, setArchivos] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [success, setSuccess] = useState(null);
    const [dragActive, setDragActive] = useState(false);

    const inputRef = useRef(null);

    const handleDrag = (e) => {
        e.preventDefault();
        e.stopPropagation();
        if (e.type === 'dragenter' || e.type === 'dragover') {
            setDragActive(true);
        } else if (e.type === 'dragleave') {
            setDragActive(false);
        }
    };

    const handleDrop = (e) => {
        e.preventDefault();
        e.stopPropagation();
        setDragActive(false);
        if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
            setArchivos(Array.from(e.dataTransfer.files));
        }
    };

    const handleChange = (e) => {
        if (e.target.files && e.target.files.length > 0) {
            setArchivos(Array.from(e.target.files));
        }
        // Esto es clave: resetea el valor para que puedas volver a seleccionar el mismo archivo si te equivocas
        e.target.value = null;
    };

    const onButtonClick = () => {
        if (inputRef.current) {
            inputRef.current.click();
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();

        // Validaciones antes de enviar
        if (archivos.length === 0) {
            setError('Por favor, selecciona al menos un archivo.');
            return;
        }
        if (!articuloSeleccionado) {
            setError('Por favor, selecciona un artículo de la lista.');
            return;
        }

        setLoading(true);
        setError(null);
        setSuccess(null);

        const formData = new FormData();
        formData.append('cantidad', cantidad);
        formData.append('ref_articulo', articuloSeleccionado);

        archivos.forEach((file) => {
            formData.append('archivos', file);
        });

        try {
            // Petición real al backend
            const data = await apiPostFormData('impresiones', formData);
            setSuccess('¡Solicitud enviada con éxito!');

            // RESTAURAMOS EL FORMATO: Le damos al componente padre exactamente lo que necesita para mostrar la notificación
            if (onFileUploaded) {
                onFileUploaded({
                    id: data.id_impresion || Date.now(),
                    text:
                        archivos.length === 1
                            ? `El archivo ${archivos[0].name} se subió correctamente`
                            : `Se subieron ${archivos.length} archivos correctamente`,
                    time: 'Ahora',
                });
            }

            // Limpiamos el formulario para permitir una nueva subida
            setCantidad(1);
            setArticuloSeleccionado('');
            setArchivos([]);
        } catch (err) {
            // Si el backend no existe, está apagado o falla, te lo dirá aquí en color rojo
            setError(
                err.message ||
                    'Error de conexión con el servidor. Verifica que el backend esté funcionando.'
            );
        } finally {
            setLoading(false);
        }
    };

    return (
        <div
            onDragEnter={handleDrag}
            onDragOver={handleDrag}
            onDragLeave={handleDrag}
            onDrop={handleDrop}
            style={{
                border: dragActive ? '2px dashed #5b21b6' : '2px dashed #ddd',
                backgroundColor: dragActive ? '#ede9fe' : '#fafafa',
                borderRadius: '16px',
                padding: archivos.length > 0 ? '30px 18px' : '40px 20px',
                textAlign: 'center',
                cursor: 'pointer',
                transition: 'all 0.2s ease',
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                gap: '12px',
                width: '100%',
                maxWidth: archivos.length > 0 ? '460px' : '500px',
                margin: '20px auto',
                boxSizing: 'border-box',
                marginTop: '-2px',
            }}
            onClick={onButtonClick}
        >
            <input
                ref={inputRef}
                type="file"
                style={{ display: 'none' }}
                onChange={handleChange}
                onClick={(e) => e.stopPropagation()} // <-- Evita que el archivo no cargue por conflicto de clicks
                multiple={true}
            />

            {/* Aquí debes poner tu componente original <IconUpload /> */}
            <div style={{ fontSize: '30px', marginBottom: '10px' }}>📁</div>

            {/* Mensajes de Error y Éxito */}
            {error && (
                <div
                    style={{
                        color: '#dc2626',
                        backgroundColor: '#fee2e2',
                        padding: '10px',
                        borderRadius: '8px',
                        width: '100%',
                        fontSize: '14px',
                        boxSizing: 'border-box',
                        fontWeight: 500,
                    }}
                    onClick={(e) => e.stopPropagation()}
                >
                    {error}
                </div>
            )}

            {success && (
                <div
                    style={{
                        color: '#16a34a',
                        backgroundColor: '#dcfce7',
                        padding: '10px',
                        borderRadius: '8px',
                        width: '100%',
                        fontSize: '14px',
                        boxSizing: 'border-box',
                        fontWeight: 500,
                    }}
                    onClick={(e) => e.stopPropagation()}
                >
                    {success}
                </div>
            )}

            <div
                style={{
                    display: 'flex',
                    gap: '12px',
                    width: '100%',
                    boxSizing: 'border-box',
                }}
                onClick={(e) => e.stopPropagation()}
            >
                <div style={{ flex: 1, textAlign: 'left' }}>
                    <label
                        htmlFor="cantidad"
                        style={{
                            display: 'block',
                            marginBottom: '4px',
                            fontSize: '13px',
                            fontWeight: '600',
                            color: '#374151',
                        }}
                    >
                        Cantidad
                    </label>
                    <input
                        id="cantidad"
                        type="number"
                        min="1"
                        value={cantidad}
                        onChange={(e) =>
                            setCantidad(parseInt(e.target.value) || 1)
                        }
                        style={{
                            width: '100%',
                            padding: '8px 12px',
                            borderRadius: '8px',
                            border: '1px solid #ddd',
                            boxSizing: 'border-box',
                        }}
                    />
                </div>
                <div style={{ flex: 2, textAlign: 'left' }}>
                    <label
                        htmlFor="articulo"
                        style={{
                            display: 'block',
                            marginBottom: '4px',
                            fontSize: '13px',
                            fontWeight: '600',
                            color: '#374151',
                        }}
                    >
                        Artículo
                    </label>
                    <select
                        id="articulo"
                        value={articuloSeleccionado}
                        onChange={(e) =>
                            setArticuloSeleccionado(e.target.value)
                        }
                        style={{
                            width: '100%',
                            padding: '8px 12px',
                            borderRadius: '8px',
                            border: '1px solid #ddd',
                            boxSizing: 'border-box',
                            backgroundColor: '#fff',
                        }}
                    >
                        <option value="">Seleccione un artículo...</option>
                        {articulos.map((art) => (
                            <option
                                key={art.id_articulo}
                                value={art.id_articulo}
                            >
                                {art.nombre_articulo}
                            </option>
                        ))}
                    </select>
                </div>
            </div>

            <div style={{ width: '100%', maxWidth: '100%' }}>
                <p
                    style={{
                        margin: '0 0 6px 0',
                        fontWeight: '600',
                        color: '#374151',
                    }}
                >
                    {archivos.length > 0
                        ? 'Archivos seleccionados:'
                        : 'Arrastra tus archivos aquí o haz clic para buscar'}
                </p>

                {archivos.length > 0 ? (
                    <div
                        style={{
                            width: '100%',
                            maxHeight: '120px',
                            overflowY: 'auto',
                            padding: '2px 0',
                        }}
                        onClick={(e) => e.stopPropagation()}
                    >
                        {archivos.map((file, idx) => (
                            <p
                                key={idx}
                                style={{
                                    margin: '4px 0',
                                    fontSize: '13px',
                                    color: '#6b7280',
                                    overflowWrap: 'anywhere',
                                    wordBreak: 'break-word',
                                }}
                            >
                                📄 <strong>{file.name}</strong> (
                                {(file.size / 1024).toFixed(1)} KB)
                            </p>
                        ))}
                    </div>
                ) : (
                    <p
                        style={{
                            margin: 0,
                            fontSize: '14px',
                            color: '#6b7280',
                            overflowWrap: 'anywhere',
                            wordBreak: 'break-word',
                        }}
                    >
                        Soporta cualquier formato de impresión
                    </p>
                )}
            </div>

            {archivos.length > 0 && (
                <button
                    type="button"
                    disabled={loading}
                    onClick={(e) => {
                        e.stopPropagation();
                        handleSubmit(e);
                    }}
                    style={{
                        marginTop: '10px',
                        padding: '10px 20px',
                        backgroundColor: loading ? '#9ca3af' : '#5b21b6',
                        color: 'white',
                        border: 'none',
                        borderRadius: '8px',
                        cursor: loading ? 'not-allowed' : 'pointer',
                        fontWeight: '600',
                        width: '100%',
                        transition: 'background-color 0.2s',
                    }}
                >
                    {loading ? 'Subiendo archivos...' : 'Enviar Impresión'}
                </button>
            )}
        </div>
    );
}
