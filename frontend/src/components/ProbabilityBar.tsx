import type { SentimentLabel } from "../types/prediction";
import { formatPercent, sentimentMeta } from "../utils/presentation";

interface ProbabilityBarProps {
  label: SentimentLabel;
  value: number;
}

export function ProbabilityBar({ label, value }: ProbabilityBarProps) {
  const meta = sentimentMeta[label];
  return (
    <div className="probability-row">
      <span className="probability-label">
        <span
          aria-hidden="true"
          className="probability-dot"
          style={{ backgroundColor: meta.color }}
        />
        {meta.label}
      </span>
      <span className="probability-track" aria-hidden="true">
        <span
          className="probability-fill"
          style={{
            backgroundColor: meta.color,
            width: `${Math.max(value * 100, 1)}%`,
          }}
        />
      </span>
      <span className="probability-value">{formatPercent(value)}</span>
      <span className="sr-only">
        {meta.label} {formatPercent(value)}
      </span>
    </div>
  );
}
