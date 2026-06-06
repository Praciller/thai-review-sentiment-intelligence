import { describe, expect, it } from "vitest";

import type { PredictionResult } from "../types/prediction";
import { aggregatePredictions, parseReviewCsv } from "./reviewData";
import { sampleReviewRows } from "./sampleData";

describe("sampleReviewRows", () => {
  it("provides a valid batch fixture within the API limit", () => {
    expect(sampleReviewRows).toHaveLength(8);
    expect(new Set(sampleReviewRows.map((row) => row.id)).size).toBe(8);
    expect(sampleReviewRows.every((row) => row.text.trim().length > 0)).toBe(
      true,
    );
  });
});

describe("parseReviewCsv", () => {
  it("parses quoted Thai text and preserves row order", () => {
    const csv = [
      "id,text",
      'a1,"อาหารอร่อย, บริการดี"',
      'a2,"รอนานเกินไป"',
    ].join("\n");

    expect(parseReviewCsv(csv)).toEqual([
      { id: "a1", text: "อาหารอร่อย, บริการดี" },
      { id: "a2", text: "รอนานเกินไป" },
    ]);
  });

  it("rejects files without a text column", () => {
    expect(() => parseReviewCsv("id,review\n1,ดีมาก")).toThrow(
      "CSV must contain a text column",
    );
  });

  it("rejects empty review rows and row counts above the limit", () => {
    expect(() => parseReviewCsv("text\n   ")).toThrow(
      "CSV contains no review rows",
    );
    expect(() => parseReviewCsv("text\nหนึ่ง\nสอง", 1)).toThrow(
      "CSV exceeds the 1 review limit",
    );
  });
});

describe("aggregatePredictions", () => {
  it("computes sentiment counts, confidence, negative rows, and topics", () => {
    const results: PredictionResult[] = [
      {
        text: "ดีมาก",
        predicted_label: "positive",
        confidence: 0.9,
        probabilities: {
          positive: 0.9,
          negative: 0.03,
          neutral: 0.04,
          question: 0.03,
        },
        model_name: "test",
        topic: "service",
        topic_method: "rule_based",
      },
      {
        text: "รอนาน",
        predicted_label: "negative",
        confidence: 0.7,
        probabilities: {
          positive: 0.05,
          negative: 0.7,
          neutral: 0.2,
          question: 0.05,
        },
        model_name: "test",
        topic: "waiting_time",
        topic_method: "rule_based",
      },
      {
        text: "ส่งช้า",
        predicted_label: "negative",
        confidence: 0.8,
        probabilities: {
          positive: 0.05,
          negative: 0.8,
          neutral: 0.1,
          question: 0.05,
        },
        model_name: "test",
        topic: "delivery",
        topic_method: "rule_based",
      },
    ];

    expect(aggregatePredictions(results)).toEqual({
      total: 3,
      averageConfidence: 0.8,
      counts: {
        positive: 1,
        negative: 2,
        neutral: 0,
        question: 0,
      },
      negativeReviews: [results[2], results[1]],
      topicCounts: [
        { topic: "delivery", count: 1 },
        { topic: "service", count: 1 },
        { topic: "waiting_time", count: 1 },
      ],
    });
  });
});
