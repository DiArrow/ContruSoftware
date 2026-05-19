import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import Login from '../components/Login';

describe('Suite de pruebas para el componente Login', () => {
    it('Debe renderizar el formulario de inicio de sesión correctamente', () => {
        render(<Login />);

        //Verificamos que el título del formulario esté presente
        const title = screen.getByText(/Iniciar Sesión/i);
        expect(title).toBeInTheDocument();
    });
});

describe('Suite de pruebas para la funcionalidad de inicio de sesión', () => {
    it('Debe permitir al usuario ingresar sus credenciales y hacer clic en el botón de inicio de sesión', () => {
        //Creamos un mock para la función de inicio de sesión
        const onLoginMock = vi.fn();
        render(<Login onLogin={onLoginMock} />);

        //Simulamos escribir en los componentes de usuario y contraseña
        fireEvent.change(screen.getByPlaceholderText(/Usuario/i), {
            target: { value: 'usuario@utalca.cl' },
        });
        fireEvent.change(screen.getByPlaceholderText(/Contraseña/i), {
            target: { value: 'usuario' },
        });
        fireEvent.click(screen.getByText(/Acceder/i));

        expect(onLoginMock).toHaveBeenCalled();
    });
});
