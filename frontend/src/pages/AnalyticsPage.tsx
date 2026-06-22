import { useEffect, useState } from "react";

import { api } from "../api";
import { PageHeader } from "../components/PageHeader";
import { PredictionTable } from "../components/PredictionTable";
import { StatCard } from "../components/StatCard";
import type { Customer, Prediction } from "../types";
import { formatProbability } from "../utils";

export function AnalyticsPage() {
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [predictions, setPredictions] = useState<Prediction[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState("");

  useEffect(() => {
    async function loadAnalytics() {
      setIsLoading(true);
      setErrorMessage("");

      try {
        const customerData = await api.getCustomers();
        const predictionGroups = await Promise.all(
          customerData.map((customer) => api.getCustomerPredictions(customer.id)),
        );

        setCustomers(customerData);
        setPredictions(predictionGroups.flat());
      } catch (error) {
        setErrorMessage(
          error instanceof Error ? error.message : "Не удалось загрузить аналитику.",
        );
      } finally {
        setIsLoading(false);
      }
    }

    void loadAnalytics();
  }, []);

  const riskDistribution = predictions.reduce(
    (accumulator, prediction) => {
      const key = prediction.risk_level ?? "unknown";
      accumulator[key] = (accumulator[key] ?? 0) + 1;
      return accumulator;
    },
    {} as Record<string, number>,
  );

  const averageProbability =
    predictions.length > 0
      ? predictions.reduce(
          (sum, prediction) => sum + (prediction.churn_probability ?? 0),
          0,
        ) / predictions.length
      : 0;

  const recentPredictions = [...predictions]
    .sort((left, right) => right.id - left.id)
    .slice(0, 5);

  return (
    <div className="page-stack">
      <PageHeader
        eyebrow="Аналитика"
        title="Обзор клиентского портфеля"
        description="Здесь собраны основные показатели по клиентской базе и результатам прогнозов: сколько клиентов находится в системе, как распределяются уровни риска и какова средняя вероятность оттока."
      />

      {isLoading ? <p className="info-banner">Загрузка аналитики...</p> : null}
      {errorMessage ? <p className="error-banner">{errorMessage}</p> : null}

      {!isLoading && !errorMessage ? (
        <>
          <section className="stats-grid">
            <StatCard label="Клиенты" value={String(customers.length)} />
            <StatCard
              label="Предсказания"
              value={String(predictions.length)}
            />
            <StatCard
              label="Средняя вероятность оттока"
              value={formatProbability(averageProbability)}
            />
            <StatCard
              label="Предсказания высокого риска"
              value={String(riskDistribution.high ?? 0)}
            />
          </section>

          <section className="grid-two-columns">
            <article className="panel">
              <div className="panel-heading">
                <h3>Распределение уровней риска</h3>
                <p>Количество предсказаний, сгруппированных по уровню риска.</p>
              </div>

              <div className="distribution-list">
                <div className="distribution-item">
                  <span>Низкий риск</span>
                  <strong>{riskDistribution.low ?? 0}</strong>
                </div>
                <div className="distribution-item">
                  <span>Средний риск</span>
                  <strong>{riskDistribution.medium ?? 0}</strong>
                </div>
                <div className="distribution-item">
                  <span>Высокий риск</span>
                  <strong>{riskDistribution.high ?? 0}</strong>
                </div>
              </div>
            </article>

            <article className="panel">
              <div className="panel-heading">
                <h3>Интерпретация</h3>
                <p>Краткая сводка по текущим данным в системе.</p>
              </div>

              <div className="insight-list">
                <p>
                  <strong>Всего отслеживаемых клиентов:</strong> {customers.length}
                </p>
                <p>
                  <strong>Всего созданных предсказаний:</strong> {predictions.length}
                </p>
                <p>
                  <strong>Средняя вероятность оттока:</strong>{" "}
                  {formatProbability(averageProbability)}
                </p>
              </div>
            </article>
          </section>

          <section className="panel">
            <div className="panel-heading">
              <h3>Последние предсказания</h3>
              <p>Пять последних записей предсказаний, доступных из API.</p>
            </div>

            <PredictionTable predictions={recentPredictions} />
          </section>
        </>
      ) : null}
    </div>
  );
}
