import os
import re
from pathlib import Path

import httpx
from dotenv import load_dotenv

ENV_FILE = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(dotenv_path=ENV_FILE)

CONTRACT_TYPE_MAP = {
    "Month-to-month": "помесячный договор",
    "One year": "договор на один год",
    "Two year": "договор на два года",
}

INTERNET_SERVICE_MAP = {
    "Fiber optic": "оптоволоконный интернет",
    "DSL": "DSL-интернет",
    "No": "нет",
}

TECH_SUPPORT_MAP = {
    "Yes": "да",
    "No": "нет",
    "No internet service": "услуга техподдержки недоступна без интернета",
}

PAYMENT_METHOD_MAP = {
    "Electronic check": "электронный чек",
    "Mailed check": "чек по почте",
    "Bank transfer (automatic)": "банковский перевод",
    "Credit card (automatic)": "банковская карта",
    "Credit card": "банковская карта",
}

RISK_LEVEL_MAP = {
    "low": "низкий риск",
    "medium": "средний риск",
    "high": "высокий риск",
}

PREDICTED_LABEL_MAP = {
    True: "возможен отток",
    False: "клиент, скорее всего, останется",
    None: "статус не определен",
}

POSTPROCESS_REPLACEMENTS = {
    "customer experience": "опыт взаимодействия клиента",
    "relatively low": "относительно низкая",
    "low risk": "низкий риск",
    "medium risk": "средний риск",
    "high risk": "высокий риск",
    "risk level": "уровень риска",
    "model version": "версия модели",
    "churn_probability": "вероятность оттока",
    "churn prediction": "прогноз оттока клиентов",
    "bank transfer": "банковский перевод",
    "credit card": "банковская карта",
    "electronic check": "электронный чек",
    "mailed check": "чек по почте",
    "fiber optic": "оптоволоконный интернет",
    "month-to-month": "помесячный договор",
    "one year": "договор на один год",
    "two year": "договор на два года",
    "experience": "опыт взаимодействия",
    "customer": "клиент",
    "churn": "отток клиентов",
    "retention": "удержание клиентов",
    "probability": "вероятность",
    "prediction": "прогноз",
    "contract": "договор",
    "risk": "риск",
    "improve": "улучшить",
    "reduce": "снизить",
}


def get_ollama_url() -> str:
    """Возвращает URL локального Ollama сервера."""
    return os.getenv("OLLAMA_URL", "http://localhost:11434")


def get_ollama_model() -> str:
    """Возвращает имя модели Ollama."""
    return os.getenv("OLLAMA_MODEL", "llama3.2:3b")


def translate_value(value, mapping: dict) -> str:
    """Переводит значение признака на русский язык."""
    return mapping.get(value, str(value))


def format_probability_value(probability: float | None) -> str:
    """Форматирует вероятность оттока в проценты на русском языке."""
    if probability is None:
        return "не указана"
    return f"{round(probability * 100, 1)}%"


def build_localized_context(customer, prediction) -> dict[str, str]:
    """Готовит локализованные данные для prompt и fallback."""
    return {
        "name": customer.name,
        "tenure": f"{customer.tenure} месяцев",
        "contract_type": translate_value(customer.contract_type, CONTRACT_TYPE_MAP),
        "monthly_charges": str(customer.monthly_charges),
        "total_charges": str(customer.total_charges),
        "internet_service": translate_value(customer.internet_service, INTERNET_SERVICE_MAP),
        "tech_support": translate_value(customer.tech_support, TECH_SUPPORT_MAP),
        "payment_method": translate_value(customer.payment_method, PAYMENT_METHOD_MAP),
        "risk_level": translate_value(prediction.risk_level, RISK_LEVEL_MAP),
        "predicted_label": PREDICTED_LABEL_MAP.get(prediction.predicted_label, "статус не определен"),
        "churn_probability": format_probability_value(prediction.churn_probability),
        "model_version": prediction.model_version or "не указана",
    }


