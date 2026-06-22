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
  selected_production_model?: string;
  topic: Topic;
  topic_method: "rule_based";
  route?: "auto_label" | "human_review" | "support_workflow" | "escalation_queue";
  requires_human_review?: boolean;
  reason_codes?: string[];
  confidence_threshold?: number;
  evidence_terms?: string[];
  topic_terms?: string[];
  explanation_mode?: "tfidf_weights" | "keyword_demo";
  selection_metric?: string;
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
