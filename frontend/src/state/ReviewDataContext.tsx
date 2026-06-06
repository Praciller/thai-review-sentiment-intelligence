import {
  useMemo,
  useState,
  type ReactNode,
} from "react";

import { sampleResults } from "../data/sampleResults";
import {
  ReviewDataContext,
  type ReviewDataContextValue,
} from "./reviewDataState";

export function ReviewDataProvider({ children }: { children: ReactNode }) {
  const [results, setResults] = useState(sampleResults);
  const [isSampleData, setIsSampleData] = useState(true);

  const value = useMemo<ReviewDataContextValue>(
    () => ({
      results,
      isSampleData,
      replaceResults: (nextResults) => {
        setResults(nextResults);
        setIsSampleData(false);
      },
    }),
    [isSampleData, results],
  );

  return (
    <ReviewDataContext.Provider value={value}>
      {children}
    </ReviewDataContext.Provider>
  );
}
