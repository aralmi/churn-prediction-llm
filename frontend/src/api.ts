import { API_BASE_URL } from "./config";
import type {
  Customer,
  CustomerFormValues,
  LLMExplanation,
  Prediction,
} from "./types";

class ApiError extends Error {
  status: number;

  constructor(message: string, status: number) {
    super(message);
    this.status = status;
  }
}


async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(options?.headers ?? {}),
    },
    ...options,
  });

  if (!response.ok) {
    let message = `Ошибка запроса: статус ${response.status}`;

    try {
      const errorBody = await response.json();
      if (typeof errorBody.detail === "string") {
        if (errorBody.detail === "Customer not found") {
          message = "Клиент не найден.";
        } else if (errorBody.detail === "Prediction not found") {
          message = "Прогноз не найден.";
        } else if (errorBody.detail === "Model not found. Run python -m app.ml.train_model first.") {
          message = "Модель не найдена. Сначала запустите python -m app.ml.train_model.";
        } else {
          message = errorBody.detail;
        }
      }
    } catch {
      message = response.statusText || message;
    }

    throw new ApiError(message, response.status);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return response.json() as Promise<T>;
}


function mapCustomerPayload(values: CustomerFormValues) {
  return {
    name: values.name.trim(),
    tenure: Number(values.tenure),
    contract_type: values.contract_type,
    monthly_charges: Number(values.monthly_charges),
    total_charges: Number(values.total_charges),
    internet_service: values.internet_service,
    tech_support: values.tech_support,
    payment_method: values.payment_method,
  };
}


export const api = {
  getCustomers() {
    return request<Customer[]>("/api/customers");
  },

  createCustomer(values: CustomerFormValues) {
    return request<Customer>("/api/customers", {
      method: "POST",
      body: JSON.stringify(mapCustomerPayload(values)),
    });
  },

  getCustomer(customerId: number) {
    return request<Customer>(`/api/customers/${customerId}`);
  },

  createPrediction(customerId: number) {
    return request<Prediction>(`/api/predictions/${customerId}`, {
      method: "POST",
    });
  },

  getCustomerPredictions(customerId: number) {
    return request<Prediction[]>(`/api/customers/${customerId}/predictions`);
  },

  createExplanation(predictionId: number) {
    return request<LLMExplanation>(`/api/explanations/${predictionId}`, {
      method: "POST",
    });
  },

  getPredictionExplanations(predictionId: number) {
    return request<LLMExplanation[]>(`/api/predictions/${predictionId}/explanations`);
  },
};

export { ApiError };
