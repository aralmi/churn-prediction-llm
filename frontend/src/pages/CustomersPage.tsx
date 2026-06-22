import { FormEvent, useDeferredValue, useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { api } from "../api";
import { PageHeader } from "../components/PageHeader";
import type { Customer, CustomerFormValues } from "../types";
import {
  formatContractType,
  formatCurrency,
  formatDate,
  formatInternetService,
  formatTechSupport,
} from "../utils";

const initialFormState: CustomerFormValues = {
  name: "",
  tenure: "",
  contract_type: "Month-to-month",
  monthly_charges: "",
  total_charges: "",
  internet_service: "Fiber optic",
  tech_support: "No",
  payment_method: "Electronic check",
};

export function CustomersPage() {
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [loadError, setLoadError] = useState("");
  const [createError, setCreateError] = useState("");
  const [isCreating, setIsCreating] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");
  const [contractFilter, setContractFilter] = useState("all");
  const [formValues, setFormValues] = useState<CustomerFormValues>(initialFormState);

  const deferredSearchTerm = useDeferredValue(searchTerm);

  async function loadCustomers() {
    setIsLoading(true);
    setLoadError("");

    try {
      const data = await api.getCustomers();
      setCustomers(data);
    } catch (error) {
      setLoadError(error instanceof Error ? error.message : "Не удалось загрузить список клиентов.");
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    void loadCustomers();
  }, []);

  async function handleCreateCustomer(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsCreating(true);
    setCreateError("");

    try {
      await api.createCustomer(formValues);
      setFormValues(initialFormState);
      await loadCustomers();
    } catch (error) {
      setCreateError(error instanceof Error ? error.message : "Не удалось создать клиента.");
    } finally {
      setIsCreating(false);
    }
  }

  const contractOptions = Array.from(new Set(customers.map((customer) => customer.contract_type)));
  const filteredCustomers = customers.filter((customer) => {
    const matchesSearch =
      customer.name.toLowerCase().includes(deferredSearchTerm.toLowerCase()) ||
      String(customer.id).includes(deferredSearchTerm.trim());
    const matchesContract =
      contractFilter === "all" || customer.contract_type === contractFilter;

    return matchesSearch && matchesContract;
  });

  return (
    <div className="page-stack">
      <PageHeader
        eyebrow="Клиенты"
        title="Реестр клиентов"
        description="Просматривайте клиентскую базу, фильтруйте записи и добавляйте новых клиентов для дальнейшего прогноза оттока."
      />

      <section className="grid-two-columns">
        <article className="panel">
          <div className="panel-heading">
            <h3>Поиск и фильтр</h3>
            <p>Показано {filteredCustomers.length} из {customers.length} клиентов</p>
          </div>

          <form className="form-grid" onSubmit={(event) => event.preventDefault()}>
            <label className="field">
              <span>Поиск по имени или ID</span>
              <input
                type="text"
                placeholder="Иван Петров или 12"
                value={searchTerm}
                onChange={(event) => setSearchTerm(event.target.value)}
              />
            </label>

            <label className="field">
              <span>Тип контракта</span>
              <select
                value={contractFilter}
                onChange={(event) => setContractFilter(event.target.value)}
              >
                <option value="all">Все контракты</option>
                {contractOptions.map((option) => (
                  <option key={option} value={option}>
                    {formatContractType(option)}
                  </option>
                ))}
              </select>
            </label>
          </form>
        </article>

        <article className="panel">
          <div className="panel-heading">
            <h3>Добавить клиента</h3>
            <p>Создайте новую запись клиента в базе данных приложения.</p>
          </div>

          <form className="form-grid" onSubmit={handleCreateCustomer}>
            <label className="field field-full">
              <span>Имя</span>
              <input
                required
                type="text"
                value={formValues.name}
                onChange={(event) =>
                  setFormValues((current) => ({ ...current, name: event.target.value }))
                }
              />
            </label>

            <label className="field">
              <span>Стаж обслуживания</span>
              <input
                required
                min="0"
                type="number"
                value={formValues.tenure}
                onChange={(event) =>
                  setFormValues((current) => ({ ...current, tenure: event.target.value }))
                }
              />
            </label>

            <label className="field">
              <span>Тип контракта</span>
              <select
                value={formValues.contract_type}
                onChange={(event) =>
                  setFormValues((current) => ({
                    ...current,
                    contract_type: event.target.value,
                  }))
                }
              >
                <option value="Month-to-month">Помесячный</option>
                <option value="One year">На 1 год</option>
                <option value="Two year">На 2 года</option>
              </select>
            </label>

            <label className="field">
              <span>Ежемесячная плата</span>
              <input
                required
                min="0"
                step="0.01"
                type="number"
                value={formValues.monthly_charges}
                onChange={(event) =>
                  setFormValues((current) => ({
                    ...current,
                    monthly_charges: event.target.value,
                  }))
                }
              />
            </label>

            <label className="field">
              <span>Общая сумма платежей</span>
              <input
                required
                min="0"
                step="0.01"
                type="number"
                value={formValues.total_charges}
                onChange={(event) =>
                  setFormValues((current) => ({
                    ...current,
                    total_charges: event.target.value,
                  }))
                }
              />
            </label>

            <label className="field">
              <span>Интернет-услуга</span>
              <select
                value={formValues.internet_service}
                onChange={(event) =>
                  setFormValues((current) => ({
                    ...current,
                    internet_service: event.target.value,
                  }))
                }
              >
                <option value="Fiber optic">Оптоволокно</option>
                <option value="DSL">DSL</option>
                <option value="No">Нет</option>
              </select>
            </label>

            <label className="field">
              <span>Техподдержка</span>
              <select
                value={formValues.tech_support}
                onChange={(event) =>
                  setFormValues((current) => ({
                    ...current,
                    tech_support: event.target.value,
                  }))
                }
              >
                <option value="Yes">Да</option>
                <option value="No">Нет</option>
                <option value="No internet service">Без интернет-услуги</option>
              </select>
            </label>

            <label className="field field-full">
              <span>Способ оплаты</span>
              <select
                value={formValues.payment_method}
                onChange={(event) =>
                  setFormValues((current) => ({
                    ...current,
                    payment_method: event.target.value,
                  }))
                }
              >
                <option value="Electronic check">Электронный чек</option>
                <option value="Mailed check">Чек по почте</option>
                <option value="Bank transfer (automatic)">Банковский перевод</option>
                <option value="Credit card (automatic)">Банковская карта</option>
              </select>
            </label>

            <div className="form-actions field-full">
              <button className="button" disabled={isCreating} type="submit">
                {isCreating ? "Создание..." : "Создать клиента"}
              </button>
            </div>
          </form>

          {createError ? <p className="error-banner">{createError}</p> : null}
        </article>
      </section>

      <section className="panel">
        <div className="panel-heading">
          <h3>Таблица клиентов</h3>
          <p>Подробный список для просмотра и перехода в карточки клиентов.</p>
        </div>

        {isLoading ? <p className="info-banner">Загрузка клиентов...</p> : null}
        {loadError ? <p className="error-banner">{loadError}</p> : null}

        {!isLoading && !loadError ? (
          filteredCustomers.length > 0 ? (
            <div className="table-card">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Имя</th>
                    <th>Стаж</th>
                    <th>Контракт</th>
                    <th>Месячный платеж</th>
                    <th>Общий платеж</th>
                    <th>Интернет</th>
                    <th>Техподдержка</th>
                    <th>Создан</th>
                    <th>Открыть</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredCustomers.map((customer) => (
                    <tr key={customer.id}>
                      <td>{customer.id}</td>
                      <td>{customer.name}</td>
                      <td>{customer.tenure}</td>
                      <td>{formatContractType(customer.contract_type)}</td>
                      <td>{formatCurrency(customer.monthly_charges)}</td>
                      <td>{formatCurrency(customer.total_charges)}</td>
                      <td>{formatInternetService(customer.internet_service)}</td>
                      <td>{formatTechSupport(customer.tech_support)}</td>
                      <td>{formatDate(customer.created_at)}</td>
                      <td>
                        <Link className="text-link" to={`/customers/${customer.id}`}>
                          Открыть карточку
                        </Link>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <p className="empty-state">По текущему фильтру клиенты не найдены.</p>
          )
        ) : null}
      </section>
    </div>
  );
}
