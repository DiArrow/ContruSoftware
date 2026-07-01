import { useState } from 'react';
import Login from './components/Login';
import FileUpload from './components/FileUpload';
import { AuthProvider, useAuth } from './context/AuthContext';
import SimpleChart from './components/SimpleChart';
import UserRegistrationForm from './components/UserRegistrationForm';
import { DashboardDocente } from './components/DashboardDocente';
import { DashboardEstudiante } from './components/DashboardEstudiante';
import { HistorialImpresiones } from './components/HistorialImpresiones';
import { ImportadorCSV } from './components/ImportadorCSV';
import SemestresPage from './components/SemestresPage';

//Iconos presentes mediante figuras geométricas
//Iconos para la sidebar
const IconGrid = () => (
    <svg
        width="20"
        height="20"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
    >
        <rect x="3" y="3" width="7" height="7" />
        <rect x="14" y="3" width="7" height="7" />
        <rect x="3" y="14" width="7" height="7" />
        <rect x="14" y="14" width="7" height="7" />
    </svg>
);
const IconUsers = () => (
    <svg
        width="20"
        height="20"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
    >
        <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
        <circle cx="9" cy="7" r="4" />
        <path d="M23 21v-2a4 4 0 0 0-3-3.87" />
        <path d="M16 3.13a4 4 0 0 1 0 7.75" />
    </svg>
);
const IconBag = () => (
    <svg
        width="20"
        height="20"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
    >
        <path d="M6 2 3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4z" />
        <line x1="3" y1="6" x2="21" y2="6" />
        <path d="M16 10a4 4 0 0 1-8 0" />
    </svg>
);
const IconPrinter = () => (
    <svg
        width="20"
        height="20"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
    >
        <polyline points="6 9 6 2 18 2 18 9" />
        <path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2" />
        <rect x="6" y="14" width="12" height="8" />
    </svg>
);
const IconSettings = () => (
    <svg
        width="20"
        height="20"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
    >
        <circle cx="12" cy="12" r="3" />
        <path d="M19.07 4.93l-1.41 1.41M4.93 4.93l1.41 1.41M4.93 19.07l1.41-1.41M19.07 19.07l-1.41-1.41M12 2v2M12 20v2M2 12h2M20 12h2" />
    </svg>
);
const IconBox = () => (
    <svg
        width="26"
        height="26"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
    >
        <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z" />
        <polyline points="3.27 6.96 12 12.01 20.73 6.96" />
        <line x1="12" y1="22.08" x2="12" y2="12" />
    </svg>
);

//Iconos para el topbar
const IconBell = () => (
    <svg
        width="20"
        height="20"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
    >
        <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9" />
        <path d="M13.73 21a2 2 0 0 1-3.46 0" />
    </svg>
);
const IconUser = () => (
    <svg
        width="20"
        height="20"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
    >
        <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
        <circle cx="12" cy="7" r="4" />
    </svg>
);
const IconLogout = () => (
    <svg
        width="20"
        height="20"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
    >
        <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
        <polyline points="16 17 21 12 16 7" />
        <line x1="21" y1="12" x2="9" y2="12" />
    </svg>
);

//Icono para el central panel
const IconCentral = () => (
    <svg
        width="100"
        height="100"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
    >
        <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z" />
        <polyline points="3.27 6.96 12 12.01 20.73 6.96" />
        <line x1="12" y1="22.08" x2="12" y2="12" />
    </svg>
);

const IconCalendar = () => (
    <svg
        width="20"
        height="20"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
    >
        <rect x="3" y="4" width="18" height="18" rx="2" ry="2" />
        <line x1="16" y1="2" x2="16" y2="6" />
        <line x1="8" y1="2" x2="8" y2="6" />
        <line x1="3" y1="10" x2="21" y2="10" />
    </svg>
);
const IconBook = () => (
    <svg
        width="20"
        height="20"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
    >
        <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20" />
        <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z" />
    </svg>
);

