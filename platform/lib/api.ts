const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function apiFetch<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...options?.headers },
    ...options,
  });
  if (!res.ok) throw new Error(`API ${res.status}: ${await res.text()}`);
  return res.json();
}

export const api = {
  health: () => apiFetch<any>("/health"),
  healthDetailed: () => apiFetch<any>("/health/detailed"),
  createWorkflow: (data: any) =>
    apiFetch<any>("/api/v1/workflows/", { method: "POST", body: JSON.stringify(data) }),
  getWorkflow: (id: string) => apiFetch<any>(`/api/v1/workflows/${id}`),
  listWorkflows: (clientId?: string) =>
    apiFetch<any>(`/api/v1/workflows/${clientId ? `?client_id=${clientId}` : ""}`),
  getTemplates: () => apiFetch<any>("/api/v1/workflows/templates/all"),
  listAgents: () => apiFetch<any>("/api/v1/agents/"),
  getAgent: (id: string) => apiFetch<any>(`/api/v1/agents/${id}`),
  getAgentStats: (id: string) => apiFetch<any>(`/api/v1/agents/${id}/stats`),
  getClientDashboard: (id: string) => apiFetch<any>(`/api/v1/clients/${id}/dashboard`),
  updateClientProfile: (id: string, data: any) =>
    apiFetch<any>(`/api/v1/clients/${id}/profile`, { method: "PUT", body: JSON.stringify(data) }),
  getClientWorkflows: (id: string) => apiFetch<any>(`/api/v1/clients/${id}/workflows`),
  getLLMUsage: () => apiFetch<any>("/api/v1/analytics/llm-usage"),
  getPlatformStats: () => apiFetch<any>("/api/v1/analytics/platform-stats"),
  getCostBreakdown: () => apiFetch<any>("/api/v1/analytics/cost-breakdown"),
};
