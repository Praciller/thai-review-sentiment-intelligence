import { Database, Filter, Play } from "lucide-react";
import { useMemo, useState } from "react";

import { CsvUploader } from "../components/CsvUploader";
import { ErrorMessage } from "../components/ErrorMessage";
import { LoadingState } from "../components/LoadingState";
import { ReviewTable } from "../components/ReviewTable";
import { predictBatch } from "../services/api";
import { useReviewData } from "../state/reviewDataState";
import {
  sentimentLabels,
  type ReviewInputRow,
  type SentimentLabel,
} from "../types/prediction";
import { sentimentMeta } from "../utils/presentation";
import { sampleReviewRows } from "../utils/sampleData";

type FilterValue = SentimentLabel | "all";

export function BatchPage() {
  const { replaceResults } = useReviewData();
  const [rows, setRows] = useState<ReviewInputRow[]>([]);
  const [results, setResults] = useState<ReturnType<typeof useReviewData>["results"]>(
    [],
  );
  const [filter, setFilter] = useState<FilterValue>("all");
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const filteredResults = useMemo(
    () =>
      filter === "all"
        ? results
        : results.filter((result) => result.predicted_label === filter),
    [filter, results],
  );

  async function runBatch() {
    if (rows.length === 0) {
      setError("กรุณาเลือกไฟล์ CSV ก่อนวิเคราะห์");
      return;
    }
    setIsLoading(true);
    setError("");
    try {
      const predictions = await predictBatch(rows.map((row) => row.text));
      setResults(predictions);
      replaceResults(predictions);
    } catch (caught) {
      setError(
        caught instanceof Error ? caught.message : "วิเคราะห์ไฟล์ไม่สำเร็จ",
      );
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <section className="page-section">
      <div className="page-intro page-intro-compact">
        <p className="section-kicker">Batch analysis</p>
        <h1>วิเคราะห์รีวิวจากไฟล์ CSV</h1>
        <p>
          ตรวจสอบตัวอย่างก่อนส่ง และประมวลผลสูงสุด 100 รีวิวต่อคำขอ
        </p>
      </div>
      {error ? (
        <ErrorMessage message={error} onDismiss={() => setError("")} />
      ) : null}
      <CsvUploader
        onRows={(nextRows) => {
          setRows(nextRows);
          setResults([]);
          setError("");
        }}
        onError={setError}
      />
      <div className="batch-action-row">
        <p>
          {rows.length > 0
            ? `พร้อมวิเคราะห์ ${rows.length.toLocaleString("th-TH")} รีวิว`
            : "ยังไม่ได้เลือกไฟล์"}
        </p>
        <div className="batch-button-group">
          <button
            className="secondary-button"
            disabled={isLoading}
            type="button"
            onClick={() => {
              setRows(sampleReviewRows);
              setResults([]);
              setError("");
            }}
          >
            <Database aria-hidden="true" size={17} />
            ใช้ข้อมูลตัวอย่าง
          </button>
          <button
            className="primary-button"
            disabled={isLoading || rows.length === 0}
            type="button"
            onClick={() => void runBatch()}
          >
            <Play aria-hidden="true" size={17} />
            {isLoading ? "กำลังวิเคราะห์" : "เริ่มวิเคราะห์"}
          </button>
        </div>
      </div>
      {rows.length > 0 && results.length === 0 && !isLoading ? (
        <section className="preview-section">
          <div className="subsection-heading">
            <div>
              <p className="section-kicker">Preview</p>
              <h2>ตัวอย่างข้อมูล</h2>
            </div>
            <span>{rows.length.toLocaleString("th-TH")} แถว</span>
          </div>
          <div className="raw-preview">
            {rows.slice(0, 8).map((row) => (
              <div key={row.id}>
                <span>{row.id}</span>
                <p>{row.text}</p>
              </div>
            ))}
          </div>
        </section>
      ) : null}
      {isLoading ? <LoadingState label="กำลังวิเคราะห์ไฟล์ CSV" /> : null}
      {results.length > 0 ? (
        <section className="batch-results">
          <div className="subsection-heading">
            <div>
              <p className="section-kicker">Results</p>
              <h2>ผลการวิเคราะห์แบบกลุ่ม</h2>
            </div>
            <div className="filter-control">
              <Filter aria-hidden="true" size={17} />
              <label htmlFor="sentiment-filter">กรองผล</label>
              <select
                id="sentiment-filter"
                value={filter}
                onChange={(event) =>
                  setFilter(event.target.value as FilterValue)
                }
              >
                <option value="all">ทั้งหมด</option>
                {sentimentLabels.map((label) => (
                  <option key={label} value={label}>
                    {sentimentMeta[label].label}
                  </option>
                ))}
              </select>
            </div>
          </div>
          <ReviewTable results={filteredResults} />
        </section>
      ) : null}
    </section>
  );
}