def build_prompt(customer, prediction) -> str:
    """Собирает строгий prompt на русском языке для генерации объяснения."""
    data = build_localized_context(customer, prediction)

    return f"""
Ты объясняешь результат прогноза оттока клиентов в учебном fullstack-проекте.

Обязательные правила:
1. Отвечай строго на русском языке.
2. Не используй английские слова, если есть русский аналог.
3. Не используй слова: relatively, experience, churn, customer.
4. Используй термин "отток клиентов" вместо слова "churn".
5. Используй термин "вероятность оттока" вместо "churn_probability".
6. Используй только переданные данные клиента и результат модели.
7. Не выдумывай дополнительные факты, причины, события или характеристики клиента.
8. Ответ должен быть кратким, понятным и структурированным.
9. Нельзя добавлять технические комментарии, англоязычные пояснения и служебные пометки.

Верни ответ строго в этом формате:
Краткое объяснение:
<2-3 коротких предложения>

Основные факторы:
1. <фактор>
2. <фактор>
3. <фактор>

Рекомендации:
1. <рекомендация>
2. <рекомендация>

Данные клиента:
- Имя: {data["name"]}
- Стаж обслуживания: {data["tenure"]}
- Тип договора: {data["contract_type"]}
- Ежемесячная плата: {data["monthly_charges"]}
- Общая сумма платежей: {data["total_charges"]}
- Интернет-услуга: {data["internet_service"]}
- Техподдержка: {data["tech_support"]}
- Способ оплаты: {data["payment_method"]}

Результат модели:
- Вероятность оттока: {data["churn_probability"]}
- Уровень риска: {data["risk_level"]}
- Итоговый статус: {data["predicted_label"]}
- Версия модели: {data["model_version"]}
""".strip()


def postprocess_text(text: str) -> str:
    """Убирает частые англоязычные фрагменты и нормализует русский текст."""
    cleaned_text = text.strip()

    for english, russian in POSTPROCESS_REPLACEMENTS.items():
        cleaned_text = re.sub(english, russian, cleaned_text, flags=re.IGNORECASE)

    cleaned_text = cleaned_text.replace("Fiber optic", "оптоволоконный интернет")
    cleaned_text = cleaned_text.replace("Month-to-month", "помесячный договор")
    cleaned_text = cleaned_text.replace("One year", "договор на один год")
    cleaned_text = cleaned_text.replace("Two year", "договор на два года")
    cleaned_text = cleaned_text.replace("Electronic check", "электронный чек")
    cleaned_text = cleaned_text.replace("Mailed check", "чек по почте")
    cleaned_text = cleaned_text.replace("Bank transfer", "банковский перевод")
    cleaned_text = cleaned_text.replace("Credit card", "банковская карта")
    cleaned_text = cleaned_text.replace("TechSupport", "техподдержка")
    cleaned_text = cleaned_text.replace("InternetService", "интернет-услуга")

    cleaned_text = re.sub(r"\bLLM\b", "", cleaned_text, flags=re.IGNORECASE)
    cleaned_text = re.sub(r"\bAPI\b", "", cleaned_text, flags=re.IGNORECASE)
    cleaned_text = re.sub(r"\s+\n", "\n", cleaned_text)
    cleaned_text = re.sub(r"\n{3,}", "\n\n", cleaned_text)
    cleaned_text = re.sub(r"[ \t]{2,}", " ", cleaned_text)
    return cleaned_text.strip()


def extract_section(text: str, header: str, next_headers: list[str]) -> str:
    """Извлекает секцию текста между заголовками."""
    if header not in text:
        return ""

    section = text.split(header, maxsplit=1)[1]
    end_positions = [section.find(next_header) for next_header in next_headers if next_header in section]
    if end_positions:
        section = section[: min(end_positions)]
    return section.strip()


def normalize_numbered_list(items: list[str], required_count: int) -> str:
    """Приводит список к стабильному нумерованному формату."""
    normalized_items = [item.strip(" -\n\t") for item in items if item.strip(" -\n\t")]
    normalized_items = normalized_items[:required_count]

    while len(normalized_items) < required_count:
        normalized_items.append("Не указано.")

    return "\n".join(f"{index}. {item}" for index, item in enumerate(normalized_items, start=1))


def split_list_lines(text: str) -> list[str]:
    """Разбивает секцию на элементы списка."""
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    cleaned_lines: list[str] = []
    for line in lines:
        normalized = re.sub(r"^\d+[.)]\s*", "", line)
        cleaned_lines.append(normalized)
    return cleaned_lines


