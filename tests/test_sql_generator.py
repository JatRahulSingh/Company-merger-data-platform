from ai.sql_generator import generate_sql


def test_revenue_query_uses_recognized_revenue():
    sql = generate_sql(
        "What was the total revenue for Company A?"
    )

    sql_lower = sql.lower()

    assert "recognized_revenue" in sql_lower
    assert "workspace.gold.fact_sales" in sql_lower
    assert "company_a" in sql_lower


def test_customer_master_query_uses_dim_customer():
    sql = generate_sql(
        "How many customers are there in Company B?"
    )

    sql_lower = sql.lower()

    assert "workspace.gold.dim_customer" in sql_lower
    assert "customer_count" in sql_lower


def test_transactional_customer_query_uses_fact_sales():
    sql = generate_sql(
        "How many Company B customers placed orders?"
    )

    sql_lower = sql.lower()

    assert "workspace.gold.fact_sales" in sql_lower
    assert "customer_count" in sql_lower


def test_top_category_query_has_limit():
    sql = generate_sql(
        "Which category had the highest revenue?"
    )

    sql_lower = sql.lower()

    assert "recognized_revenue" in sql_lower
    assert "workspace.gold.dim_product" in sql_lower
    assert "order by" in sql_lower
    assert "limit 1" in sql_lower


def test_detail_query_respects_requested_limit():
    sql = generate_sql(
        "Show me 20 sales records"
    )

    sql_lower = sql.lower()

    assert "workspace.gold.fact_sales" in sql_lower
    assert "limit 20" in sql_lower