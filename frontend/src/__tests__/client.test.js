import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { apiGet, apiPost } from '../api/client';

function mockHeaders(contentType) {
    return {
        get: (key) => (key === 'content-type' ? contentType : null),
    };
}

describe('client.js', () => {
    beforeEach(() => {
        vi.stubGlobal('fetch', vi.fn());
        localStorage.clear();
    });

    afterEach(() => {
        vi.unstubAllGlobals();
    });

    it('authenticated request includes Bearer header', async () => {
        localStorage.setItem('token', 'abc123');
        fetch.mockResolvedValue({
            ok: true,
            headers: mockHeaders('application/json'),
            json: async () => ({ message: 'ok' }),
        });

        await apiGet('auth/me');
        expect(fetch).toHaveBeenCalledWith('/api/auth/me', {
            headers: { Authorization: 'Bearer abc123' },
        });
    });

    it('no token = no Authorization header', async () => {
        fetch.mockResolvedValue({
            ok: true,
            headers: mockHeaders('application/json'),
            json: async () => ({ message: 'ok' }),
        });

        await apiGet('health');
        expect(fetch).toHaveBeenCalledWith('/api/health', {
            headers: {},
        });
    });

    it('non-JSON response returned as-is', async () => {
        fetch.mockResolvedValue({
            ok: true,
            headers: mockHeaders('text/plain'),
            text: async () => 'pong',
        });

        const result = await apiGet('health');
        expect(result).toBe('pong');
    });

    it('network error thrown', async () => {
        fetch.mockRejectedValue(new Error('Network error'));
        await expect(apiGet('auth/me')).rejects.toThrow('Network error');
    });

    it('HTTP error throws with detail message', async () => {
        fetch.mockResolvedValue({
            ok: false,
            status: 401,
            headers: mockHeaders('application/json'),
            json: async () => ({ detail: 'Credenciales inválidas' }),
        });

        await expect(
            apiPost('auth/token', { email: 'x', password: 'y' })
        ).rejects.toThrow('Credenciales inválidas');
    });

    it('apiPost sends JSON body with Content-Type header', async () => {
        localStorage.setItem('token', 'tok456');
        fetch.mockResolvedValue({
            ok: true,
            headers: mockHeaders('application/json'),
            json: async () => ({ access_token: 'newtok' }),
        });

        await apiPost('auth/token', { email: 'a@b.cl', password: 'pw' });
        expect(fetch).toHaveBeenCalledWith('/api/auth/token', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                Authorization: 'Bearer tok456',
            },
            body: JSON.stringify({ email: 'a@b.cl', password: 'pw' }),
        });
    });
});
