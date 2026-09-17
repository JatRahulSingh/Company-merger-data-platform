import os

from dotenv import load_dotenv

from databricks import sql
from databricks.sdk.core import Config


load_dotenv()


PROFILE = os.getenv(
    "DATABRICKS_PROFILE"
)

HTTP_PATH = os.getenv(
    "DATABRICKS_HTTP_PATH"
)

MAX_RESULT_ROWS = 50

def get_databricks_config():
    """
    Loads the locally saved Databricks CLI profile.
    """

    config = Config(
        profile=PROFILE,
        auth_type="databricks-cli",
    )

    return config


def get_access_token(config):
    """
    Gets a valid OAuth access token using the
    Databricks CLI cached authentication.
    """

    headers = config.authenticate()

    authorization_header = headers.get(
        "Authorization"
    )

    if not authorization_header:
        raise ValueError(
            "Could not obtain Databricks access token."
        )

    return authorization_header.replace(
        "Bearer ",
        ""
    )


def run_query(query: str):
    """
    Executes a SQL query against Databricks
    and returns column names and rows.
    """

    if not HTTP_PATH:
        raise ValueError(
            "DATABRICKS_HTTP_PATH is not set."
        )

    config = get_databricks_config()

    access_token = get_access_token(
        config
    )

    server_hostname = (
        config.host
        .replace("https://", "")
        .rstrip("/")
    )

    with sql.connect(
        server_hostname=server_hostname,
        http_path=HTTP_PATH,
        access_token=access_token,
    ) as connection:

        with connection.cursor() as cursor:

            cursor.execute(query)

            columns = [
                column[0]
                    for column in cursor.description
            ]

            rows = cursor.fetchmany(
                MAX_RESULT_ROWS + 1
            )

            if len(rows) > MAX_RESULT_ROWS:
                raise ValueError(
                    "Query returned too many rows. "
                    f"Maximum allowed is {MAX_RESULT_ROWS}. "
                    "Please ask a more specific question."
                )

            return columns, rows