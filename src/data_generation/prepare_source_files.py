from pathlib import Path

import pandas as pd


# ---------------------------------------------------------
# INPUT DIRECTORIES
# ---------------------------------------------------------

COMPANY_A_INPUT_DIR = Path(
    "data_samples/company_a_generated"
)

COMPANY_B_INPUT_DIR = Path(
    "data_samples/company_b_generated"
)


# ---------------------------------------------------------
# OUTPUT DIRECTORIES
# ---------------------------------------------------------

OUTPUT_ROOT = Path(
    "data_samples/source_delivery"
)

COMPANY_A_OUTPUT_DIR = OUTPUT_ROOT / "company_a"

COMPANY_B_OUTPUT_DIR = OUTPUT_ROOT / "company_b"


# ---------------------------------------------------------
# CREATE OUTPUT FOLDERS
# ---------------------------------------------------------

for company_dir in [
    COMPANY_A_OUTPUT_DIR,
    COMPANY_B_OUTPUT_DIR,
]:
    for entity in [
        "customers",
        "products",
        "orders",
        "order_items",
    ]:
        (
            company_dir
            / "raw"
            / entity
        ).mkdir(
            parents=True,
            exist_ok=True,
        )


def prepare_company_a():
    print("Preparing Company A source files...")

    customers = pd.read_csv(
        COMPANY_A_INPUT_DIR / "customers.csv"
    )

    products = pd.read_csv(
        COMPANY_A_INPUT_DIR / "products.csv"
    )

    orders = pd.read_csv(
        COMPANY_A_INPUT_DIR / "orders.csv",
        parse_dates=["order_date"],
    )

    order_items = pd.read_csv(
        COMPANY_A_INPUT_DIR / "order_items.csv"
    )

    # -----------------------------------------------------
    # CUSTOMERS
    # -----------------------------------------------------

    customers.to_csv(
        COMPANY_A_OUTPUT_DIR
        / "raw"
        / "customers"
        / "customers_master.csv",
        index=False,
    )

    # -----------------------------------------------------
    # PRODUCTS
    # -----------------------------------------------------

    products.to_csv(
        COMPANY_A_OUTPUT_DIR
        / "raw"
        / "products"
        / "products_master.csv",
        index=False,
    )

    # -----------------------------------------------------
    # MONTHLY ORDERS
    # -----------------------------------------------------

    orders["year_month"] = (
        orders["order_date"]
        .dt.strftime("%Y_%m")
    )

    for year_month, monthly_orders in (
        orders.groupby("year_month")
    ):

        output = monthly_orders.drop(
            columns=["year_month"]
        )

        output.to_csv(
            COMPANY_A_OUTPUT_DIR
            / "raw"
            / "orders"
            / f"orders_{year_month}.csv",
            index=False,
        )

    # -----------------------------------------------------
    # MONTHLY ORDER ITEMS
    # -----------------------------------------------------
    #
    # order_items does not contain order_date.
    #
    # Therefore we temporarily join it with orders
    # to discover which month each order item belongs to.
    # -----------------------------------------------------

    order_month_lookup = orders[
        [
            "order_id",
            "year_month",
        ]
    ]

    order_items_with_month = (
        order_items.merge(
            order_month_lookup,
            on="order_id",
            how="left",
        )
    )

    for year_month, monthly_items in (
        order_items_with_month.groupby(
            "year_month"
        )
    ):

        output = monthly_items.drop(
            columns=["year_month"]
        )

        output.to_csv(
            COMPANY_A_OUTPUT_DIR
            / "raw"
            / "order_items"
            / f"order_items_{year_month}.csv",
            index=False,
        )

    print("Company A source files prepared.")


