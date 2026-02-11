import { type ReactNode } from "react";

interface StatCardProps {
  label: string;
  value: string | number;
  icon: ReactNode;
  trend?: { value: string; positive: boolean };
  color?: string;
}

export function StatCard({ label, value, icon, trend, color }: StatCardProps) {
  return (
    <div className="card-hover group">
      <div className="flex items-start justify-between mb-3">
        <div
          className="w-10 h-10 rounded-lg flex items-center justify-center"
          style={{ backgroundColor: `${color || "#6366f1"}15` }}
        >
          <span style={{ color: color || "#6366f1" }}>{icon}</span>
        </div>
        {trend && (
          <span
            className={`text-xs font-medium px-2 py-0.5 rounded-full ${
              trend.positive
                ? "bg-emerald-500/15 text-emerald-400"
                : "bg-red-500/15 text-red-400"
            }`}
          >
            {trend.positive ? "+" : ""}{trend.value}
          </span>
        )}
      </div>
      <p className="stat-value">{value}</p>
      <p className="stat-label mt-1">{label}</p>
    </div>
  );
}
