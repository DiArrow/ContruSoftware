const BASE_URL = '/api/';

function getToken() {
    return localStorage.getItem('token');
}

function buildHeaders(extra = {}) {
    const headers = { ...extra };
    const token = getToken();
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }
    return headers;
}

async function parseResponse(response) {
    const contentType = response.headers.get('content-type');
    if (contentType && contentType.includes('application/json')) {
        return response.json();
    }
    return response.text();
}

export async function apiGet(path) {
    const response = await fetch(`${BASE_URL}${path}`, {
        headers: buildHeaders(),
    });
    const data = await parseResponse(response);
    if (!response.ok) {
        throw new Error(
            data.detail || data.message || data || 'Request failed'
        );
    }
    return data;
}

export async function apiPost(path, body) {
    const response = await fetch(`${BASE_URL}${path}`, {
        method: 'POST',
        headers: buildHeaders({ 'Content-Type': 'application/json' }),
        body: JSON.stringify(body),
    });
    const data = await parseResponse(response);
    if (!response.ok) {
        throw new Error(
            data.detail || data.message || data || 'Request failed'
        );
    }
    return data;
}
