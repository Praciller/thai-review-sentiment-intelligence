import type { SentimentLabel, Topic } from "../types/prediction";

export const sentimentMeta: Record<
  SentimentLabel,
  { label: string; color: string; surface: string }
> = {
  positive: {
    label: "เชิงบวก",
    color: "#2E7D32",
    surface: "#EDF7ED",
  },
  negative: {
    label: "เชิงลบ",
    color: "#C0392B",
    surface: "#FCEFED",
  },
  neutral: {
    label: "เป็นกลาง",
    color: "#607086",
    surface: "#EFF2F5",
  },
  question: {
    label: "คำถาม",
    color: "#355C8A",
    surface: "#EDF3FA",
  },
};

export const topicLabels: Record<Topic, string> = {
  taste: "รสชาติ",
  price: "ราคา",
  service: "บริการ",
  delivery: "การจัดส่ง",
  cleanliness: "ความสะอาด",
  waiting_time: "เวลารอ",
  product_quality: "คุณภาพสินค้า",
  other: "อื่น ๆ",
};

export function formatPercent(value: number): string {
  return new Intl.NumberFormat("th-TH", {
    style: "percent",
    maximumFractionDigits: 0,
  }).format(value);
}
