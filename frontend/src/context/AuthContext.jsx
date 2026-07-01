import {
    createContext,
    useContext,
    useState,
    useEffect,
    useCallback,
} from 'react';
import { apiGet, apiPost } from '../api/client';

export const AuthContext = createContext(null);

export function AuthProvider({ children }) {
    const [currentUser, setCurrentUser] = useState(null);
    const [isLoading, setIsLoading] = useState(true);

    const logout = useCallback(() => {
        localStorage.removeItem('token');
        setCurrentUser(null);
    }, []);

    const fetchMe = useCallback(async () => {
        try {
            // Nuevo path del endpoint de perfil tras el refactor de routers
            const user = await apiGet('auth/me');
            setCurrentUser(user);
        } catch {
            logout();
        }
    }, [logout]);

    useEffect(() => {
        let isMounted = true;

        const initializeAuth = async () => {
            const token = localStorage.getItem('token');
            if (token) {
                try {
                    await fetchMe();
                } catch {
                    // El manejo de errores se desarrollan internamente
                } finally {
                    if (isMounted) setIsLoading(false);
                }
            } else {
                if (isMounted) setIsLoading(false);
            }
        };

        initializeAuth();

        return () => {
            isMounted = false;
        };
    }, [fetchMe]);

    const login = async (email, password) => {
        // Nuevo path del endpoint de login tras el refactor de routers
        const data = await apiPost('auth/token', {
            email,
            password,
        });
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

// eslint-disable-next-line react-refresh/only-export-components
export function useAuth() {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error('useAuth must be used within AuthProvider');
    }
    return context;
}
