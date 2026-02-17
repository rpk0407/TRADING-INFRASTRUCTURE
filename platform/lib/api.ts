const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function apiFetch<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...options?.headers },
    ...options,
  });
  if (!res.ok) throw new Error(`API ${res.status}: ${await res.text()}`);
  return res.json();
}

/** Safe fetch that returns null on error instead of throwing */
async function safeFetch<T>(path: string, options?: RequestInit): Promise<T | null> {
  try {
    return await apiFetch<T>(path, options);
  } catch {
    return null;
  }
}

export const api = {
  // Health
  health: () => apiFetch<any>("/health"),
  healthDetailed: () => apiFetch<any>("/health/detailed"),
  systemHealth: () => safeFetch<any>("/api/v1/lifecycle/system/health"),

  // Workflows
  createWorkflow: (data: any) =>
    apiFetch<any>("/api/v1/workflows/", { method: "POST", body: JSON.stringify(data) }),
  getWorkflow: (id: string) => apiFetch<any>(`/api/v1/workflows/${id}`),
  listWorkflows: (clientId?: string) =>
    safeFetch<any>(`/api/v1/workflows${clientId ? `?client_id=${clientId}` : ""}`),
  getTemplates: () => apiFetch<any>("/api/v1/workflows/templates/all"),

  // Agents
  listAgents: () => safeFetch<any>("/api/v1/agents/"),
  getAgent: (id: string) => apiFetch<any>(`/api/v1/agents/${id}`),
  getAgentStats: (id: string) => apiFetch<any>(`/api/v1/agents/${id}/stats`),

  // Clients
  getClientDashboard: (id: string) => apiFetch<any>(`/api/v1/clients/${id}/dashboard`),
  updateClientProfile: (id: string, data: any) =>
    apiFetch<any>(`/api/v1/clients/${id}/profile`, { method: "PUT", body: JSON.stringify(data) }),
  getClientWorkflows: (id: string) => apiFetch<any>(`/api/v1/clients/${id}/workflows`),

  // Analytics
  getLLMUsage: () => safeFetch<any>("/api/v1/analytics/llm-usage"),
  getPlatformStats: () => safeFetch<any>("/api/v1/analytics/platform-stats"),
  getCostBreakdown: () => apiFetch<any>("/api/v1/analytics/cost-breakdown"),

  // Lifecycle
  onboardClient: (data: any) =>
    apiFetch<any>("/api/v1/lifecycle/onboard", { method: "POST", body: JSON.stringify(data) }),
  advancePhase: (clientId: string) =>
    apiFetch<any>(`/api/v1/lifecycle/${clientId}/advance`, { method: "POST" }),
  clientHealth: (clientId: string) => apiFetch<any>(`/api/v1/lifecycle/${clientId}/health`),
  clientProgress: (clientId: string) => apiFetch<any>(`/api/v1/lifecycle/${clientId}/progress`),
  lifecycleClients: () => safeFetch<any>("/api/v1/lifecycle/"),
  lifecycleTemplates: () => safeFetch<any>("/api/v1/lifecycle/templates"),

  // WebSocket
  connectWorkflow: (workflowId: string): WebSocket => {
    const wsBase = API_BASE.replace("http", "ws");
    return new WebSocket(`${wsBase}/ws/${workflowId}`);
  },
};
