import React, { createContext, useState, useEffect, useContext } from 'react';
import { jwtDecode } from 'jwt-decode';
import api from '../services/api';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const initializeAuth = async () => {
            const accessToken = localStorage.getItem('access');
            if (accessToken) {
                try {
                    const decodedToken = jwtDecode(accessToken);
                    // Assuming token holds user_id. We fetch details to get role and other info.
                    const response = await api.get(`/users/${decodedToken.user_id}/`);
                    setUser(response.data);
                } catch (error) {
                    console.error("Auth initialization failed:", error);
                    localStorage.removeItem('access');
                    localStorage.removeItem('refresh');
                }
            }
            setLoading(false);
        };

        initializeAuth();
    }, []);

    const login = async (username, password) => {
        try {
            const response = await api.post('/auth/login/', { username, password });
            const { access, refresh } = response.data;

            localStorage.setItem('access', access);
            localStorage.setItem('refresh', refresh);

            const decodedToken = jwtDecode(access);
            const userResponse = await api.get(`/users/${decodedToken.user_id}/`);
            setUser(userResponse.data);
            return { success: true };
        } catch (error) {
            console.error("Login Error", error);
            return {
                success: false,
                message: error.response?.data?.detail || "Invalid credentials."
            };
        }
    };

    const logout = () => {
        localStorage.removeItem('access');
        localStorage.removeItem('refresh');
        setUser(null);
    };

    return (
        <AuthContext.Provider value={{ user, loading, login, logout }}>
            {!loading && children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => useContext(AuthContext);
