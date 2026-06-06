import {
  Cell,
  Legend,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
} from "recharts";

import {
  sentimentLabels,
  type DashboardSummary,
} from "../types/prediction";
import { sentimentMeta } from "../utils/presentation";

export function SentimentChart({
  counts,
}: {
  counts: DashboardSummary["counts"];
}) {
  const data = sentimentLabels.map((label) => ({
    key: label,
    name: sentimentMeta[label].label,
    value: counts[label],
    color: sentimentMeta[label].color,
  }));
  const total = data.reduce((sum, item) => sum + item.value, 0);

  return (
    <div className="chart-shell">
      <div className="chart-visual" aria-hidden="true">
        <ResponsiveContainer
          width="100%"
          height="100%"
          minWidth={0}
          minHeight={360}
          initialDimension={{ width: 360, height: 360 }}
        >
          <PieChart accessibilityLayer>
            <Pie
              data={data}
              dataKey="value"
              nameKey="name"
              cx="50%"
              cy="50%"
              innerRadius="56%"
              outerRadius="78%"
              paddingAngle={1}
              stroke="#FAF7F1"
              strokeWidth={3}
            >
              {data.map((item) => (
                <Cell key={item.key} fill={item.color} />
              ))}
            </Pie>
            <Tooltip formatter={(value) => Number(value).toLocaleString("th-TH")} />
            <Legend />
          </PieChart>
        </ResponsiveContainer>
        <div className="chart-center">
          <strong>{total.toLocaleString("th-TH")}</strong>
          <span>รีวิวทั้งหมด</span>
        </div>
      </div>
      <table className="sr-only">
        <caption>จำนวนรีวิวแยกตามความรู้สึก</caption>
        <tbody>
          {data.map((item) => (
            <tr key={item.key}>
              <th>{item.name}</th>
              <td>{item.value}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
