import { Sparkles } from "lucide-react";
import { useState, type FormEvent } from "react";

const examples = [
  "บริการดี พนักงานน่ารักมาก",
  "คุณภาพไม่สมราคา",
  "ส่งเร็ว แพ็กของเรียบร้อย",
  "ร้านเปิดกี่โมงวันอาทิตย์",
];

interface ReviewInputProps {
  isLoading: boolean;
  onSubmit: (text: string) => Promise<void>;
}

export function ReviewInput({ isLoading, onSubmit }: ReviewInputProps) {
  const [text, setText] = useState(
    "ส้มตำอร่อยมาก รสชาติดี แต่การจัดส่งช้า รอนานเกือบ 2 ชั่วโมง",
  );
  const [localError, setLocalError] = useState("");

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const cleaned = text.trim();
    if (!cleaned) {
      setLocalError("กรุณาพิมพ์ข้อความรีวิว");
      return;
    }
    setLocalError("");
    await onSubmit(cleaned);
  }

  return (
    <form className="review-form" onSubmit={handleSubmit}>
      <label htmlFor="review-text">พิมพ์หรือวางข้อความรีวิว</label>
      <textarea
        id="review-text"
        value={text}
        maxLength={2_000}
        onChange={(event) => setText(event.target.value)}
        aria-describedby="review-help review-count review-error"
      />
      <div className="field-meta">
        <span id="review-help">รองรับภาษาไทย สูงสุด 2,000 ตัวอักษร</span>
        <span id="review-count">{text.length.toLocaleString("th-TH")} / 2,000</span>
      </div>
      {localError ? (
        <p className="field-error" id="review-error">
          {localError}
        </p>
      ) : null}
      <div className="form-action-row">
        <div>
          <p className="example-label">ตัวอย่างรีวิว</p>
          <div className="example-list">
            {examples.map((example) => (
              <button
                className="example-button"
                key={example}
                type="button"
                onClick={() => setText(example)}
              >
                “{example}”
              </button>
            ))}
          </div>
        </div>
        <button className="primary-button" disabled={isLoading} type="submit">
          <Sparkles aria-hidden="true" size={18} />
          {isLoading ? "กำลังวิเคราะห์" : "วิเคราะห์ข้อความ"}
        </button>
      </div>
    </form>
  );
}
