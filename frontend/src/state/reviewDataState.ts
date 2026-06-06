import { createContext, useContext } from "react";

import type { PredictionResult } from "../types/prediction";

export interface ReviewDataContextValue {
  results: PredictionResult[];
  isSampleData: boolean;
  replaceResults: (results: PredictionResult[]) => void;
}

export const ReviewDataContext =
  createContext<ReviewDataContextValue | null>(null);

export function useReviewData(): ReviewDataContextValue {
  const context = useContext(ReviewDataContext);
  if (!context) {
    throw new Error("useReviewData must be used inside ReviewDataProvider");
  }
  return context;
}
