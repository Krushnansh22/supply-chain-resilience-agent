import { apiRequest } from "./client.js";

export const getDiagnostics = () => apiRequest("/audit/diagnostics");
export const injectDiagnostics = (scenario) => apiRequest("/audit/diagnostics/inject", {
	method: "POST",
	body: JSON.stringify({ scenario }),
});