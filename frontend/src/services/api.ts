import type {
  BatchPredictionResponse,
  PredictionResult,
} from "../types/prediction";

const apiBaseUrl =
  import.meta.env.VITE_API_URL?.replace(/\/$/, "") ??
  "http://localhost:8000";

async function requestJson<T>(
  path: string,
  init?: RequestInit,
): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${apiBaseUrl}${path}`, {
      ...init,
      headers: {
        "Content-Type": "application/json",
        ...init?.headers,
      },
    });
  } catch {
    throw new Error(
      "เชื่อมต่อ API ไม่ได้ ตรวจสอบว่า FastAPI ทำงานที่พอร์ต 8000",
    );
  }

  if (!response.ok) {
    const payload = (await response.json().catch(() => null)) as
      | { detail?: unknown }
      | null;
    const detail =
      typeof payload?.detail === "string"
        ? payload.detail
        : `API ตอบกลับด้วยสถานะ ${response.status}`;
    throw new Error(detail);
  }
  return (await response.json()) as T;
}

export function predictReview(text: string): Promise<PredictionResult> {
  return requestJson<PredictionResult>("/predict", {
    method: "POST",
    body: JSON.stringify({ text }),
  });
}

export async function predictBatch(
  texts: string[],
): Promise<PredictionResult[]> {
  const response = await requestJson<BatchPredictionResponse>(
    "/predict-batch",
    {
      method: "POST",
      body: JSON.stringify({ texts }),
    },
  );
  return response.results;
}

export async function checkHealth(): Promise<{
  status: string;
  model_name: string;
  runtime_mode: string;
}> {
  return requestJson("/health");
}
