import { FormEvent, useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { api } from "../api";
import { PageHeader } from "../components/PageHeader";
import { RiskBadge } from "../components/RiskBadge";
import type { Customer, Prediction } from "../types";
import {
  formatContractType,
  formatCurrency,
  formatInternetService,
  formatProbability,
} from "../utils";

export function PredictPage() {
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [customerIdInput, setCustomerIdInput] = useState("");
  const [result, setResult] = useState<Prediction | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");

  useEffect(() => {
    async function loadCustomers() {
      setIsLoading(true);
      setErrorMessage("");

      try {
        const data = await api.getCustomers();
        setCustomers(data);
        if (data.length > 0) {
          setCustomerIdInput(String(data[0].id));
        }
      } catch (error) {
        setErrorMessage(error instanceof Error ? error.message : "Не удалось загрузить клиентов.");
      } finally {
        setIsLoading(false);
      }
    }

    void loadCustomers();
  }, []);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!selectedCustomer) {
      setErrorMessage("Клиент с таким ID не найден.");
      return;
    }

    setIsSubmitting(true);
    setErrorMessage("");

    try {
      const prediction = await api.createPrediction(selectedCustomer.id);
      setResult(prediction);
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Не удалось создать предсказание.");
    } finally {
      setIsSubmitting(false);
    }
  }

  const normalizedCustomerId = Number(customerIdInput);
  const selectedCustomer = customers.find((customer) => customer.id === normalizedCustomerId);
  const hasCustomerIdInput = customerIdInput.trim() !== "";
  const customerIdNotFound = hasCustomerIdInput && !selectedCustomer;

  return (
    <div className="page-stack">
      <PageHeader
        eyebrow="Прогноз"
        title="Запуск прогноза оттока"
        description="Используйте эту форму, если хотите быстро запустить предсказание без перехода в карточку клиента."
      />

      <section className="grid-two-columns">
        <article className="panel">
          <div className="panel-heading">
            <h3>Форма прогноза</h3>
            <p>Выберите клиента и отправьте запрос на построение нового прогноза.</p>
          </div>

          {isLoading ? <p className="info-banner">Загрузка клиентов...</p> : null}

          {!isLoading ? (
            <form className="form-grid" onSubmit={handleSubmit}>
              <label className="field">
                <span>ID клиента</span>
                <input
                  min="1"
                  placeholder="Например, 1"
                  type="number"
                  value={customerIdInput}
                  onChange={(event) => setCustomerIdInput(event.target.value)}
                />
              </label>

              <label className="field field-full">
                <span>Или выберите клиента из списка</span>
                <select
                  value={selectedCustomer ? String(selectedCustomer.id) : ""}
                  onChange={(event) => setCustomerIdInput(event.target.value)}
                >
                  <option value="">Выберите клиента</option>
                  {customers.length === 0 ? (
                    <option value="">Клиенты отсутствуют</option>
                  ) : null}
                  {customers.map((customer) => (
                    <option key={customer.id} value={customer.id}>
                      #{customer.id} - {customer.name}
                    </option>
                  ))}
                </select>
              </label>

              {customerIdNotFound ? (
                <p className="error-banner field-full">Клиент с таким ID не найден.</p>
              ) : null}

              {selectedCustomer ? (
                <div className="customer-preview field-full">
                  <p>
                    <strong>Контракт:</strong> {formatContractType(selectedCustomer.contract_type)}
                  </p>
                  <p>
                    <strong>Ежемесячный платеж:</strong>{" "}
                    {formatCurrency(selectedCustomer.monthly_charges)}
                  </p>
                  <p>
                    <strong>Интернет:</strong> {formatInternetService(selectedCustomer.internet_service)}
                  </p>
                  <Link className="text-link" to={`/customers/${selectedCustomer.id}`}>
                    Открыть карточку клиента
                  </Link>
                </div>
              ) : null}

              <div className="form-actions field-full">
                <button
                  className="button"
                  disabled={isSubmitting || customers.length === 0 || !selectedCustomer}
                  type="submit"
                >
                  {isSubmitting ? "Запуск..." : "Запустить предсказание"}
                </button>
              </div>
            </form>
          ) : null}

          {errorMessage ? <p className="error-banner">{errorMessage}</p> : null}
        </article>

        <article className="panel">
          <div className="panel-heading">
            <h3>Последний результат</h3>
            <p>Здесь отображается последнее предсказание, созданное на этой странице.</p>
          </div>

          {result ? (
            <div className="prediction-summary">
              <div>
                <span>ID клиента</span>
                <strong>{result.customer_id}</strong>
              </div>
              <div>
                <span>Вероятность</span>
                <strong>{formatProbability(result.churn_probability)}</strong>
              </div>
              <div>
                <span>Уровень риска</span>
                <RiskBadge level={result.risk_level} />
              </div>
              <div>
                <span>Версия модели</span>
                <strong>{result.model_version ?? "Н/Д"}</strong>
              </div>
            </div>
          ) : (
            <p className="empty-state">Запустите предсказание, чтобы увидеть результат здесь.</p>
          )}
        </article>
      </section>
    </div>
  );
}
