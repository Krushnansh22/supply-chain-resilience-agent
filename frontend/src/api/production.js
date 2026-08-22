/**
 * src/api/production.js
 * Owner: Developer 4 (Frontend)
 * Backend contract: app/api/routes_production.py (Dev2)
 */
import { apiRequest } from "./client.js";

export const listProductionOrders = () => apiRequest("/production/");
export const getProductionOrder = (id) => apiRequest(`/production/${id}`);
