from ai.sql_generator import generate_sql
from ai.query_validator import validate_sql
from ai.analytics_engine import run_query
from ai.answer_generator import generate_answer


question = (
    "Which product category generated "
    "the highest total revenue?"
)


print("=" * 60)
print("USER QUESTION")
print("=" * 60)

print(question)


# ---------------------------------------------------------
# STEP 1: GENERATE SQL USING OLLAMA
# ---------------------------------------------------------

sql_query = generate_sql(question)


print()
print("=" * 60)
print("GENERATED SQL")
print("=" * 60)

print(sql_query)


# ---------------------------------------------------------
# STEP 2: VALIDATE GENERATED SQL
# ---------------------------------------------------------

is_safe, reason = validate_sql(
    sql_query,
    question,
)


print()
print("=" * 60)
print("SQL VALIDATION")
print("=" * 60)

print("Safe:", is_safe)
print("Reason:", reason)


# ---------------------------------------------------------
# STEP 3: BLOCK UNSAFE SQL
# ---------------------------------------------------------

if not is_safe:
    raise ValueError(
        f"SQL query was blocked: {reason}"
    )


# ---------------------------------------------------------
# STEP 4: EXECUTE SAFE SQL IN DATABRICKS
# ---------------------------------------------------------

columns, rows = run_query(
    sql_query
)


print()
print("=" * 60)
print("DATABRICKS RESULT")
print("=" * 60)

print("Columns:")
print(columns)

print()

print("Rows:")

for row in rows:
    print(row)

# ---------------------------------------------------------
# STEP 5: GENERATE NATURAL-LANGUAGE ANSWER
# ---------------------------------------------------------

answer = generate_answer(
    question,
    columns,
    rows,
)


print()
print("=" * 60)
print("FINAL ANSWER")
print("=" * 60)

print(answer)