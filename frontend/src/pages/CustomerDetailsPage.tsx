import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";

import { api } from "../api";
import { PageHeader } from "../components/PageHeader";
import { PredictionTable } from "../components/PredictionTable";
import { RiskBadge } from "../components/RiskBadge";
import type { Customer, LLMExplanation, Prediction } from "../types";
import {
  formatContractType,
  formatCurrency,
  formatDate,
  formatInternetService,
  formatPaymentMethod,
  formatPredictedLabel,
  formatProbability,
  formatTechSupport,
} from "../utils";

export function CustomerDetailsPage() {
  const { customerId } = useParams();
  const numericCustomerId = Number(customerId);

  const [customer, setCustomer] = useState<Customer | null>(null);
  const [predictions, setPredictions] = useState<Prediction[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isPredicting, setIsPredicting] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const [predictionError, setPredictionError] = useState("");
  const [latestPrediction, setLatestPrediction] = useState<Prediction | null>(null);
  const [latestExplanations, setLatestExplanations] = useState<LLMExplanation[]>([]);
  const [isExplanationLoading, setIsExplanationLoading] = useState(false);
  const [explanationError, setExplanationError] = useState("");
  const [isGeneratingExplanation, setIsGeneratingExplanation] = useState(false);

  async function loadLatestExplanation(prediction: Prediction | null) {
    if (!prediction) {
      setLatestExplanations([]);
      setIsExplanationLoading(false);
      setExplanationError("");
      return;
    }

    setIsExplanationLoading(true);
    setExplanationError("");

    try {
      const explanations = await api.getPredictionExplanations(prediction.id);
      setLatestExplanations(explanations);
    } catch (error) {
      setExplanationError(
        error instanceof Error ? error.message : "Не удалось загрузить LLM-объяснение.",
      );
    } finally {
      setIsExplanationLoading(false);
    }
  }

  async function loadCustomerDetails() {
    if (!Number.isFinite(numericCustomerId)) {
      setErrorMessage("Некорректный ID клиента.");
      setIsLoading(false);
      return;
    }

    setIsLoading(true);
    setErrorMessage("");

    try {
      const [customerData, predictionData] = await Promise.all([
        api.getCustomer(numericCustomerId),
        api.getCustomerPredictions(numericCustomerId),
      ]);
      const latestPredictionData = predictionData[predictionData.length - 1] ?? null;

      setCustomer(customerData);
      setPredictions(predictionData);
      setLatestPrediction(latestPredictionData);
      await loadLatestExplanation(latestPredictionData);
    } catch (error) {
      setErrorMessage(
        error instanceof Error ? error.message : "Не удалось загрузить данные клиента.",
      );
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    void loadCustomerDetails();
  }, [numericCustomerId]);

  async function handleRunPrediction() {
    if (!customer) {
      return;
    }

    setIsPredicting(true);
    setPredictionError("");

    try {
      const createdPrediction = await api.createPrediction(customer.id);
      setPredictions((current) => [...current, createdPrediction]);
      setLatestPrediction(createdPrediction);
      setLatestExplanations([]);
      setExplanationError("");
    } catch (error) {
      setPredictionError(
        error instanceof Error ? error.message : "Не удалось запустить предсказание.",
      );
    } finally {
      setIsPredicting(false);
    }
  }

  async function handleGenerateExplanation() {
    if (!latestPrediction) {
      return;
    }

    setIsGeneratingExplanation(true);
    setExplanationError("");

    try {
      const createdExplanation = await api.createExplanation(latestPrediction.id);
      setLatestExplanations((current) => [...current, createdExplanation]);
    } catch (error) {
      setExplanationError(
        error instanceof Error ? error.message : "Не удалось сгенерировать объяснение.",
      );
    } finally {
      setIsGeneratingExplanation(false);
    }
  }

  if (isLoading) {
    return <p className="info-banner">Загрузка карточки клиента...</p>;
  }

  if (errorMessage) {
    return (
      <div className="page-stack">
        <p className="error-banner">{errorMessage}</p>
        <Link className="button button-secondary" to="/customers">
          Назад к клиентам
        </Link>
      </div>
    );
  }

  if (!customer) {
    return <p className="empty-state">Клиент не найден.</p>;
  }

  return (
    <div className="page-stack">
      <PageHeader
        eyebrow={`Клиент #${customer.id}`}
        title={customer.name}
        description="Здесь собраны данные клиента, ключевые признаки для модели и полная история предсказаний."
      />

      <section className="grid-two-columns">
        <article className="panel">
          <div className="panel-heading">
            <h3>Параметры клиента</h3>
            <p>Текущие признаки, которые используются ML-моделью для прогноза.</p>
          </div>

          <div className="detail-grid">
            <div>
              <span>Имя</span>
              <strong>{customer.name}</strong>
            </div>
            <div>
              <span>Стаж обслуживания</span>
              <strong>{customer.tenure} мес.</strong>
            </div>
            <div>
              <span>Контракт</span>
              <strong>{formatContractType(customer.contract_type)}</strong>
            </div>
            <div>
              <span>Интернет</span>
              <strong>{formatInternetService(customer.internet_service)}</strong>
            </div>
            <div>
              <span>Техподдержка</span>
              <strong>{formatTechSupport(customer.tech_support)}</strong>
            </div>
            <div>
              <span>Способ оплаты</span>
              <strong>{formatPaymentMethod(customer.payment_method)}</strong>
            </div>
            <div>
              <span>Ежемесячная плата</span>
              <strong>{formatCurrency(customer.monthly_charges)}</strong>
            </div>
            <div>
              <span>Общая сумма платежей</span>
              <strong>{formatCurrency(customer.total_charges)}</strong>
            </div>
            <div>
              <span>Создан</span>
              <strong>{formatDate(customer.created_at)}</strong>
            </div>
          </div>
        </article>

        <article className="panel">
          <div className="panel-heading">
            <h3>Последний результат прогноза</h3>
            <p>Запустите новое предсказание, чтобы добавить запись в историю.</p>
          </div>

          {latestPrediction ? (
            <div className="prediction-summary">
              <div>
                <span>Уровень риска</span>
                <RiskBadge level={latestPrediction.risk_level} />
              </div>
              <div>
                <span>Вероятность оттока</span>
                <strong>{formatProbability(latestPrediction.churn_probability)}</strong>
              </div>
              <div>
                <span>Статус</span>
                <strong>{formatPredictedLabel(latestPrediction.predicted_label)}</strong>
              </div>
              <div>
                <span>Создано</span>
                <strong>{formatDate(latestPrediction.created_at)}</strong>
              </div>
            </div>
          ) : (
            <p className="empty-state">Для этого клиента пока нет предсказаний.</p>
          )}

          <div className="form-actions">
            <button className="button" disabled={isPredicting} onClick={handleRunPrediction}>
              {isPredicting ? "Запуск предсказания..." : "Запустить новое предсказание"}
            </button>
          </div>

          {predictionError ? <p className="error-banner">{predictionError}</p> : null}
        </article>
      </section>

      <section className="panel">
        <div className="panel-heading">
          <h3>LLM-объяснение риска клиента</h3>
          <p>Объяснение строится по последнему сохраненному прогнозу клиента.</p>
        </div>

        {!latestPrediction ? (
          <p className="empty-state">Сначала запустите прогноз для клиента.</p>
        ) : (
          <div className="single-explanation-panel">
            <div className="single-explanation-header">
              <div>
                <h4>Объяснение по последнему прогнозу</h4>
                <p>Прогноз ID: {latestPrediction.id}</p>
              </div>

              <button
                className="button"
                disabled={isGeneratingExplanation}
                onClick={handleGenerateExplanation}
                type="button"
              >
                {isGeneratingExplanation
                  ? "Генерация объяснения..."
                  : "Сгенерировать объяснение по клиенту"}
              </button>
            </div>

            {isExplanationLoading ? (
              <p className="info-banner">Загрузка LLM-объяснения...</p>
            ) : null}
            {explanationError ? <p className="error-banner">{explanationError}</p> : null}

            {latestExplanations.length > 0 ? (
              <article className="explanation-card">
                <h4>Текущее объяснение</h4>
                <p className="multiline-text">
                  {latestExplanations[latestExplanations.length - 1].explanation_text ??
                    "Объяснение отсутствует."}
                </p>
                <div className="recommendations-box">
                  <span>Рекомендации</span>
                  <p className="multiline-text">
                    {latestExplanations[latestExplanations.length - 1].recommendations ??
                      "Рекомендации отсутствуют."}
                  </p>
                </div>
                <p className="explanation-created">
                  Создано: {formatDate(latestExplanations[latestExplanations.length - 1].created_at)}
                </p>
              </article>
            ) : (
              <p className="empty-state">
                Для последнего прогноза пока нет сохраненного объяснения.
              </p>
            )}
          </div>
        )}
      </section>

      <section className="panel">
        <div className="panel-heading">
          <h3>История прогнозов</h3>
          <p>Компактная история всех сохраненных прогнозов клиента.</p>
        </div>

        <PredictionTable predictions={[...predictions].sort((left, right) => right.id - left.id)} />
      </section>
    </div>
  );
}
