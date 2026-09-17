import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "qwen2.5-coder:3b"

prompt = """
You are a SQL assistant.

Table:
fact_sales

Columns:
- sale_date DATE
- total_amount DECIMAL

Generate only the SQL query required to answer this question:

What were the total sales in December 2025?
"""

response = requests.post(
    OLLAMA_URL,
    json={
        "model": MODEL,
        "prompt": prompt,
        "stream": False
    }
)

response.raise_for_status()

result = response.json()

print(result["response"])