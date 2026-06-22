export function formatDate(value: string) {
  return new Intl.DateTimeFormat("ru-RU", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}


export function formatCurrency(value: number) {
  return new Intl.NumberFormat("ru-RU", {
    style: "currency",
    currency: "RUB",
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(value);
}


export function formatProbability(value: number | null) {
  if (value === null) {
    return "Н/Д";
  }

  return `${(value * 100).toFixed(1)}%`;
}


export function formatRiskLevel(level: string | null) {
  if (!level) {
    return "Неизвестно";
  }

  const map: Record<string, string> = {
    low: "Низкий риск",
    medium: "Средний риск",
    high: "Высокий риск",
  };

  return map[level] ?? level;
}


export function formatPredictedLabel(value: boolean | null) {
  if (value === null) {
    return "Н/Д";
  }

  return value ? "Возможен отток" : "Стабилен";
}


export function formatContractType(value: string) {
  const map: Record<string, string> = {
    "Month-to-month": "Помесячный",
    "One year": "На 1 год",
    "Two year": "На 2 года",
  };

  return map[value] ?? value;
}


export function formatInternetService(value: string) {
  const map: Record<string, string> = {
    "Fiber optic": "Оптоволокно",
    DSL: "DSL",
    No: "Нет",
  };

  return map[value] ?? value;
}


export function formatTechSupport(value: string) {
  const map: Record<string, string> = {
    Yes: "Да",
    No: "Нет",
    "No internet service": "Без интернет-услуги",
  };

  return map[value] ?? value;
}


export function formatPaymentMethod(value: string) {
  const map: Record<string, string> = {
    "Electronic check": "Электронный чек",
    "Mailed check": "Чек по почте",
    "Bank transfer (automatic)": "Банковский перевод",
    "Credit card (automatic)": "Банковская карта",
    "Bank transfer": "Банковский перевод",
    "Credit card": "Банковская карта",
  };

  return map[value] ?? value;
}
