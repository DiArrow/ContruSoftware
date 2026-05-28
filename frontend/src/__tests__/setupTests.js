import '@testing-library/jest-dom';
import { vi } from 'vitest';

let store = {};

const localStorageMock = {
    getItem: vi.fn((key) => store[key] || null),
    setItem: vi.fn((key, value) => {
        store[key] = String(value);
    }),
    removeItem: vi.fn((key) => {
        delete store[key];
    }),
    clear: vi.fn(() => {
        store = {};
    }),
};

Object.defineProperty(window, 'localStorage', {
    value: localStorageMock,
    writable: true,
});
