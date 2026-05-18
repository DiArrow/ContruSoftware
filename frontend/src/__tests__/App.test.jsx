import { describe, it, expect } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import App from '../App';

describe('Suite de pruebas generales', () => {
  it('Debe renderizar el Dashboard y el mensaje de bienvenida correctamente', () => {
    render(<App />);

    // Verificamos logo de la Sidebar
    const logo = screen.getByText((content, element) => {
      return (
        element.tagName.toLowerCase() === 'span' && content.includes('MakerBox')
      );
    });
    expect(logo).toBeInTheDocument();

    // Verificamos mensaje de bienvenida del Topbar
    const bienvenida = screen.getByText(
      /Tu espacio de creación y aprendizaje/i
    );
    expect(bienvenida).toBeInTheDocument();
  });
});

describe('Suite de pruebas para la Sidebar', () => {
  const items = ["Dashboard", "Students", "Inventory", "Reports", "Courses", "Settings"];

  items.forEach((label) => {
  it('Debe resaltar el icono de ' + label + ' al ser seleccionado', () => {
    render(<App />);
    const button = screen.getByTitle(label);
    fireEvent.click(button);
    expect(button).toHaveStyle('background-color: rgb(237, 233, 254)');
  });
  });
});