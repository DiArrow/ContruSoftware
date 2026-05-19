import { describe, it, expect } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import App from '../App';

function AccederSeccionLogin() {
  fireEvent.change(screen.getByPlaceholderText(/Usuario/i), {
    target: { value: 'usuario@utalca.cl' },
  });
  fireEvent.change(screen.getByPlaceholderText(/Contraseña/i), {
    target: { value: 'usuario' },
  });
  fireEvent.click(screen.getByText(/Acceder/i));
}

describe('Suite de pruebas tras login', () => {
  it('Debe mostrar la página principal después de un login exitoso', () => {
    render(<App />);
    AccederSeccionLogin();

    expect(screen.getByText(/Bienvenid@ a MakerBox/i)).toBeInTheDocument();
  });
});

describe('Suite de pruebas para el click en la sidebar', () => {
  it('Debe mostrar la sección seleccionada al hacer clic en la sidebar', () => {
    render(<App />);
    AccederSeccionLogin();

    const items = [
      'Dashboard',
      'Students',
      'Inventory',
      'Reports',
      'Courses',
      'Settings',
    ];
    items.forEach((label) => {
      const button = screen.getByTitle(label);
      fireEvent.click(button);
      expect(button).toHaveStyle('background-color: rgb(237, 233, 254)');
    });
  });
});
