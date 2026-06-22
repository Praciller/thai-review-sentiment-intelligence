import { useMemo, useState } from "react";

import { DashboardOverview } from "../components/DashboardOverview";
import { ErrorMessage } from "../components/ErrorMessage";
import { LoadingState } from "../components/LoadingState";
import { PredictionResult } from "../components/PredictionResult";
import { ReviewInput } from "../components/ReviewInput";
import { predictReview } from "../services/api";
import { useReviewData } from "../state/reviewDataState";
import type { PredictionResult as PredictionResultType } from "../types/prediction";
import { aggregatePredictions } from "../utils/reviewData";

export function PredictionPage() {
  const { results, replaceResults } = useReviewData();
  const [result, setResult] = useState<PredictionResultType | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const summary = useMemo(() => aggregatePredictions(results), [results]);

  async function handlePredict(text: string) {
    setIsLoading(true);
    setError("");
    try {
      const prediction = await predictReview(text);
      setResult(prediction);
      replaceResults([prediction]);
    } catch (caught) {
      setError(
        caught instanceof Error ? caught.message : "วิเคราะห์ข้อความไม่สำเร็จ",
      );
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <>
      <section className="prediction-hero">
        <div className="page-intro">
          <p className="section-kicker">Thai sentiment workspace</p>
          <h1>เข้าใจเสียงลูกค้าไทยในไม่กี่วินาที</h1>
          <p>
            วิเคราะห์ความรู้สึกของรีวิวเพื่อค้นหาประเด็นที่สำคัญ
            และเปลี่ยนข้อมูลข้อความให้พร้อมใช้ตัดสินใจ
          </p>
        </div>
        {error ? (
          <ErrorMessage message={error} onDismiss={() => setError("")} />
        ) : null}
        <div className="prediction-workspace">
          <ReviewInput isLoading={isLoading} onSubmit={handlePredict} />
          {isLoading ? <LoadingState /> : <PredictionResult result={result} />}
        </div>
        <p className="demo-warning">
          ผลลัพธ์นี้เป็นเดโมเพื่อช่วยจัดลำดับการตรวจสอบ ไม่ควรใช้ทำงานธุรกิจอัตโนมัติโดยไม่มีมนุษย์กำกับ
        </p>
      </section>
      <DashboardOverview summary={summary} compact />
    </>
  );
}
