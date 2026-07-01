import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { apiPut } from '../client';

function mockHeaders(contentType) {
    return {
        get: (key) => (key === 'content-type' ? contentType : null),
    };
}

describe('apiPut', () => {
    beforeEach(() => {
        vi.stubGlobal('fetch', vi.fn());
        localStorage.clear();
    });

    afterEach(() => {
        vi.unstubAllGlobals();
    });

    it('sends PUT request with JSON body and auth header', async () => {
        localStorage.setItem('token', 'tok789');
        fetch.mockResolvedValue({
            ok: true,
            headers: mockHeaders('application/json'),
            json: async () => ({ updated: true }),
        });

        await apiPut('auth/me', { nombre: 'Carlos' });

        expect(fetch).toHaveBeenCalledWith('/api/auth/me', {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                Authorization: 'Bearer tok789',
            },
            body: JSON.stringify({ nombre: 'Carlos' }),
        });
    });

    it('returns parsed JSON response', async () => {
        localStorage.setItem('token', 'tok789');
        fetch.mockResolvedValue({
            ok: true,
            headers: mockHeaders('application/json'),
            json: async () => ({ id_usuario: '1', nombre: 'Carlos' }),
        });

        const result = await apiPut('auth/me', { nombre: 'Carlos' });

        expect(result).toEqual({ id_usuario: '1', nombre: 'Carlos' });
    });

    it('throws on HTTP error with detail message', async () => {
        fetch.mockResolvedValue({
            ok: false,
            status: 422,
            headers: mockHeaders('application/json'),
            json: async () => ({ detail: 'Validation error' }),
        });

        await expect(apiPut('auth/me', { email: 'bad' })).rejects.toThrow(
            'Validation error'
        );
    });
});
