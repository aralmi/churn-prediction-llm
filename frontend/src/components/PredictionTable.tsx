import type { Prediction } from "../types";
import {
  formatDate,
  formatPredictedLabel,
  formatProbability,
} from "../utils";
import { RiskBadge } from "./RiskBadge";

interface PredictionTableProps {
  predictions: Prediction[];
}

export function PredictionTable({ predictions }: PredictionTableProps) {
  if (predictions.length === 0) {
    return <p className="empty-state">Предсказания для этого раздела пока отсутствуют.</p>;
  }

  return (
    <div className="table-card">
      <table className="data-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Вероятность</th>
            <th>Риск</th>
            <th>Статус</th>
            <th>Модель</th>
            <th>Создано</th>
          </tr>
        </thead>
        <tbody>
          {predictions.map((prediction) => (
            <tr key={prediction.id}>
              <td>{prediction.id}</td>
              <td>{formatProbability(prediction.churn_probability)}</td>
              <td>
                <RiskBadge level={prediction.risk_level} />
              </td>
              <td>{formatPredictedLabel(prediction.predicted_label)}</td>
              <td>{prediction.model_version ?? "Н/Д"}</td>
              <td>{formatDate(prediction.created_at)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
