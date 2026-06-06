import Papa from "papaparse";

import {
  sentimentLabels,
  type DashboardSummary,
  type PredictionResult,
  type ReviewInputRow,
  type Topic,
} from "../types/prediction";

type CsvRecord = Record<string, string | undefined>;

export function parseReviewCsv(
  csv: string,
  maxRows = 100,
): ReviewInputRow[] {
  const parsed = Papa.parse<CsvRecord>(csv, {
    header: true,
    skipEmptyLines: "greedy",
    transformHeader: (header) => header.trim(),
  });

  const fatalError = parsed.errors.find(
    (error) => error.code !== "UndetectableDelimiter",
  );
  if (fatalError) {
    throw new Error(`CSV could not be parsed: ${fatalError.message}`);
  }

  const fields = parsed.meta.fields ?? [];
  const textField = fields.find(
    (field) => field.trim().toLowerCase() === "text",
  );
  if (!textField) {
    throw new Error("CSV must contain a text column");
  }
  const idField = fields.find((field) => field.trim().toLowerCase() === "id");

  const rows = parsed.data.flatMap((record, index) => {
    const text = record[textField]?.trim() ?? "";
    if (!text) {
      return [];
    }
    const rawId = idField ? record[idField]?.trim() : "";
    return [{ id: rawId || String(index + 1), text }];
  });

  if (rows.length === 0) {
    throw new Error("CSV contains no review rows");
  }
  if (rows.length > maxRows) {
    throw new Error(`CSV exceeds the ${maxRows} review limit`);
  }
  return rows;
}

export function aggregatePredictions(
  results: PredictionResult[],
): DashboardSummary {
  const counts = Object.fromEntries(
    sentimentLabels.map((label) => [label, 0]),
  ) as DashboardSummary["counts"];
  const topicCounter = new Map<Topic, number>();

  for (const result of results) {
    counts[result.predicted_label] += 1;
    topicCounter.set(result.topic, (topicCounter.get(result.topic) ?? 0) + 1);
  }

  const confidenceTotal = results.reduce(
    (total, result) => total + result.confidence,
    0,
  );
  const averageConfidence =
    results.length === 0
      ? 0
      : Math.round((confidenceTotal / results.length) * 1_000_000) / 1_000_000;

  return {
    total: results.length,
    averageConfidence,
    counts,
    negativeReviews: results
      .filter((result) => result.predicted_label === "negative")
      .sort((left, right) => right.confidence - left.confidence),
    topicCounts: Array.from(topicCounter, ([topic, count]) => ({
      topic,
      count,
    })).sort(
      (left, right) =>
        right.count - left.count || left.topic.localeCompare(right.topic),
    ),
  };
}
