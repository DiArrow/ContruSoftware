export default function SimpleChart() {
    const valorActual = 20;
    const metaMax = 25;

    const porcentajeProgreso = (valorActual / metaMax) * 100;

    // Números para el eje X (abajo)
    const ticksX = [0, 5, 10, 15, 20, 25];

    // Números para el eje Y (izquierdo), distribuidos de arriba a abajo
    const ticksY = [25, 20, 15, 10, 5, 0];

    return (
        <div
            style={{
                width: '100%',
                padding: '10px 0',
                fontFamily: 'system-ui, -apple-system, sans-serif',
                boxSizing: 'border-box',
            }}
        >
            {/* CONTENEDOR PRINCIPAL DEL GRÁFICO (Agrandado a 240px de altura) */}
            <div
                style={{
                    display: 'flex',
                    width: '100%',
                    height: '340px',
                    alignItems: 'stretch',
                }}
            >
                {/* 1. EJE VERTICAL IZQUIERDO */}
                <div
                    style={{
                        display: 'flex',
                        flexDirection: 'column',
                        justifyContent: 'space-between',
                        alignItems: 'flex-end',
                        paddingRight: '12px',
                        width: '25px',
                        minWidth: '25px',
                        boxSizing: 'border-box',
                    }}
                >
                    {ticksY.map((num) => (
                        <span
                            key={num}
                            style={{
                                fontSize: '13px',
                                color: '#9ca3af',
                                lineHeight: '1',
                                transform: 'translateY(-1px)',
                            }}
                        >
                            {num}
                        </span>
                    ))}
                </div>

                {/* 2. ÁREA DE LA BARRA Y LÍNEAS DE FONDO */}
                <div style={{ position: 'relative', flex: 1, height: '100%' }}>
                    {/* Líneas grises de fondo */}
                    <div
                        style={{
                            position: 'absolute',
                            top: 0,
                            left: 0,
                            width: '100%',
                            height: '100%',
                            display: 'flex',
                            flexDirection: 'column',
                            justifyContent: 'space-between',
                            pointerEvents: 'none',
                        }}
                    >
                        {[1, 2, 3, 4, 5].map((_, index) => (
                            <div
                                key={index}
                                style={{
                                    width: '100%',
                                    borderTop: '1px solid #f3f4f6',
                                }}
                            />
                        ))}
                        <div
                            style={{
                                width: '100%',
                                borderTop: '1px solid #e5e7eb',
                            }}
                        />
                    </div>

                    {/* LA BARRA: Agrandada a 190px de grosor para comerse el espacio blanco */}
                    <div
                        style={{
                            position: 'absolute',
                            bottom: '0',
                            left: '0',
                            width: `${porcentajeProgreso}%`,
                            height: '190px', // Ocupa casi todo el alto del contenedor
                            background:
                                'linear-gradient(90deg, #4c1d95 0%, #6366f1 60%, #7dd3fc 100%)',
                            transition: 'width 0.5s ease-out',
                        }}
                    />
                </div>
            </div>

            {/* 3. EJE INFERIOR HORIZONTAL */}
            <div
                style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    width: '100%',
                    paddingLeft: '37px',
                    boxSizing: 'border-box',
                    borderTop: '1px solid #e5e7eb',
                    paddingTop: '8px',
                    marginTop: '4px',
                }}
            >
                {ticksX.map((num) => (
                    <span
                        key={num}
                        style={{
                            fontSize: '13px',
                            color: '#9ca3af',
                            fontWeight: '400',
                            width: '20px',
                            textAlign: 'center',
                        }}
                    >
                        {num}
                    </span>
                ))}
            </div>

            {/* NUEVO: CONTENEDOR DE TEXTO CENTRADO Y ALINEADO CON EL ANCHO REAL DE LA BARRA */}
            <div
                style={{
                    display: 'grid',
                    gridTemplateColumns: `${porcentajeProgreso}% 1fr`, // El primer tramo mide exactamente lo mismo que la barra (80%)
                    width: '100%',
                    paddingLeft: '37px',
                    boxSizing: 'border-box',
                    marginTop: '16px',
                }}
            >
                {/* Bloque del Proyecto: Centrado milimétricamente abajo de la barra azul */}
                <div
                    style={{
                        display: 'flex',
                        justifyContent: 'center',
                    }}
                >
                    <span
                        style={{
                            fontSize: '14px',
                            fontWeight: '600',
                            color: '#374151',
                            textTransform: 'uppercase',
                            letterSpacing: '0.02em',
                            fontFamily: 'inter',
                        }}
                    >
                        PROYECTO: CONSTRUCCIÓN DE SOFTWARE
                    </span>
                </div>

                {/* Bloque de la Meta: Se alinea justo en la esquina del límite 25 */}
                <div
                    style={{
                        display: 'flex',
                        justifyContent: 'flex-end',
                    }}
                >
                    <span
                        style={{
                            fontSize: '14px',
                            fontWeight: '500',
                            color: '#6b7280',
                        }}
                    >
                        Meta
                    </span>
                </div>
            </div>
        </div>
    );
}
