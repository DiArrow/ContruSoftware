import React from 'react';

const SimpleChart = () => {
    const data = [
        { month: 'Ene', total: 35 },
        { month: 'Feb', total: 55 },
        { month: 'Mar', total: 78 },
        { month: 'Abr', total: 45 },
        { month: 'May', total: 62 },
        { month: 'Jun', total: 95 },
    ];
    const maxVal = 100;
    const chartHeight = 130;

    return (
        <div style={{
            padding: '20px',
            backgroundColor: '#ffffff',
            borderRadius: '16px',
            border: '1px solid rgba(0, 0, 0, 0.05)',
            width: '100%',
            maxWidth: '520px',
            boxSizing: 'border-box',
            zIndex: 10
        }}>
            <h4 style={{ margin: '0 0 4px 0', color: '#1f2937', fontSize: '16px', fontWeight: 600 }}>
                Resumen de Actividad
            </h4>
            <p style={{ margin: '0 0 20px 0', color: '#6b7280', fontSize: '12px' }}>
                Solicitudes mensuales en el sistema
            </p>

            <div style={{
                display: 'flex',
                alignItems: 'flex-end',
                justifyContent: 'space-between',
                height: `${chartHeight}px`,
                borderBottom: '2px solid #e5e7eb',
                paddingBottom: '4px',
                gap: '12px'
            }}>
                {data.map((item, index) => {
                    const barHeight = (item.total / maxVal) * chartHeight;
                    return (
                        <div key={index} style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', flex: 1 }}>
                            <div style={{
                                width: '100%',
                                height: `${barHeight}px`,
                                backgroundColor: '#7c3aed',
                                borderRadius: '4px 4px 0 0',
                                position: 'relative',
                                display: 'flex',
                                justifyContent: 'center'
                            }}>
                                <span style={{ position: 'absolute', top: '-22px', fontSize: '11px', fontWeight: '600', color: '#7c3aed' }}>
                                    {item.total}
                                </span>
                            </div>
                            <span style={{ marginTop: '8px', fontSize: '12px', color: '#4b5563', fontWeight: '500' }}>
                                {item.month}
                            </span>
                        </div>
                    );
                })}
            </div>
        </div>
    );
};

export default SimpleChart;