def build_structured_response(
    explanation_summary: str,
    factors: list[str],
    recommendations: list[str],
) -> dict[str, str]:
    """Собирает стабильный формат ответа для хранения в БД."""
    explanation_text = (
        "Краткое объяснение:\n"
        f"{explanation_summary.strip()}\n\n"
        "Основные факторы:\n"
        f"{normalize_numbered_list(factors, required_count=3)}"
    )
    recommendations_text = normalize_numbered_list(recommendations, required_count=2)
    return {
        "explanation_text": explanation_text,
        "recommendations": recommendations_text,
    }


def parse_llm_text(response_text: str) -> dict[str, str]:
    """Преобразует ответ Ollama в стабильный структурированный формат."""
    cleaned_text = postprocess_text(response_text)
    if not cleaned_text:
        return {"explanation_text": "", "recommendations": ""}

    summary = extract_section(
        cleaned_text,
        "Краткое объяснение:",
        ["Основные факторы:", "Рекомендации:"],
    )
    factors_text = extract_section(
        cleaned_text,
        "Основные факторы:",
        ["Рекомендации:"],
    )
    recommendations_text = extract_section(
        cleaned_text,
        "Рекомендации:",
        [],
    )

    if not summary:
        paragraphs = [paragraph.strip() for paragraph in cleaned_text.split("\n\n") if paragraph.strip()]
        summary = paragraphs[0] if paragraphs else "Объяснение не было сформировано."

    factors = split_list_lines(factors_text)
    recommendations = split_list_lines(recommendations_text)

    if not factors:
        factors = [
            "уровень риска рассчитан на основе сочетания условий договора и платежных характеристик",
            "учтены признаки обслуживания и подключенных услуг клиента",
            "на итог влияет рассчитанная моделью вероятность оттока",
        ]

    if not recommendations:
        recommendations = [
            "предложить клиенту персональное удерживающее предложение",
            "связаться с клиентом и уточнить удовлетворенность текущими условиями обслуживания",
        ]

    return build_structured_response(summary, factors, recommendations)


def build_fallback_explanation(customer, prediction) -> dict[str, str]:
    """Возвращает шаблонное объяснение, если Ollama недоступна."""
    data = build_localized_context(customer, prediction)

    summary = (
        f"Для клиента рассчитан {data['risk_level']}. "
        f"Текущая вероятность оттока составляет {data['churn_probability']}. "
        "Оценка сформирована на основе данных о договоре, услугах и платежах клиента."
    )

    factors: list[str] = []
    recommendations: list[str] = []

    if customer.contract_type == "Month-to-month":
        factors.append("у клиента помесячный договор, что обычно означает более низкую устойчивость к смене условий")
        recommendations.append("предложить более выгодный долгосрочный договор с бонусом за продление")

    if customer.tech_support == "No":
        factors.append("у клиента отсутствует техподдержка, что может снижать удовлетворенность сервисом")
        recommendations.append("предложить подключение техподдержки или персональную консультацию")

    if customer.monthly_charges >= 70:
        factors.append("ежемесячная плата находится на повышенном уровне и может усиливать чувствительность к цене")
        recommendations.append("подготовить персональную скидку или более подходящий тариф")

    if not factors:
        factors = [
            "модель учитывает стаж обслуживания клиента",
            "модель учитывает параметры договора и интернет-услуги",
            "модель учитывает платежные характеристики клиента",
        ]

    if len(recommendations) < 2:
        recommendations.append("связаться с клиентом и уточнить его удовлетворенность текущими условиями")
    if len(recommendations) < 2:
        recommendations.append("предложить персональный план удержания на основе текущего тарифа")

    return build_structured_response(summary, factors, recommendations)


def generate_explanation(customer, prediction) -> dict[str, str]:
    """Генерирует текстовое объяснение через Ollama или fallback."""
    payload = {
        "model": get_ollama_model(),
        "prompt": build_prompt(customer, prediction),
        "stream": False,
        "options": {"temperature": 0.2},
    }

    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.post(f"{get_ollama_url()}/api/generate", json=payload)
            response.raise_for_status()

        response_text = response.json().get("response", "").strip()
        parsed_response = parse_llm_text(response_text)

        if not parsed_response["explanation_text"]:
            return build_fallback_explanation(customer, prediction)

        return parsed_response
    except (httpx.HTTPError, ValueError, KeyError):
        return build_fallback_explanation(customer, prediction)
