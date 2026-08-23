/**
 * src/context/AuthContext.jsx
 *
 * Centralized authentication state manager.
 * - Stores current user + role + auth state
 * - Persists token in localStorage for session restoration
 * - Handles token expiry → clears state and redirects to login
 * - Provides login/logout/register helpers consumed by all components
 */

import { createContext, useContext, useState, useEffect, useCallback } from "react";
import { authApi } from "../api/auth.js";

const AuthContext = createContext(null);

const TOKEN_KEY = "scda_auth_token";
const USER_KEY = "scda_auth_user";

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(() => localStorage.getItem(TOKEN_KEY));
  const [loading, setLoading] = useState(true); // true while restoring session
  const [authError, setAuthError] = useState(null);

  /** Persist auth state to localStorage */
  const persistAuth = useCallback((accessToken, userObj) => {
    localStorage.setItem(TOKEN_KEY, accessToken);
    localStorage.setItem(USER_KEY, JSON.stringify(userObj));
    setToken(accessToken);
    setUser(userObj);
  }, []);

  /** Clear all auth state */
  const clearAuth = useCallback(() => {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
    setToken(null);
    setUser(null);
  }, []);

  /** Restore session on mount / page refresh */
  useEffect(() => {
    async function restoreSession() {
      const storedToken = localStorage.getItem(TOKEN_KEY);
      if (!storedToken) {
        setLoading(false);
        return;
      }

      try {
        // Validate token against backend — if expired/invalid, /auth/me returns 401
        const userData = await authApi.me(storedToken);
        setUser(userData);
        setToken(storedToken);
      } catch {
        // Token invalid or expired — clear stored state
        clearAuth();
      } finally {
        setLoading(false);
      }
    }
    restoreSession();
  }, [clearAuth]);

  /** Login and persist session */
  const login = useCallback(async (email, password) => {
    setAuthError(null);
    const data = await authApi.login(email, password);
    persistAuth(data.access_token, data.user);
    return data.user;
  }, [persistAuth]);

  /** Register and persist session */
  const register = useCallback(async (payload) => {
    setAuthError(null);
    const data = await authApi.register(payload);
    persistAuth(data.access_token, data.user);
    return data.user;
  }, [persistAuth]);

  /** Logout — clear client state and notify server */
  const logout = useCallback(async () => {
    try {
      if (token) await authApi.logout(token);
    } catch {
      // Ignore logout errors — still clear client state
    } finally {
      clearAuth();
    }
  }, [token, clearAuth]);

  /** Called by API client when a 401 is received mid-session */
  const handleUnauthorized = useCallback(() => {
    clearAuth();
  }, [clearAuth]);

  const value = {
    user,
    token,
    loading,
    authError,
    setAuthError,
    isAuthenticated: !!user,
    isAdmin: user?.role === "admin",
    isSupplier: user?.role === "supplier",
    isUser: user?.role === "user",
    login,
    logout,
    register,
    handleUnauthorized,
    persistAuth,
    clearAuth,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
