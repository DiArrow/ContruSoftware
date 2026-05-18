import { useState } from 'react';
import './index.css';

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
const IconChart = () => (
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
    <line x1="18" y1="20" x2="18" y2="10" />
    <line x1="12" y1="20" x2="12" y2="4" />
    <line x1="6" y1="20" x2="6" y2="14" />
    <line x1="2" y1="20" x2="22" y2="20" />
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

//Items de navegación
const navItems = [
  { icon: <IconGrid />, label: 'Dashboard' },
  { icon: <IconUsers />, label: 'Students' },
  { icon: <IconBag />, label: 'Inventory' },
  { icon: <IconChart />, label: 'Reports' },
  { icon: <IconBook />, label: 'Courses' },
  { icon: <IconSettings />, label: 'Settings' },
];

// Sidebar
function Sidebar() {
  const [active, setActive] = useState(0);
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
        {navItems.map((item, i) => (
          <button
            key={i}
            onClick={() => setActive(i)}
            title={item.label}
            style={{
              width: '44px',
              height: '44px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              borderRadius: '12px',
              border: 'none',
              backgroundColor: active === i ? '#ede9fe' : 'transparent',
              color: active === i ? '#5b21b6' : '#9ca3af',
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
function Topbar() {
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
          {/* fontWeight: 100 para el texto general y 750 para el mensaje destacado */}
          Bienvenid@ a MakerBox,{' '}
          <strong style={{ fontWeight: 750 }}>
            tu espacio de creación y aprendizaje
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
        {/* Campana */}
        <button
          title="Notificaciones"
          style={{
            width: '40px',
            height: '40px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            borderRadius: '12px',
            border: '1px solid rgba(0,0,0,0.08)',
            backgroundColor: '#ffffff',
            color: '#6b7280',
            cursor: 'pointer',
            position: 'relative',
            transition: 'background 0.2s, color 0.2s',
          }}
        >
          <IconBell />

          {/* Badge de notificación */}
          <span
            style={{
              position: 'absolute',
              top: '8px',
              right: '8px',
              width: '7px',
              height: '7px',
              borderRadius: '50%',
              backgroundColor: '#7c3aed',
              border: '1.5px solid #ffffff',
            }}
          />
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
          <IconUser />
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
  },
  CentralPanel: {
    ...baseCard,
    height: 'var(--central-panel-height)',
    border: '1px solid rgba(0, 0, 0, 0.08)',
    marginTop: '70px',
    marginBottom: '30px',
  },
  LowerPanel: {
    ...baseCard,
    height: 'var(--lower-panel-height)',
    border: '1px solid rgba(0, 0, 0, 0.08)',
  },
};

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

function CentralPanel({ children }) {
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
      {children}
    </div>
  );
}

//App (llamada de funciones)
export default function App() {
  return (
    <div style={{ display: 'flex', minHeight: '100vh' }}>
      <Sidebar />

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
            <Topbar />
            <p></p>
          </TopPanel>

          <CentralPanel>
            <p></p>
          </CentralPanel>

          <LowerPanel>
            <p></p>
          </LowerPanel>
        </div>
      </div>
    </div>
  );
}
