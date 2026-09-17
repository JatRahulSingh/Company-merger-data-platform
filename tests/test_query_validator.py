from ai.query_validator import validate_sql


def test_safe_revenue_query():
    query = """
    SELECT
        source_system,
        SUM(recognized_revenue) AS total_revenue
    FROM workspace.gold.fact_sales
    GROUP BY source_system
    """

    is_safe, reason = validate_sql(
        query,
        "Compare revenue by company",
    )

    assert is_safe is True
    assert reason == "Query is safe."


def test_delete_is_blocked():
    query = """
    DELETE FROM workspace.gold.fact_sales
    """

    is_safe, reason = validate_sql(query)

    assert is_safe is False
    assert "Only SELECT" in reason


def test_multiple_statements_are_blocked():
    query = """
    SELECT *
    FROM workspace.gold.fact_sales
    LIMIT 10;

    DELETE FROM workspace.gold.fact_sales;
    """

    is_safe, reason = validate_sql(query)

    assert is_safe is False
    assert "Exactly one SQL statement" in reason


def test_unauthorized_table_is_blocked():
    query = """
    SELECT *
    FROM workspace.bronze.company_b_orders
    LIMIT 10
    """

    is_safe, reason = validate_sql(query)

    assert is_safe is False
    assert "unauthorized tables" in reason.lower()


def test_wrong_revenue_column_is_blocked():
    query = """
    SELECT
        SUM(net_amount) AS total_revenue
    FROM workspace.gold.fact_sales
    """

    is_safe, reason = validate_sql(
        query,
        "What is the total revenue?",
    )

    assert is_safe is False
    assert "recognized_revenue" in reason


def test_general_customer_count_uses_dimension():
    query = """
    SELECT
        COUNT(DISTINCT customer_id) AS customer_count
    FROM workspace.gold.dim_customer
    WHERE source_system = 'company_b'
    """

    is_safe, reason = validate_sql(
        query,
        "How many customers are there in Company B?",
    )

    assert is_safe is True


def test_general_customer_count_from_fact_is_blocked():
    query = """
    SELECT
        COUNT(DISTINCT customer_id) AS customer_count
    FROM workspace.gold.fact_sales
    WHERE source_system = 'company_b'
    """

    is_safe, reason = validate_sql(
        query,
        "How many customers are there in Company B?",
    )

    assert is_safe is False
    assert "dim_customer" in reason


def test_transactional_customer_count_can_use_fact():
    query = """
    SELECT
        COUNT(DISTINCT customer_id) AS customer_count
    FROM workspace.gold.fact_sales
    WHERE source_system = 'company_b'
    """

    is_safe, reason = validate_sql(
        query,
        "How many Company B customers placed orders?",
    )

    assert is_safe is True


def test_detail_query_without_limit_is_blocked():
    query = """
    SELECT
        order_id,
        order_date,
        customer_id
    FROM workspace.gold.fact_sales
    """

    is_safe, reason = validate_sql(query)

    assert is_safe is False
    assert "LIMIT" in reason


def test_detail_query_with_limit_is_allowed():
    query = """
    SELECT
        order_id,
        order_date,
        customer_id
    FROM workspace.gold.fact_sales
    LIMIT 20
    """

    is_safe, reason = validate_sql(query)

    assert is_safe is True


def test_limit_over_50_is_blocked():
    query = """
    SELECT
        order_id
    FROM workspace.gold.fact_sales
    LIMIT 100
    """

    is_safe, reason = validate_sql(query)

    assert is_safe is False
    assert "50" in reason


def test_query_without_table_is_blocked():
    query = """
    SELECT 1
    """

    is_safe, reason = validate_sql(query)

    assert is_safe is False
    assert "No table" in reason