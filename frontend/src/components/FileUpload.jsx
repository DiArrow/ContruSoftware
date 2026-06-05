import { useState, useRef } from 'react';

const IconUpload = () => (
    <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" color="#5b21b6">
        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
        <polyline points="17 8 12 3 7 8" />
        <line x1="12" y1="3" x2="12" y2="15" />
    </svg>
);

export default function FileUpload() {
    const [dragActive, setDragActive] = useState(false);
    const [file, setFile] = useState(null);
    const inputRef = useRef(null);

    const handleDrag = (e) => {
        e.preventDefault();
        e.stopPropagation();
        if (e.type === "dragenter" || e.type === "dragover") {
            setDragActive(true);
        } else if (e.type === "dragleave") {
            setDragActive(false);
        }
    };

    const handleDrop = (e) => {
        e.preventDefault();
        e.stopPropagation();
        setDragActive(false);
        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            setFile(e.dataTransfer.files[0]);
        }
    };

    const handleChange = (e) => {
        e.preventDefault();
        if (e.target.files && e.target.files[0]) {
            setFile(e.target.files[0]);
        }
    };

    const onButtonClick = () => {
        inputRef.current.click();
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
                padding: '40px 20px',
                textAlign: 'center',
                cursor: 'pointer',
                transition: 'all 0.2s ease',
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                gap: '12px',
                width: '100%',
                maxWidth: '500px',
                margin: '20px auto',
                boxSizing: 'border-box'
            }}
            onClick={onButtonClick}
        >
            <input 
                ref={inputRef}
                type="file" 
                style={{ display: 'none' }} 
                onChange={handleChange}
                multiple={false}
            />
            <IconUpload />
            <div>
                <p style={{ margin: '0 0 4px 0', fontWeight: '600', color: '#374151' }}>
                    {file ? 'Archivo seleccionado:' : 'Arrastra tu archivo aquí o haz clic para buscar'}
                </p>
                <p style={{ margin: 0, fontSize: '14px', color: '#6b7280' }}>
                    {file ? `${file.name} (${(file.size / 1024).toFixed(1)} KB)` : 'Soporta cualquier formato de impresión'}
                </p>
            </div>
            {file && (
                <button
                    onClick={(e) => {
                        e.stopPropagation();
                        alert(`Enviando ${file.name} a la cola de impresión...`);
                        // Aquí conectarías con tu endpoint de backend en el futuro
                    }}
                    style={{
                        marginTop: '10px',
                        padding: '10px 20px',
                        backgroundColor: '#5b21b6',
                        color: 'white',
                        border: 'none',
                        borderRadius: '8px',
                        cursor: 'pointer',
                        fontWeight: '600'
                    }}
                >
                    Enviar Impresión
                </button>
            )}
        </div>
    );
}