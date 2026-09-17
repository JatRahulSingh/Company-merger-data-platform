import requests
from decimal import Decimal

OLLAMA_URL = "http://localhost:11434/api/generate"

MODEL_NAME = "qwen2.5-coder:3b"


def format_result_value(
    column_name: str,
    value,
) -> str:

    if value is None:
        return "NULL"

    if isinstance(
        value,
        (int, float, Decimal),
    ):
        numeric_value = float(value)

        is_revenue = (
            "revenue" in column_name.lower()
        )

        if is_revenue:
            if abs(numeric_value) >= 1_000_000_000:
                return (
                    f"₹{numeric_value / 1_000_000_000:.2f} billion"
                )

            if abs(numeric_value) >= 1_000_000:
                return (
                    f"₹{numeric_value / 1_000_000:.2f} million"
                )

            if abs(numeric_value) >= 1_000:
                return (
                    f"₹{numeric_value / 1_000:.2f} thousand"
                )

            return f"₹{numeric_value:.2f}"

    return str(value)

def generate_answer(
    question: str,
    columns,
    rows,
) -> str:
    """
    Convert a Databricks query result into a
    concise natural-language answer.
    """

    result_lines = []

    for row in rows:
        values = [
    format_result_value(
        columns[index],
        value,
    )
    for index, value in enumerate(row)
]

        result_lines.append(
            " | ".join(values)
        )

    result_text = "\n".join(
        result_lines
    )

    column_text = ", ".join(
        columns
    )

    prompt = f"""
You are an analytics assistant.

Answer the user's question using ONLY the database result provided below.

IMPORTANT RULES:

- Include all important values returned by the database that directly answer the question.
- If the result contains a category/name and a numeric metric, include BOTH.
- Do not return only a category or entity name if a relevant metric is available.
- Use numeric values exactly as provided.
- Do not recalculate, rescale, or modify numeric values.
- Do not invent numbers.
- Do not make assumptions beyond the result.
- Keep the answer concise and business-friendly.

METRIC INTERPRETATION RULES:

- Use the result column names to understand what each numeric value represents.
- A column named customer_count represents customers, never orders.
- A column named order_count represents orders.
- A column named total_revenue represents revenue.
- Never change the meaning of a metric based only on wording elsewhere in the question.
- If the question asks how many customers placed orders and the result is customer_count,
  answer with the number of customers who placed at least one order.

MULTI-ROW RESULT RULES:

- If the database returns multiple rows, include EVERY returned row in the answer.
- Never summarize a top-N result using only the first row.
- If the user asks for top 5 and 5 rows are returned, list all 5.
- Preserve the ordering of the database result.
- Include the relevant numeric metric for every row.

RAW RECORD RULES:

- If the user asks to "show", "list", or "display" records and no ranking
  criterion is specified, never describe the records as "top".
- Say "Here are N records" or "Here are N sales records".
- Only use words such as "top", "highest", or "best" when the SQL result
  was explicitly ranked using ORDER BY for the requested metric.

Example:

Question:
Which category generated the highest revenue?

Database result:
Laptops | ₹2.89 billion

Good answer:
Laptops generated the highest revenue, at ₹2.89 billion.

Question:
How many Company B customers placed orders?

Result:
customer_count | 2302

Good answer:
2,302 Company B customers placed at least one order.

Bad answer:
Company B customers placed 2,302 orders.

USER QUESTION:
{question}

RESULT COLUMNS:
{column_text}

DATABASE RESULT:
{result_text}

FINAL ANSWER:
"""

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.1
            },
        },
        timeout=120,
    )

    response.raise_for_status()

    result = response.json()

    answer = result[
        "response"
    ].strip()

    return answer