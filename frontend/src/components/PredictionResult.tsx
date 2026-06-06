import {
  CircleHelp,
  CircleMinus,
  Frown,
  Smile,
} from "lucide-react";

import {
  sentimentLabels,
  type PredictionResult as PredictionResultType,
  type SentimentLabel,
} from "../types/prediction";
import { formatPercent, sentimentMeta } from "../utils/presentation";
import { ProbabilityBar } from "./ProbabilityBar";

const sentimentIcons: Record<SentimentLabel, typeof Smile> = {
  positive: Smile,
  negative: Frown,
  neutral: CircleMinus,
  question: CircleHelp,
};

export function PredictionResult({
  result,
}: {
  result: PredictionResultType | null;
}) {
  if (!result) {
    return (
      <section className="result-panel result-panel-empty" aria-live="polite">
        <CircleHelp aria-hidden="true" size={36} strokeWidth={1.6} />
        <div>
          <h2>ผลการวิเคราะห์</h2>
          <p>
            ผลลัพธ์ ความมั่นใจ และความน่าจะเป็นของแต่ละกลุ่มจะแสดงที่นี่
          </p>
        </div>
      </section>
    );
  }

  const meta = sentimentMeta[result.predicted_label];
  const Icon = sentimentIcons[result.predicted_label];
  return (
    <section className="result-panel" aria-live="polite">
      <div className="result-heading">
        <span
          className="sentiment-icon"
          style={{ color: meta.color, backgroundColor: meta.surface }}
        >
          <Icon aria-hidden="true" size={36} strokeWidth={1.8} />
        </span>
        <div>
          <p className="section-kicker">ผลการวิเคราะห์</p>
          <h2 style={{ color: meta.color }}>{meta.label}</h2>
          <p>
            ความมั่นใจ {formatPercent(result.confidence)}
            <span className="model-label"> · {result.model_name}</span>
          </p>
        </div>
      </div>
      <div className="divider" />
      <p className="probability-title">ความน่าจะเป็นของแต่ละความรู้สึก</p>
      <div className="probability-list">
        {sentimentLabels.map((label) => (
          <ProbabilityBar
            key={label}
            label={label}
            value={result.probabilities[label]}
          />
        ))}
      </div>
    </section>
  );
}
