import React, { createContext, useContext, useState, useEffect, useCallback } from "react";
import AsyncStorage from "@react-native-async-storage/async-storage";
import {
  authAPI,
  clearTokens,
  setUnauthorizedHandler,
} from "../services/api";

export interface User {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  role: string;
  is_verified: boolean;
}

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (data: {
    first_name: string;
    last_name: string;
    email: string;
    password: string;
    password_confirm: string;
    role: string;
  }) => Promise<void>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;

    const loadUser = async () => {
      const token = await AsyncStorage.getItem("access_token");
      if (!token) {
        if (!cancelled) setLoading(false);
        return;
      }
      try {
        const res = await authAPI.getMe();
        if (!cancelled) setUser(res.data);
      } catch {
        // Stale or revoked token: drop it so the app shows the login flow.
        await clearTokens();
        if (!cancelled) setUser(null);
      } finally {
        if (!cancelled) setLoading(false);
      }
    };

    loadUser();
    return () => {
      cancelled = true;
    };
  }, []);

  // The API layer signs the user out when a refresh cannot be obtained.
  useEffect(() => {
    setUnauthorizedHandler(() => setUser(null));
    return () => setUnauthorizedHandler(null);
  }, []);

  const login = useCallback(async (email: string, password: string) => {
    const res = await authAPI.login(email, password);
    const { access, refresh, user: userData } = res.data;
    await AsyncStorage.setItem("access_token", access);
    await AsyncStorage.setItem("refresh_token", refresh);
    setUser(userData);
  }, []);

  const register = useCallback(
    async (data: {
      first_name: string;
      last_name: string;
      email: string;
      password: string;
      password_confirm: string;
      role: string;
    }) => {
      await authAPI.register(data);
    },
    []
  );

  const logout = useCallback(async () => {
    await clearTokens();
    setUser(null);
  }, []);

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};
