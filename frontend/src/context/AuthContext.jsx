import {
    createContext,
    useContext,
    useState,
    useEffect,
    useCallback,
} from 'react';
import { apiGet, apiPost } from '../api/client';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
    const [currentUser, setCurrentUser] = useState(null);
    const [isLoading, setIsLoading] = useState(true);

    const logout = useCallback(() => {
        localStorage.removeItem('token');
        setCurrentUser(null);
    }, []);

    const fetchMe = useCallback(async () => {
        try {
            const user = await apiGet('auth/me');
            setCurrentUser(user);
        } catch {
            logout();
        }
    }, [logout]);

    useEffect(() => {
        const token = localStorage.getItem('token');
        if (token) {
            fetchMe().finally(() => setIsLoading(false));
        } else {
            setIsLoading(false);
        }
    }, [fetchMe]);

    const login = async (email, password) => {
        const data = await apiPost('auth/token', { email, password });
        localStorage.setItem('token', data.access_token);
        await fetchMe();
        return data;
    };

    const isAuthenticated = !!currentUser;

    return (
        <AuthContext.Provider
            value={{
                currentUser,
                isAuthenticated,
                isLoading,
                login,
                logout,
            }}
        >
            {children}
        </AuthContext.Provider>
    );
}

export function useAuth() {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error('useAuth must be used within AuthProvider');
    }
    return context;
}
