from ai.analytics_engine import run_query


def test_databricks_connection_and_query():
    query = """
    SELECT
        COUNT(*) AS total_rows
    FROM workspace.gold.fact_sales
    """

    columns, rows = run_query(query)

    assert columns == ["total_rows"]

    assert len(rows) == 1

    assert rows[0][0] > 0