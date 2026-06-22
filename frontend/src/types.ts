export interface Customer {
  id: number;
  name: string;
  tenure: number;
  contract_type: string;
  monthly_charges: number;
  total_charges: number;
  internet_service: string;
  tech_support: string;
  payment_method: string;
  created_at: string;
}

export interface CustomerFormValues {
  name: string;
  tenure: string;
  contract_type: string;
  monthly_charges: string;
  total_charges: string;
  internet_service: string;
  tech_support: string;
  payment_method: string;
}

export interface Prediction {
  id: number;
  customer_id: number;
  churn_probability: number | null;
  predicted_label: boolean | null;
  risk_level: "low" | "medium" | "high" | string | null;
  model_version: string | null;
  created_at: string;
}

export interface LLMExplanation {
  id: number;
  customer_id: number;
  prediction_id: number | null;
  explanation_text: string | null;
  recommendations: string | null;
  created_at: string;
}