//Items de navegación
const navItems = [
    { icon: <IconGrid />, label: 'Dashboard', roles: ['EST', 'SOL', 'PRO', 'AYU', 'ADM'] },
    { icon: <IconCalendar />, label: 'Semestres', roles: ['PRO', 'ADM'] },
    { icon: <IconUsers />, label: 'Estudiantes', roles: ['PRO', 'ADM'] },
    { icon: <IconBag />, label: 'Inventario', roles: ['PRO', 'ADM'] },
    { icon: <IconPrinter />, label: 'Impresiones', roles: ['AYU', 'ADM', 'EST', 'SOL'] },
    { icon: <IconSettings />, label: 'Ajustes', roles: ['ADM'] },
    { icon: <IconBook />, label: 'Mis Cursos', roles: ['EST'] },
    { icon: <IconPrinter />, label: 'Historial Impresiones', roles: ['EST', 'SOL'] },
];

// Sidebar
function Sidebar({ active, setActive, currentUser }) {
    const userRole = currentUser?.rol;
    const visibleItems = navItems.filter(
        (item) => !item.roles || item.roles.includes(userRole)
    );

    return (
        <aside
            style={{
                width: '72px',
                minWidth: '72px',
                backgroundColor: '#ffffff',
                borderRight: '1px solid rgba(0,0,0,0.07)',
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                padding: '16px 0 24px',
                position: 'sticky',
                top: 0,
                height: '100vh',
                boxSizing: 'border-box',
                boxShadow: '2px 0 10px rgba(0,0,0,0.04)',
                zIndex: 100,
            }}
        >
            {/* Logo y características */}
            <div
                style={{
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                    marginBottom: '28px',
                    gap: '4px',
                }}
            >
                <div
                    style={{
                        width: '44px',
                        height: '44px',
                        backgroundColor: '#ede9fe',
                        borderRadius: '12px',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        color: '#5b21b6',
                    }}
                >
                    <IconBox />
                </div>
                <span
                    style={{
                        fontSize: '9px',
                        fontWeight: 700,
                        color: '#5b21b6',
                        letterSpacing: '0.05em',
                        textTransform: 'uppercase',
                    }}
                >
                    MakerBox
                </span>
            </div>

            {/* Navegación y características */}
            <nav
                style={{
                    display: 'flex',
                    flexDirection: 'column',
                    gap: '4px',
                    flex: 1,
                }}
            >
                {visibleItems.map((item) => (
                    <button
                        key={item.label}
                        onClick={() => setActive(navItems.indexOf(item))}
                        title={item.label}
                        style={{
                            width: '44px',
                            height: '44px',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            borderRadius: '12px',
                            border: 'none',
                            backgroundColor:
                                active === navItems.indexOf(item)
                                    ? '#ede9fe'
                                    : 'transparent',
                            color:
                                active === navItems.indexOf(item)
                                    ? '#5b21b6'
                                    : '#9ca3af',
                            cursor: 'pointer',
                            transition: 'background 0.2s, color 0.2s',
                        }}
                    >
                        {item.icon}
                    </button>
                ))}
            </nav>
        </aside>
    );
}

