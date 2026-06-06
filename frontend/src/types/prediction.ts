export const sentimentLabels = [
  "positive",
  "negative",
  "neutral",
  "question",
] as const;

export type SentimentLabel = (typeof sentimentLabels)[number];

export type Topic =
  | "taste"
  | "price"
  | "service"
  | "delivery"
  | "cleanliness"
  | "waiting_time"
  | "product_quality"
  | "other";

export interface PredictionResult {
  text: string;
  predicted_label: SentimentLabel;
  confidence: number;
  probabilities: Record<SentimentLabel, number>;
  model_name: string;
  topic: Topic;
  topic_method: "rule_based";
}

export interface BatchPredictionResponse {
  results: PredictionResult[];
}

export interface ReviewInputRow {
  id: string;
  text: string;
}

export interface DashboardSummary {
  total: number;
  averageConfidence: number;
  counts: Record<SentimentLabel, number>;
  negativeReviews: PredictionResult[];
  topicCounts: Array<{ topic: Topic; count: number }>;
}
