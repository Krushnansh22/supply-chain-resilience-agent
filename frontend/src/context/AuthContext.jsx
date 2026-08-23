/**
 * src/context/AuthContext.jsx
 * Role-Based Access Control, Authentication, and Multi-Warehouse State
 */
import React, { createContext, useContext, useState, useEffect, useCallback } from "react";
import { loginUser, registerUser, fetchDemoUsers, fetchCurrentUser } from "../api/auth.js";
import { apiRequest } from "../api/client.js";

const AuthContext = createContext(null);

const DEFAULT_ADMIN = {
  user_id: "USR-ADMIN",
  name: "Alex Whitfield",
  email: "alex.whitfield@atlas-scm.io",
  role: "ADMIN",
  title: "Global Supply Chain Director",
  assigned_warehouse: "ALL",
};

const DEFAULT_WAREHOUSES = [
  { warehouse_id: "Warehouse-A", name: "Warehouse-A (Main Assembly)", region: "North America" },
  { warehouse_id: "Warehouse-B", name: "Warehouse-B (Sub-Assembly Depot)", region: "Central Hub" },
  { warehouse_id: "Warehouse-C", name: "Warehouse-C (Silicon Logistics)", region: "Asia-Pacific" },
  { warehouse_id: "Warehouse-D", name: "Warehouse-D (Packaging & Distribution)", region: "Europe Gateway" },
];

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem("scda_auth_token"));
  const [currentUser, setCurrentUser] = useState(() => {
    const saved = localStorage.getItem("scda_active_user");
    return saved ? JSON.parse(saved) : DEFAULT_ADMIN;
  });

  const [activeWarehouse, setActiveWarehouseState] = useState(() => {
    const saved = localStorage.getItem("scda_active_warehouse");
    return saved || (currentUser?.role === "ADMIN" ? "ALL" : currentUser?.assigned_warehouse || "Warehouse-A");
  });

  const [usersList, setUsersList] = useState([DEFAULT_ADMIN]);
  const [warehousesList, setWarehousesList] = useState(DEFAULT_WAREHOUSES);
  const [loading, setLoading] = useState(false);

  // Sync users and warehouses list
  useEffect(() => {
    fetchDemoUsers()
      .then((users) => {
        if (users && users.length > 0) setUsersList(users);
      })
      .catch(() => null);

    apiRequest("/users/warehouses/all")
      .then((warehouses) => {
        if (warehouses && warehouses.length > 0) setWarehousesList(warehouses);
      })
      .catch(() => null);
  }, []);

  const login = async (email, password) => {
    setLoading(true);
    try {
      const res = await loginUser({ email, password });
      if (res.access_token) {
        localStorage.setItem("scda_auth_token", res.access_token);
        setToken(res.access_token);
      }
      if (res.user) {
        setCurrentUser(res.user);
        localStorage.setItem("scda_active_user", JSON.stringify(res.user));
        const targetWh = res.user.role === "ADMIN" ? "ALL" : (res.user.assigned_warehouse || "Warehouse-A");
        setActiveWarehouseState(targetWh);
        localStorage.setItem("scda_active_warehouse", targetWh);
      }
      return res;
    } finally {
      setLoading(false);
    }
  };

  const signup = async (formData) => {
    setLoading(true);
    try {
      const res = await registerUser(formData);
      if (res.access_token) {
        localStorage.setItem("scda_auth_token", res.access_token);
        setToken(res.access_token);
      }
      if (res.user) {
        setCurrentUser(res.user);
        localStorage.setItem("scda_active_user", JSON.stringify(res.user));
        const targetWh = res.user.role === "ADMIN" ? "ALL" : (res.user.assigned_warehouse || "Warehouse-A");
        setActiveWarehouseState(targetWh);
        localStorage.setItem("scda_active_warehouse", targetWh);
      }
      return res;
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    localStorage.removeItem("scda_auth_token");
    localStorage.removeItem("scda_active_user");
    localStorage.removeItem("scda_active_warehouse");
    localStorage.removeItem("scda_user_id");
    localStorage.removeItem("scda_warehouse_id");
    setToken(null);
    setCurrentUser(null);
    setActiveWarehouseState("ALL");
  };

  const quickLogin = useCallback((user) => {
    setCurrentUser(user);
    localStorage.setItem("scda_active_user", JSON.stringify(user));
    const targetWh = user.role === "ADMIN" ? "ALL" : (user.assigned_warehouse || "Warehouse-A");
    setActiveWarehouseState(targetWh);
    localStorage.setItem("scda_active_warehouse", targetWh);
  }, []);

  const switchUser = useCallback((userId) => {
    const selected = usersList.find((u) => u.user_id === userId) || DEFAULT_ADMIN;
    quickLogin(selected);
  }, [usersList, quickLogin]);

  const setWarehouse = useCallback((warehouseId) => {
    if (currentUser?.role === "ADMIN") {
      setActiveWarehouseState(warehouseId);
      localStorage.setItem("scda_active_warehouse", warehouseId);
    }
  }, [currentUser]);

  // Sync to request headers
  useEffect(() => {
    if (currentUser?.user_id) {
      localStorage.setItem("scda_user_id", currentUser.user_id);
    }
    if (activeWarehouse) {
      localStorage.setItem("scda_warehouse_id", activeWarehouse);
    }
  }, [currentUser, activeWarehouse]);

  const value = {
    isAuthenticated: !!currentUser,
    token,
    currentUser,
    user: currentUser,
    isAdmin: currentUser?.role === "ADMIN",
    isWarehouseManager: currentUser?.role === "WAREHOUSE_MANAGER",
    activeWarehouse,
    usersList,
    warehousesList,
    loading,
    login,
    signup,
    logout,
    quickLogin,
    switchUser,
    setWarehouse,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