def prepare_company_b():
    print("Preparing Company B legacy source files...")

    # IMPORTANT:
    #
    # We deliberately use the DIRTY datasets here.
    # These simulate what Company B actually provides
    # during the acquisition.
    customers = pd.read_csv(
        COMPANY_B_INPUT_DIR
        / "customers_dirty.csv"
    )

    products = pd.read_csv(
        COMPANY_B_INPUT_DIR
        / "products_dirty.csv"
    )

    orders = pd.read_csv(
        COMPANY_B_INPUT_DIR
        / "orders_dirty.csv"
    )

    order_items = pd.read_csv(
        COMPANY_B_INPUT_DIR
        / "order_items_dirty.csv"
    )

    # -----------------------------------------------------
    # LEGACY CUSTOMER DUMP
    # -----------------------------------------------------

    customers.to_csv(
        COMPANY_B_OUTPUT_DIR
        / "raw"
        / "customers"
        / "customers_legacy.csv",
        index=False,
    )

    # -----------------------------------------------------
    # LEGACY PRODUCT DUMP
    # -----------------------------------------------------
    #
    # company_a_product_id is our synthetic "answer key".
    #
    # Company B would NOT actually provide this column,
    # because that mapping is what our pipeline must discover.
    # -----------------------------------------------------

    products_source = products.drop(
        columns=["company_a_product_id"],
        errors="ignore",
    )

    products_source.to_csv(
        COMPANY_B_OUTPUT_DIR
        / "raw"
        / "products"
        / "products_legacy.csv",
        index=False,
    )

    # -----------------------------------------------------
    # SPLIT ORDERS INTO H1 / H2
    # -----------------------------------------------------
    #
    # Because txn_date contains dirty/mixed formats,
    # we should NOT depend on parsing it here.
    #
    # Instead, use the original clean/base orders only
    # to determine which transaction IDs belonged to
    # Jan-Jun versus Jul-Dec.
    #
    # The actual output rows still come from dirty orders.
    # -----------------------------------------------------

    orders_base = pd.read_csv(
        COMPANY_B_INPUT_DIR
        / "orders_base.csv",
        parse_dates=["txn_date"],
    )

    h1_order_ids = set(
        orders_base.loc[
            orders_base[
                "txn_date"
            ].dt.month <= 6,
            "txn_id",
        ]
    )

    h2_order_ids = set(
        orders_base.loc[
            orders_base[
                "txn_date"
            ].dt.month >= 7,
            "txn_id",
        ]
    )

    orders_h1 = orders[
        orders["txn_id"].isin(
            h1_order_ids
        )
    ]

    orders_h2 = orders[
        orders["txn_id"].isin(
            h2_order_ids
        )
    ]

    orders_h1.to_csv(
        COMPANY_B_OUTPUT_DIR
        / "raw"
        / "orders"
        / "orders_2025_H1.csv",
        index=False,
    )

    orders_h2.to_csv(
        COMPANY_B_OUTPUT_DIR
        / "raw"
        / "orders"
        / "orders_2025_H2.csv",
        index=False,
    )

    # -----------------------------------------------------
    # SPLIT ORDER ITEMS INTO H1 / H2
    # -----------------------------------------------------

    order_items_h1 = order_items[
        order_items["txn_id"].isin(
            h1_order_ids
        )
    ]

    order_items_h2 = order_items[
        order_items["txn_id"].isin(
            h2_order_ids
        )
    ]

    # Orphan order items do not match any real order.
    orphan_order_items = order_items[
        ~order_items["txn_id"].isin(
            h1_order_ids | h2_order_ids
        )
    ]

    # Keep orphan rows instead of silently losing them.
    #
    # Put them into H2 to simulate bad legacy records
    # being included in the acquisition dump.
    order_items_h2 = pd.concat(
        [
            order_items_h2,
            orphan_order_items,
        ],
        ignore_index=True,
    )

    order_items_h1.to_csv(
        COMPANY_B_OUTPUT_DIR
        / "raw"
        / "order_items"
        / "order_items_2025_H1.csv",
        index=False,
    )

    order_items_h2.to_csv(
        COMPANY_B_OUTPUT_DIR
        / "raw"
        / "order_items"
        / "order_items_2025_H2.csv",
        index=False,
    )

    print("Company B source files prepared.")


def print_summary():
    print()
    print("=" * 60)
    print("SOURCE DELIVERY PREPARATION COMPLETE")
    print("=" * 60)

    company_a_orders = list(
        (
            COMPANY_A_OUTPUT_DIR
            / "raw"
            / "orders"
        ).glob("*.csv")
    )

    company_a_order_items = list(
        (
            COMPANY_A_OUTPUT_DIR
            / "raw"
            / "order_items"
        ).glob("*.csv")
    )

    print()
    print("Company A")
    print("-" * 30)
    print(
        f"Monthly order files: "
        f"{len(company_a_orders)}"
    )
    print(
        f"Monthly order-item files: "
        f"{len(company_a_order_items)}"
    )

    print()
    print("Company B")
    print("-" * 30)
    print(
        "customers_legacy.csv"
    )
    print(
        "products_legacy.csv"
    )
    print(
        "orders_2025_H1.csv"
    )
    print(
        "orders_2025_H2.csv"
    )
    print(
        "order_items_2025_H1.csv"
    )
    print(
        "order_items_2025_H2.csv"
    )


if __name__ == "__main__":

    prepare_company_a()

    prepare_company_b()

    print_summary()