import { CircleAlert, X } from "lucide-react";

export function ErrorMessage({
  message,
  onDismiss,
}: {
  message: string;
  onDismiss?: () => void;
}) {
  return (
    <div className="error-message" role="alert">
      <CircleAlert aria-hidden="true" size={20} />
      <span>{message}</span>
      {onDismiss ? (
        <button
          aria-label="ปิดข้อความแจ้งเตือน"
          type="button"
          onClick={onDismiss}
        >
          <X aria-hidden="true" size={18} />
        </button>
      ) : null}
    </div>
  );
}
