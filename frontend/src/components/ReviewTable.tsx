import type {
  PredictionResult,
  SentimentLabel,
} from "../types/prediction";
import { formatPercent, sentimentMeta, topicLabels } from "../utils/presentation";

interface ReviewTableProps {
  results: PredictionResult[];
  emptyMessage?: string;
}

export function ReviewTable({
  results,
  emptyMessage = "ยังไม่มีผลการวิเคราะห์",
}: ReviewTableProps) {
  if (results.length === 0) {
    return <p className="empty-inline">{emptyMessage}</p>;
  }

  return (
    <div className="table-scroll">
      <table className="review-table">
        <thead>
          <tr>
            <th>รีวิว</th>
            <th>ความรู้สึก</th>
            <th>ความมั่นใจ</th>
            <th>หัวข้อ</th>
          </tr>
        </thead>
        <tbody>
          {results.map((result, index) => (
            <ReviewRow key={`${result.text}-${index}`} result={result} />
          ))}
        </tbody>
      </table>
    </div>
  );
}

function ReviewRow({ result }: { result: PredictionResult }) {
  return (
    <tr>
      <td data-label="รีวิว">{result.text}</td>
      <td data-label="ความรู้สึก">
        <SentimentBadge label={result.predicted_label} />
      </td>
      <td data-label="ความมั่นใจ">{formatPercent(result.confidence)}</td>
      <td data-label="หัวข้อ">{topicLabels[result.topic]}</td>
    </tr>
  );
}

function SentimentBadge({ label }: { label: SentimentLabel }) {
  const meta = sentimentMeta[label];
  return (
    <span
      className="sentiment-badge"
      style={{ color: meta.color, backgroundColor: meta.surface }}
    >
      <span
        aria-hidden="true"
        className="probability-dot"
        style={{ backgroundColor: meta.color }}
      />
      {meta.label}
    </span>
  );
}
