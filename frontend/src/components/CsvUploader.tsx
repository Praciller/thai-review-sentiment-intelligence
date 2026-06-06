import { FileSpreadsheet, Upload } from "lucide-react";
import { useRef, useState, type ChangeEvent, type DragEvent } from "react";

import type { ReviewInputRow } from "../types/prediction";
import { parseReviewCsv } from "../utils/reviewData";

interface CsvUploaderProps {
  onRows: (rows: ReviewInputRow[]) => void;
  onError: (message: string) => void;
}

const maxFileBytes = 2 * 1024 * 1024;

export function CsvUploader({ onRows, onError }: CsvUploaderProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [fileName, setFileName] = useState("");

  async function processFile(file: File) {
    if (!file.name.toLowerCase().endsWith(".csv")) {
      onError("รองรับเฉพาะไฟล์ .csv");
      return;
    }
    if (file.size > maxFileBytes) {
      onError("ไฟล์มีขนาดเกิน 2 MB กรุณาแบ่งไฟล์ให้เล็กลง");
      return;
    }

    try {
      const rows = parseReviewCsv(await file.text(), 100);
      setFileName(file.name);
      onRows(rows);
    } catch (error) {
      onError(error instanceof Error ? error.message : "อ่านไฟล์ CSV ไม่สำเร็จ");
    }
  }

  function handleChange(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (file) {
      void processFile(file);
    }
  }

  function handleDrop(event: DragEvent<HTMLDivElement>) {
    event.preventDefault();
    const file = event.dataTransfer.files[0];
    if (file) {
      void processFile(file);
    }
  }

  return (
    <div
      className="upload-zone"
      onDragOver={(event) => event.preventDefault()}
      onDrop={handleDrop}
    >
      <input
        ref={inputRef}
        className="sr-only"
        type="file"
        accept=".csv,text/csv"
        onChange={handleChange}
      />
      <FileSpreadsheet aria-hidden="true" size={32} strokeWidth={1.6} />
      <div>
        <p className="upload-title">
          {fileName || "วางไฟล์ CSV ที่นี่ หรือเลือกจากเครื่อง"}
        </p>
        <p>ต้องมีคอลัมน์ text รองรับสูงสุด 100 รีวิวต่อครั้ง</p>
      </div>
      <button
        className="secondary-button"
        type="button"
        onClick={() => inputRef.current?.click()}
      >
        <Upload aria-hidden="true" size={17} />
        เลือกไฟล์
      </button>
    </div>
  );
}
