from ai.sql_generator import generate_sql
from ai.query_validator import validate_sql
from ai.analytics_engine import run_query
from ai.answer_generator import generate_answer


def ask_question(question: str) -> str:
    """
    Run the complete AI analytics pipeline
    for one user question.
    """

    sql_query = generate_sql(
        question
    )
    print("\n[Generated SQL]")
    print(sql_query)
    print()

    is_safe, reason = validate_sql(
        sql_query,
        question,
    )

    if not is_safe:

        if "LIMIT" in reason:
            return (
                "That request would return too many records. "
                "Please ask for a smaller sample, for example: "
                "'Show me 20 sales records.'"
            )

        return (
            "I could not safely execute that question. "
         f"Reason: {reason}"
        )

    columns, rows = run_query(
        sql_query
    )

    if not rows:
        return (
            "The query ran successfully, "
            "but no matching data was found."
        )

    answer = generate_answer(
        question,
        columns,
        rows,
    )

    return answer


def main():
    print("=" * 60)
    print("COMPANY MERGER ANALYTICS ASSISTANT")
    print("=" * 60)

    print(
        "\nAsk questions about sales, "
        "customers, products, and companies."
    )

    print(
        "Type 'exit' to close the assistant.\n"
    )

    while True:
        question = input("You: ").strip()

        if question.lower() in {
            "exit",
            "quit",
        }:
            print(
                "\nAssistant: Goodbye!"
            )
            break

        if not question:
            continue

        try:
            answer = ask_question(
                question
            )

            print(
                f"\nAssistant: {answer}\n"
            )

        except Exception as error:
            print(
                "\nAssistant: An error occurred:"
            )

            print(
                f"{error}\n"
            )


if __name__ == "__main__":
    main()