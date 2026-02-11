interface AgentStatusBadgeProps {
  status: "ready" | "running" | "error" | "idle";
}

const STATUS_MAP = {
  ready: { label: "Ready", cls: "badge-green" },
  running: { label: "Running", cls: "badge-blue" },
  error: { label: "Error", cls: "badge-red" },
  idle: { label: "Idle", cls: "badge-amber" },
};

export function AgentStatusBadge({ status }: AgentStatusBadgeProps) {
  const s = STATUS_MAP[status] || STATUS_MAP.idle;
  return (
    <span className={s.cls}>
      <span className={`status-dot ${status === "running" ? "active" : status === "error" ? "error" : "idle"}`} />
      {s.label}
    </span>
  );
}
