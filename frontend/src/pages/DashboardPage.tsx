import { useMemo } from "react";

import { DashboardOverview } from "../components/DashboardOverview";
import { useReviewData } from "../state/reviewDataState";
import { aggregatePredictions } from "../utils/reviewData";

export function DashboardPage() {
  const { results, isSampleData } = useReviewData();
  const summary = useMemo(() => aggregatePredictions(results), [results]);

  return (
    <section className="page-section dashboard-page">
      <div className="page-intro page-intro-compact">
        <p className="section-kicker">Sentiment dashboard</p>
        <h1>ภาพรวมเสียงลูกค้า</h1>
        <p>
          สรุปสัดส่วนความรู้สึก ความมั่นใจ และหัวข้อที่ควรส่งต่อให้ทีมปฏิบัติการ
        </p>
        {isSampleData ? (
          <span className="sample-data-note">
            กำลังแสดงข้อมูลตัวอย่าง วิเคราะห์รีวิวหรืออัปโหลด CSV เพื่อแทนที่
          </span>
        ) : null}
      </div>
      <DashboardOverview summary={summary} />
    </section>
  );
}
