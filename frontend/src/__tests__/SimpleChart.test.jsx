import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import SimpleChart from '../components/SimpleChart';

describe('SimpleChart Component', () => {
    it('renders structural titles and labels correctly', () => {
        render(<SimpleChart />);

        // 2. Verificar las etiquetas de estado del proyecto en la parte inferior
        expect(
            screen.getByText('PROYECTO: CONSTRUCCIÓN DE SOFTWARE')
        ).toBeInTheDocument();
        expect(screen.getByText('Meta')).toBeInTheDocument();
    });

    it('renders all ticks on the X and Y axes correctly', () => {
        render(<SimpleChart />);

        // El set de números esperado en los ejes es del 0 al 25 de 5 en 5
        const expectedTicks = ['0', '5', '10', '15', '20', '25'];

        expectedTicks.forEach((tick) => {
            // Buscamos que cada número aparezca en el documento
            // Usamos getAllByText ya que algunos números se repiten en el eje X y en el eje Y
            const tickElements = screen.getAllByText(tick);
            expect(tickElements.length).toBeGreaterThanOrEqual(1);
        });
    });

    it('calculates and applies the mathematically correct width for the progress bar', () => {
        const { container } = render(<SimpleChart />);

        // Buscamos el elemento div que contiene el degradado lineal continuo
        const divs = container.querySelectorAll('div');

        // Buscamos la barra filtrando por la propiedad CSS background que inyectamos
        const progressBar = Array.from(divs).find((div) =>
            div.style.background.includes('linear-gradient')
        );

        expect(progressBar).toBeInTheDocument();

        // Como el valorActual es 20 y metaMax es 25, (20/25)*100 = 80
        // Verificamos que el motor de estilos aplique exactamente el "80%" de ancho
        expect(progressBar.style.width).toBe('80%');
        expect(progressBar.style.height).toBe('190px');
    });
});
