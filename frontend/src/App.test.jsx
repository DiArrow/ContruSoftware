import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import * as React from 'react';
import App from './App';

describe('Suite de pruebas generales', () => {
  it('debe renderizar el Dashboard y el mensaje de bienvenida correctamente', () => {
    render(<App />);

    // Verificamos el logo de la Sidebar
    const logo = screen.getByText((content, element) => {
    return element.tagName.toLowerCase() === 'span' && content.includes('MakerBox');
    });
    expect(logo).toBeInTheDocument();
    
    // Verificamos el mensaje de bienvenida del Topbar
    const bienvenida = screen.getByText(/tu espacio de creación y aprendizaje/i);
    expect(bienvenida).toBeInTheDocument();
  });
});