//Topbar
function Topbar({ user, onLogout, notifications, hasUnread, setHasUnread }) {
    const [isOpen, setIsOpen] = useState(false);
    return (
        <div
            style={{
                width: '100%',
                height: '64px',
                display: 'flex',
                alignItems: 'flex-start',
                padding: '0 8px 0',
                boxSizing: 'border-box',
                position: 'relative',
            }}
        >
            {/* Mensaje de bienvenida */}
            <div
                style={{
                    position: 'absolute',
                    left: '50%',
                    transform: 'translateX(-50%)',
                    display: 'flex',
                    alignItems: 'center',
                    paddingTop: '8px',
                }}
            >
                <p
                    style={{
                        fontSize: '19px',
                        color: '#374151',
                        fontWeight: 100,
                        margin: 0,
                    }}
                >
                    Bienvenid@ a MakerBox,{' '}
                    <strong style={{ fontWeight: 750 }}>
                        {user
                            ? user.nombre
                            : 'tu espacio de creación y aprendizaje'}
                    </strong>
                </p>
            </div>

            {/* Iconos */}
            <div
                style={{
                    position: 'absolute',
                    right: '8px',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '12px',
                }}
            >
                {/* Contenedor relativo para posicionar el menú flotante justo bajo la campana */}
                <div
                    style={{
                        position: 'relative',
                        display: 'flex',
                        alignItems: 'center',
                    }}
                >
                    {/* Campana */}
                    <button
                        title="Notificaciones"
                        onClick={() => {
                            setIsOpen(!isOpen);
                            if (!isOpen) {
                                setHasUnread(false);
                            }
                        }}
                        style={{
                            width: '40px',
                            height: '40px',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            borderRadius: '12px',
                            border: '1px solid rgba(0,0,0,0.08)',
                            backgroundColor: isOpen ? '#ede9fe' : '#ffffff',
                            color: isOpen ? '#5b21b6' : '#6b7280',
                            cursor: 'pointer',
                            position: 'relative',
                            transition: 'background 0.2s, color 0.2s',
                        }}
                    >
                        <IconBell />

                        {/* Badge de notificación */}
                        {hasUnread && (
                            <span
                                style={{
                                    position: 'absolute',
                                    top: '8px',
                                    right: '8px',
                                    width: '8px',
                                    height: '8px',
                                    borderRadius: '50%',
                                    backgroundColor: '#ef4444',
                                    border: '2px solid white',
                                }}
                            />
                        )}
                    </button>

                    {/* Menú Desplegable de Notificaciones */}
                    {isOpen && (
                        <div
                            style={{
                                position: 'absolute',
                                top: '48px',
                                right: '0',
                                width: '280px',
                                backgroundColor: '#ffffff',
                                borderRadius: '16px',
                                boxShadow: '0 10px 25px rgba(0,0,0,0.1)',
                                border: '1px solid rgba(0,0,0,0.06)',
                                padding: '12px 0',
                                zIndex: 200,
                                fontFamily: 'system-ui, sans-serif',
                            }}
                        >
                            <div
                                style={{
                                    padding: '0 16px 8px 16px',
                                    borderBottom: '1px solid #f3f4f6',
                                    display: 'flex',
                                    justifyContent: 'space-between',
                                    alignItems: 'center',
                                }}
                            >
                                <span
                                    style={{
                                        fontWeight: 600,
                                        fontSize: '14px',
                                        color: '#1f2937',
                                    }}
                                >
                                    Notificaciones
                                </span>
                            </div>

                            <div
                                style={{
                                    maxHeight: '240px',
                                    overflowY: 'auto',
                                }}
                            >
                                {notifications.map((notif) => (
                                    <div
                                        key={notif.id}
                                        style={{
                                            padding: '12px 16px',
                                            borderBottom: '1px solid #f9fafb',
                                            cursor: 'pointer',
                                            transition: 'background 0.2s',
                                            textAlign: 'left',
                                        }}
                                        onMouseEnter={(e) =>
                                            (e.currentTarget.style.backgroundColor =
                                                '#f9fafb')
                                        }
                                        onMouseLeave={(e) =>
                                            (e.currentTarget.style.backgroundColor =
                                                'transparent')
                                        }
                                    >
                                        <p
                                            style={{
                                                margin: '0 0 4px 0',
                                                fontSize: '13px',
                                                color: '#4b5563',
                                                lineHeight: '1.4',
                                                fontWeight: 'normal',
                                            }}
                                        >
                                            {notif.text}
                                        </p>
                                        <span
                                            style={{
                                                fontSize: '11px',
                                                color: '#9ca3af',
                                            }}
                                        >
                                            {notif.time}
                                        </span>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}
                </div>

                {/* Logout */}
                <button
                    style={{
                        width: '40px',
                        height: '40px',
                        borderRadius: '12px',
                        border: '1px solid rgba(0,0,0,0.08)',
                        background: '#fff',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        cursor: 'pointer',
                        transition: 'all 0.2s',
                        color: '#6b7280',
                    }}
                    onMouseEnter={(e) => {
                        e.currentTarget.style.background = '#ede9fe';
                        e.currentTarget.style.color = '#5b21b6';
                    }}
                    onMouseLeave={(e) => {
                        e.currentTarget.style.background = '#fff';
                        e.currentTarget.style.color = '#6b7280';
                    }}
                    title="Cerrar sesión"
                    onClick={onLogout}
                >
                    <IconLogout />
                </button>

                {/* Perfil */}
                <button
                    title="Perfil"
                    style={{
                        width: '40px',
                        height: '40px',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        borderRadius: '12px',
                        border: '1px solid rgba(0,0,0,0.08)',
                        backgroundColor: '#ede9fe',
                        color: '#5b21b6',
                        cursor: 'pointer',
                        transition: 'background 0.2s, color 0.2s',
                    }}
                >
                    {user ? (
                        <span
                            style={{
                                fontSize: '14px',
                                fontWeight: 600,
                            }}
                        >
                            {user.nombre.charAt(0).toUpperCase()}
                        </span>
                    ) : (
                        <IconUser />
                    )}
                </button>
            </div>
        </div>
    );
}

//Cards
const baseCard = {
    backgroundColor: '#ffffff',
    opacity: 0.95,
    width: 'min(90%, 1750px)',
    padding: '32px',
    borderRadius: '24px',
    boxShadow: '0 10px 30px rgba(0, 0, 0, 0.08)',
    position: 'relative',
    margin: '10px auto',
    boxSizing: 'border-box',
    transition: 'box-shadow 0.3s ease',
};

const hoverShadow = { boxShadow: '0 15px 40px rgba(0, 0, 0, 0.12)' };

const styles = {
    TopPanel: {
        ...baseCard,
        height: 'var(--top-panel-height)',
        paddingTop: '5px',
        position: 'relative',
        zIndex: 100,
    },
    CentralPanel: {
        ...baseCard,
        minHeight: 'var(--central-panel-height)',
        height: 'auto',
        border: '1px solid rgba(0, 0, 0, 0.08)',
        marginTop: '70px',
        marginBottom: '30px',
    },
    LowerPanel: {
        ...baseCard,
        minHeight: 'var(--lower-panel-height)',
        height: 'auto',
        border: '1px solid rgba(0, 0, 0, 0.08)',
        //paddingBottom: '30px',
    },
};

// Hook personalizado para gestionar el estado de los paneles
function useHover() {
    const [hovered, setHovered] = useState(false);
    return {
        hovered,
        onMouseEnter: () => setHovered(true),
        onMouseLeave: () => setHovered(false),
    };
}

function TopPanel({ children }) {
    const { hovered, ...handlers } = useHover();
    return (
        <div
            style={{
                ...styles.TopPanel,
                ...(hovered ? hoverShadow : {}),
                display: 'flex',
                flexDirection: 'column',
                gap: '18px',
            }}
            {...handlers}
        >
            {children}
        </div>
    );
}

function CentralPanel({ children, showDefaultLogo }) {
    const { hovered, ...handlers } = useHover();
    return (
        <div
            style={{
                ...styles.CentralPanel,
                ...(hovered ? hoverShadow : {}),
                display: 'flex',
                flexDirection: 'column',
                gap: '18px',
            }}
            {...handlers}
        >
            {children}

            {/* Logo makerbox (solo mostrar si showDefaultLogo es true) */}
            {showDefaultLogo && (
                <div
                    style={{
                        display: 'flex',
                        flexDirection: 'row', // Mantiene el logo y el texto lado a lado
                        alignItems: 'center', // Los centra verticalmente entre sí
                        justifyContent: 'flex-start', // ¡Alinea todo hacia el lado izquierdo!
                        width: '100%',
                        flex: 1,
                        gap: '40px', // Espacio entre el cubo y el texto
                        padding: '60px 24px', // 24px de margen a los lados para que respire
                    }}
                >
                    <div
                        style={{
                            width: '150px',
                            height: '150px',
                            backgroundColor: '#ede9fe',
                            borderRadius: '16px',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            color: '#5b21b6',
                            flexShrink: 0,
                        }}
                    >
                        <IconCentral />
                    </div>
                    <span
                        style={{
                            fontSize: '50px',
                            fontWeight: 100,
                            color: '#000000',
                            letterSpacing: '0.05em',
                            margin: 0,
                        }}
                    >
                        Proyectos realizados: 0
                    </span>
                </div>
            )}
        </div>
    );
}

function LowerPanel({ children }) {
    const { hovered, ...handlers } = useHover();
    return (
        <div
            style={{
                ...styles.LowerPanel,
                ...(hovered ? hoverShadow : {}),
                display: 'flex',
                flexDirection: 'column',
                gap: '18px',
            }}
            {...handlers}
        >
            <>
                <span
                    style={{
                        fontSize: '30px',
                        fontWeight: 100,
                        color: '#000000',
                        fontFamily: 'inter',
                        letterSpacing: '0.05em',
                    }}
                >
                    Progreso de proyecto actual: 20%
                </span>
                {children}
            </>
        </div>
    );
}

function AppContent() {
    const { currentUser, isAuthenticated, isLoading, logout } = useAuth();
    const [activeTab, setActiveTab] = useState(0);
    const [notifications, setNotifications] = useState([]);
    const [hasUnread, setHasUnread] = useState(false);
    const [cursoSeleccionadoId, setCursoSeleccionadoId] = useState(null); // <-- LÍNEA NUEVA
    const addNotification = (notification) => {
        setNotifications((prev) => [notification, ...prev]);
        setHasUnread(true);
    };
    const mockArticulos = [
        { id_articulo: 'art-001', nombre_articulo: 'Filamento PLA Morado' },
        { id_articulo: 'art-002', nombre_articulo: 'Resina Estándar Gris' },
        { id_articulo: 'art-003', nombre_articulo: 'Filamento ABS Negro' },
    ];

    if (isLoading) {
        return (
            <div
                style={{
                    height: '100vh',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    backgroundColor: '#f3f4f6',
                    fontFamily: 'Inter, sans-serif',
                    color: '#5b21b6',
                    fontSize: '18px',
                }}
            >
                Cargando...
            </div>
        );
    }

    if (!isAuthenticated) {
        return <Login />;
    }

    return (
        <div style={{ display: 'flex', minHeight: '100vh' }}>
            <Sidebar
                active={activeTab}
                setActive={setActiveTab}
                currentUser={currentUser}
            />
            <div
                style={{
                    flex: 1,
                    minWidth: 0,
                    display: 'flex',
                    flexDirection: 'column',
                }}
            >
                <div style={{ flex: 1, minWidth: 0 }}>
                    <TopPanel>
                        <Topbar
                            user={currentUser}
                            onLogout={logout}
                            notifications={notifications}
                            hasUnread={hasUnread}
                            setHasUnread={setHasUnread}
                        />
                    </TopPanel>
                    <CentralPanel showDefaultLogo={activeTab === 3}>
                        {activeTab === 1 && <SemestresPage />}
                        {activeTab === 4 && (
                            <FileUpload
                                onFileUploaded={addNotification}
                                articulos={mockArticulos}
                            />
                        )}
                        {activeTab === 5 && <UserRegistrationForm />}
                        {activeTab === 0 && (
                            <DashboardDocente
                                setActiveTab={setActiveTab}
                                setCursoSeleccionadoId={setCursoSeleccionadoId}
                            />
                        )}
                        {activeTab === 2 && (
                            <ImportadorCSV
                                cursoId={cursoSeleccionadoId}
                                onVolver={() => setActiveTab(0)}
                            />
                        )}
                        {activeTab === 6 && <DashboardEstudiante />}
                        {activeTab === 7 && <HistorialImpresiones />}
                    </CentralPanel>
                    {activeTab === 3 && (
                        <LowerPanel>
                            <SimpleChart />
                        </LowerPanel>
                    )}
                </div>
            </div>
        </div>
    );
}

export default function App() {
    return (
        <AuthProvider>
            <AppContent />
        </AuthProvider>
    );
}
