import { Activity, FileSpreadsheet, Gauge, MessageSquareText } from "lucide-react";
import { lazy, Suspense } from "react";
import { NavLink, Route, Routes } from "react-router-dom";

import { LoadingState } from "./components/LoadingState";
import { ReviewDataProvider } from "./state/ReviewDataContext";

const PredictionPage = lazy(() =>
  import("./pages/PredictionPage").then((module) => ({
    default: module.PredictionPage,
  })),
);
const BatchPage = lazy(() =>
  import("./pages/BatchPage").then((module) => ({
    default: module.BatchPage,
  })),
);
const DashboardPage = lazy(() =>
  import("./pages/DashboardPage").then((module) => ({
    default: module.DashboardPage,
  })),
);

const navigation = [
  {
    to: "/",
    label: "วิเคราะห์รีวิว",
    icon: MessageSquareText,
    end: true,
  },
  {
    to: "/batch",
    label: "วิเคราะห์แบบกลุ่ม",
    icon: FileSpreadsheet,
    end: false,
  },
  {
    to: "/dashboard",
    label: "แดชบอร์ด",
    icon: Gauge,
    end: false,
  },
];

export default function App() {
  return (
    <ReviewDataProvider>
      <a className="skip-link" href="#main-content">
        ข้ามไปยังเนื้อหาหลัก
      </a>
      <header className="app-header">
        <div className="app-header-inner">
          <NavLink className="brand" to="/" aria-label="Thai Review Intelligence">
            <span className="brand-mark" aria-hidden="true">
              <Activity size={20} />
            </span>
            <span>Thai Review Intelligence</span>
          </NavLink>
          <nav aria-label="เมนูหลัก">
            {navigation.map(({ to, label, icon: Icon, end }) => (
              <NavLink
                key={to}
                to={to}
                end={end}
                className={({ isActive }) =>
                  isActive ? "nav-link nav-link-active" : "nav-link"
                }
              >
                <Icon aria-hidden="true" size={17} />
                <span>{label}</span>
              </NavLink>
            ))}
          </nav>
          <span className="local-badge">Local-first</span>
        </div>
      </header>
      <main id="main-content">
        <Suspense fallback={<LoadingState label="กำลังโหลดหน้า" />}>
          <Routes>
            <Route path="/" element={<PredictionPage />} />
            <Route path="/batch" element={<BatchPage />} />
            <Route path="/dashboard" element={<DashboardPage />} />
          </Routes>
        </Suspense>
      </main>
      <footer>
        <p>
          ผลลัพธ์จากโมเดลภาษาไทยอาจคลาดเคลื่อน
          ควรให้มนุษย์ตรวจสอบกรณีความมั่นใจต่ำ
        </p>
      </footer>
    </ReviewDataProvider>
  );
}
