/**
 * src/api/suppliers.js
 * Owner: Developer 4 (Frontend)
 * Backend contract: app/api/routes_suppliers.py (Dev2)
 */
import { apiRequest } from "./client.js";

export const listSuppliers = () => apiRequest("/suppliers/");
export const getSupplier = (id) => apiRequest(`/suppliers/${id}`);
