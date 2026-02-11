interface ProgressBarProps {
  value: number;
  max?: number;
  color?: string;
  label?: string;
  showPercent?: boolean;
}

export function ProgressBar({ value, max = 100, color = "#6366f1", label, showPercent = true }: ProgressBarProps) {
  const pct = Math.min((value / max) * 100, 100);
  return (
    <div className="w-full">
      {(label || showPercent) && (
        <div className="flex justify-between mb-1">
          {label && <span className="text-xs text-gray-400">{label}</span>}
          {showPercent && <span className="text-xs text-gray-500">{Math.round(pct)}%</span>}
        </div>
      )}
      <div className="h-1.5 bg-surface-3 rounded-full overflow-hidden">
        <div
          className="h-full rounded-full transition-all duration-500"
          style={{ width: `${pct}%`, backgroundColor: color }}
        />
      </div>
    </div>
  );
}
