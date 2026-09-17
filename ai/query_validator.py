from sqlglot import parse, exp


ALLOWED_TABLES = {
    "workspace.gold.fact_sales",
    "workspace.gold.dim_product",
    "workspace.gold.dim_customer",
}


FORBIDDEN_EXPRESSIONS = (
    exp.Insert,
    exp.Update,
    exp.Delete,
    exp.Drop,
    exp.Create,
    exp.Alter,
)


def validate_sql(
    query: str,
    question: str | None = None,
) -> tuple[bool, str]:
    """
    Validate AI-generated SQL before execution.

    Returns:
        (True, "Query is safe.")
        or
        (False, "Reason query was rejected.")
    """

    if not query or not query.strip():
        return False, "Query is empty."

    try:
        statements = parse(
            query,
            dialect="databricks",
        )

        statements = [
            statement
            for statement in statements
            if statement is not None
        ]

        if len(statements) != 1:
            return False, (
                "Exactly one SQL statement is allowed."
            )

        parsed_query = statements[0]

    except Exception as error:
        return False, f"SQL could not be parsed: {error}"

    if not isinstance(parsed_query, exp.Select):
        return False, "Only SELECT queries are allowed."

    for forbidden_type in FORBIDDEN_EXPRESSIONS:
        if parsed_query.find(forbidden_type):
            return False, (
                f"Forbidden SQL operation detected: "
                f"{forbidden_type.__name__}"
            )

    referenced_tables = set()

    for table in parsed_query.find_all(exp.Table):

        catalog = table.catalog
        db = table.db
        name = table.name

        full_name_parts = [
            part
            for part in [catalog, db, name]
            if part
        ]

        full_table_name = ".".join(
            full_name_parts
        ).lower()

        referenced_tables.add(
            full_table_name
        )

    if not referenced_tables:
        return False, "No table was referenced."

    unauthorized_tables = (
        referenced_tables - ALLOWED_TABLES
    )

    if unauthorized_tables:
        return False, (
            "Query references unauthorized tables: "
            + ", ".join(
                sorted(unauthorized_tables)
            )
        )
    if question:
        question_lower = question.lower()

        if "revenue" in question_lower:
            referenced_columns = {
                column.name.lower()
                for column in parsed_query.find_all(exp.Column)
            }

            if "recognized_revenue" not in referenced_columns:
                return False, (
                    "Revenue questions must use "
                    "recognized_revenue."
                )

    if question:
        question_lower = question.lower()

        generic_customer_count_phrases = [
            "how many customers",
            "number of customers",
            "total customers",
        ]

        transactional_customer_phrases = [
            "placed orders",
            "placed an order",
            "purchased",
            "made purchases",
            "bought",
            "ordered",
            "active customers",
        ]

        is_customer_count_question = any(
            phrase in question_lower
            for phrase in generic_customer_count_phrases
        )

        is_transactional_customer_question = any(
            phrase in question_lower
            for phrase in transactional_customer_phrases
        )

        if (
            is_customer_count_question
            and not is_transactional_customer_question
        ):
            if (
                "workspace.gold.dim_customer"
                not in referenced_tables
            ):
                return False, (
                    "General customer counts must use "
                    "workspace.gold.dim_customer."
                )

    MAX_QUERY_LIMIT = 50

    limit_expression = parsed_query.args.get("limit")

    has_aggregation = (
        parsed_query.find(exp.AggFunc)
        is not None
    )

    if not has_aggregation:

        if limit_expression is None:
            return False, (
                "Detail queries must include a LIMIT. "
                f"Maximum allowed is {MAX_QUERY_LIMIT} rows."
            )

        try:
            limit_value = int(
                limit_expression.expression.name
            )
        except Exception:
            return False, (
                "Query LIMIT must be a fixed numeric value."
            )

        if limit_value > MAX_QUERY_LIMIT:
            return False, (
                f"Query LIMIT cannot exceed "
                f"{MAX_QUERY_LIMIT} rows."
            )
    return True, "Query is safe."