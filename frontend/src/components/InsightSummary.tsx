import { ArrowUpRight, Lightbulb } from "lucide-react";

import type { DashboardSummary } from "../types/prediction";
import { topicLabels } from "../utils/presentation";

export function InsightSummary({
  summary,
}: {
  summary: DashboardSummary;
}) {
  const leadingTopics = summary.topicCounts.slice(0, 3);
  const negativeShare =
    summary.total === 0 ? 0 : summary.counts.negative / summary.total;
  return (
    <section className="insight-summary">
      <div className="insight-heading">
        <Lightbulb aria-hidden="true" size={22} />
        <div>
          <p className="section-kicker">Business insight</p>
          <h2>ประเด็นที่ควรติดตาม</h2>
        </div>
      </div>
      <p className="insight-lead">
        {negativeShare >= 0.3
          ? "สัดส่วนรีวิวเชิงลบอยู่ในระดับที่ควรตรวจสอบเชิงปฏิบัติการ"
          : "ภาพรวมยังไม่พบสัญญาณเชิงลบสูง แต่ควรติดตามหัวข้อหลักต่อเนื่อง"}
      </p>
      <ol className="topic-ranking">
        {leadingTopics.map((item) => (
          <li key={item.topic}>
            <span>{topicLabels[item.topic]}</span>
            <strong>{item.count.toLocaleString("th-TH")}</strong>
          </li>
        ))}
      </ol>
      <p className="method-note">
        <ArrowUpRight aria-hidden="true" size={16} />
        หัวข้อเป็นการจัดกลุ่มแบบ rule-based ไม่ใช่โมเดล ML
      </p>
    </section>
  );
}
