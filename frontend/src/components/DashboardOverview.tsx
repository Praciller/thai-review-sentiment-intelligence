import { Clock3, Gauge, MessageSquareText, TriangleAlert } from "lucide-react";

import type { DashboardSummary } from "../types/prediction";
import { formatPercent } from "../utils/presentation";
import { InsightSummary } from "./InsightSummary";
import { ReviewTable } from "./ReviewTable";
import { SentimentChart } from "./SentimentChart";

export function DashboardOverview({
  summary,
  compact = false,
}: {
  summary: DashboardSummary;
  compact?: boolean;
}) {
  return (
    <section className={compact ? "dashboard-overview compact" : "dashboard-overview"}>
      <div className="section-heading-row">
        <div>
          <p className="section-kicker">ภาพรวมความคิดเห็น</p>
          <h2>สัญญาณจากเสียงลูกค้า</h2>
        </div>
        <p>อัปเดตจากผลวิเคราะห์ล่าสุดในเบราว์เซอร์</p>
      </div>
      <div className="analytics-grid">
        <SentimentChart counts={summary.counts} />
        <div className="analytics-detail">
          <div className="metric-strip">
            <Metric
              icon={MessageSquareText}
              label="รีวิวทั้งหมด"
              value={summary.total.toLocaleString("th-TH")}
            />
            <Metric
              icon={Gauge}
              label="ความมั่นใจเฉลี่ย"
              value={formatPercent(summary.averageConfidence)}
            />
            <Metric
              icon={TriangleAlert}
              label="รีวิวเชิงลบ"
              value={summary.counts.negative.toLocaleString("th-TH")}
            />
            <Metric
              icon={Clock3}
              label="หัวข้อที่พบ"
              value={summary.topicCounts.length.toLocaleString("th-TH")}
            />
          </div>
          <div className="dashboard-lower-grid">
            <InsightSummary summary={summary} />
            <section>
              <div className="subsection-heading">
                <div>
                  <p className="section-kicker">Priority queue</p>
                  <h2>รีวิวเชิงลบล่าสุด</h2>
                </div>
              </div>
              <ReviewTable
                results={summary.negativeReviews.slice(0, compact ? 3 : 8)}
                emptyMessage="ไม่พบรีวิวเชิงลบในชุดข้อมูลนี้"
              />
            </section>
          </div>
        </div>
      </div>
    </section>
  );
}

function Metric({
  icon: Icon,
  label,
  value,
}: {
  icon: typeof Clock3;
  label: string;
  value: string;
}) {
  return (
    <div className="metric">
      <Icon aria-hidden="true" size={19} strokeWidth={1.7} />
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}
