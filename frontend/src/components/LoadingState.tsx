export function LoadingState({ label = "กำลังประมวลผล" }: { label?: string }) {
  return (
    <div className="loading-state" role="status">
      <span className="loading-line loading-line-wide" />
      <span className="loading-line" />
      <span className="loading-line loading-line-short" />
      <span className="sr-only">{label}</span>
    </div>
  );
}
