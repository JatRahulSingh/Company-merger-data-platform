import os

from databricks import sql


SERVER_HOSTNAME = os.getenv(
    "DATABRICKS_SERVER_HOSTNAME"
)

HTTP_PATH = os.getenv(
    "DATABRICKS_HTTP_PATH"
)


print("Connecting to Databricks...")


with sql.connect(
    server_hostname=SERVER_HOSTNAME,
    http_path=HTTP_PATH,
    auth_type="databricks-oauth",
) as connection:

    with connection.cursor() as cursor:

        cursor.execute("""
            SELECT COUNT(*) AS total_rows
            FROM workspace.gold.fact_sales
        """)

        result = cursor.fetchone()

        print(
            "Total rows in Gold fact_sales:",
            result[0]
        )