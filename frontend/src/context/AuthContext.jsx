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
  // Initialize user synchronously from localStorage so ProtectedRoute
  // sees the correct value immediately after navigate() on login — before
  // React's async setUser state update would otherwise commit.
  const [user, setUser] = useState(() => {
    try {
      const stored = localStorage.getItem(USER_KEY);
      return stored ? JSON.parse(stored) : null;
    } catch {
      return null;
    }
  });
  const [token, setToken] = useState(() => localStorage.getItem(TOKEN_KEY));
  const [loading, setLoading] = useState(true); // true while validating token with backend
  const [authError, setAuthError] = useState(null);

  /** Persist auth state to localStorage and context synchronously */
  const persistAuth = useCallback((accessToken, userObj) => {
    localStorage.setItem(TOKEN_KEY, accessToken);
    localStorage.setItem(USER_KEY, JSON.stringify(userObj));
    setToken(accessToken);
    setUser(userObj);
    setLoading(false);
  }, []);

  /** Clear all auth state */
  const clearAuth = useCallback(() => {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
    setToken(null);
    setUser(null);
    setLoading(false);
  }, []);

  /** Restore session on mount / page refresh */
  useEffect(() => {
    let isMounted = true;

    async function restoreSession() {
      const storedToken = localStorage.getItem(TOKEN_KEY);
      if (!storedToken) {
        if (isMounted) setLoading(false);
        return;
      }

      try {
        // Validate token against backend
        const userData = await authApi.me(storedToken);
        if (isMounted) {
          setUser(userData);
          setToken(storedToken);
        }
      } catch (err) {
        // Only clear credentials if server explicitly returned 401 or 403
        if (err.status === 401 || err.status === 403) {
          if (isMounted) clearAuth();
        }
      } finally {
        if (isMounted) setLoading(false);
      }
    }
    restoreSession();

    return () => {
      isMounted = false;
    };
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
