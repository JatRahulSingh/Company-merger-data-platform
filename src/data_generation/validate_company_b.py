from pathlib import Path

import pandas as pd


DATA_DIR = Path("data_samples/company_b_generated")


def load_data():
    customers = pd.read_csv(
        DATA_DIR / "customers_dirty.csv"
    )

    products = pd.read_csv(
        DATA_DIR / "products_dirty.csv"
    )

    orders = pd.read_csv(
        DATA_DIR / "orders_dirty.csv"
    )

    order_items = pd.read_csv(
        DATA_DIR / "order_items_dirty.csv"
    )

    return customers, products, orders, order_items


def check_duplicate_keys(
    df,
    column_name,
    table_name,
):
    duplicate_count = df[
        column_name
    ].duplicated().sum()

    if duplicate_count == 0:
        print(
            f"[PASS] {table_name}: "
            f"no duplicate {column_name}"
        )
    else:
        print(
            f"[FAIL] {table_name}: "
            f"{duplicate_count} duplicate "
            f"{column_name} values found"
        )


def check_nulls(
    df,
    columns,
    table_name,
):
    for column in columns:
        null_count = df[column].isna().sum()

        if null_count == 0:
            print(
                f"[PASS] {table_name}.{column}: "
                "no nulls"
            )
        else:
            print(
                f"[FAIL] {table_name}.{column}: "
                f"{null_count} null values"
            )


def check_email_format(customers):
    valid_email_mask = (
        customers["email_address"]
        .fillna("")
        .str.contains(
            r"^[^@\s]+@[^@\s]+\.[^@\s]+$",
            regex=True,
        )
    )

    invalid_count = (
        ~valid_email_mask
    ).sum()

    if invalid_count == 0:
        print(
            "[PASS] All customer emails "
            "have valid format"
        )
    else:
        print(
            f"[FAIL] {invalid_count} customer "
            "emails are missing or invalid"
        )


def check_foreign_key(
    child_df,
    child_column,
    parent_df,
    parent_column,
    relationship_name,
):
    invalid_rows = child_df[
        ~child_df[child_column].isin(
            parent_df[parent_column]
        )
    ]

    invalid_count = len(invalid_rows)

    if invalid_count == 0:
        print(
            f"[PASS] {relationship_name}"
        )
    else:
        print(
            f"[FAIL] {relationship_name}: "
            f"{invalid_count} invalid "
            "foreign keys found"
        )


def check_order_dates(orders):
    parsed_dates = pd.to_datetime(
        orders["txn_date"],
        errors="coerce",
        dayfirst=False,
    )

    invalid_count = (
        parsed_dates.isna().sum()
    )

    if invalid_count == 0:
        print(
            "[PASS] All order dates "
            "can be parsed"
        )
    else:
        print(
            f"[FAIL] {invalid_count} order "
            "dates cannot be parsed"
        )


def check_order_statuses(orders):
    allowed_statuses = {
        "Completed",
        "Cancelled",
        "Returned",
    }

    invalid_rows = orders[
        ~orders["txn_status"].isin(
            allowed_statuses
        )
    ]

    invalid_count = len(invalid_rows)

    if invalid_count == 0:
        print(
            "[PASS] All order statuses "
            "are standardized"
        )
    else:
        print(
            f"[FAIL] {invalid_count} orders "
            "contain non-standard status values"
        )


def check_quantities(order_items):
    quantities = pd.to_numeric(
        order_items["qty"],
        errors="coerce",
    )

    invalid = quantities[
        quantities.isna()
        | (quantities <= 0)
    ]

    if len(invalid) == 0:
        print(
            "[PASS] All quantities are valid"
        )
    else:
        print(
            f"[FAIL] {len(invalid)} order items "
            "contain invalid quantities"
        )


def check_prices(order_items):
    prices = pd.to_numeric(
        order_items["sale_price"],
        errors="coerce",
    )

    invalid = prices[
        prices.isna()
        | (prices <= 0)
    ]

    if len(invalid) == 0:
        print(
            "[PASS] All sale prices are valid"
        )
    else:
        print(
            f"[FAIL] {len(invalid)} order items "
            "contain invalid/unparseable prices"
        )


def check_discounts(order_items):
    discounts = pd.to_numeric(
        order_items["discount"],
        errors="coerce",
    )

    invalid = discounts[
        discounts.isna()
        | (discounts < 0)
        | (discounts > 100)
    ]

    if len(invalid) == 0:
        print(
            "[PASS] All discounts are valid"
        )
    else:
        print(
            f"[FAIL] {len(invalid)} order items "
            "contain invalid/unparseable discounts"
        )


def run_validation():

    (
        customers,
        products,
        orders,
        order_items,
    ) = load_data()

    print("=" * 65)
    print("COMPANY B DIRTY DATA VALIDATION")
    print("=" * 65)

    print("\n1. PRIMARY KEY CHECKS")
    print("-" * 65)

    check_duplicate_keys(
        customers,
        "cust_code",
        "customers",
    )

    check_duplicate_keys(
        products,
        "prd_code",
        "products",
    )

    check_duplicate_keys(
        orders,
        "txn_id",
        "orders",
    )

    check_duplicate_keys(
        order_items,
        "txn_line_id",
        "order_items",
    )

    print("\n2. NULL / FORMAT CHECKS")
    print("-" * 65)

    check_nulls(
        customers,
        [
            "cust_code",
            "full_name",
            "email_address",
            "location",
            "state_name",
            "registered_on",
        ],
        "customers",
    )

    check_nulls(
        products,
        [
            "prd_code",
            "prd_nm",
            "prd_category",
            "selling_price",
        ],
        "products",
    )

    check_email_format(
        customers
    )

    print("\n3. FOREIGN KEY CHECKS")
    print("-" * 65)

    check_foreign_key(
        orders,
        "cust_code",
        customers,
        "cust_code",
        "orders.cust_code -> customers.cust_code",
    )

    check_foreign_key(
        order_items,
        "txn_id",
        orders,
        "txn_id",
        "order_items.txn_id -> orders.txn_id",
    )

    check_foreign_key(
        order_items,
        "prd_code",
        products,
        "prd_code",
        "order_items.prd_code -> products.prd_code",
    )

    print("\n4. BUSINESS / FORMAT CHECKS")
    print("-" * 65)

    check_order_dates(
        orders
    )

    check_order_statuses(
        orders
    )

    check_quantities(
        order_items
    )

    check_prices(
        order_items
    )

    check_discounts(
        order_items
    )

    print("\nDATASET SUMMARY")
    print("-" * 65)

    print(
        f"Customers:   {len(customers):,}"
    )

    print(
        f"Products:    {len(products):,}"
    )

    print(
        f"Orders:      {len(orders):,}"
    )

    print(
        f"Order Items: {len(order_items):,}"
    )

    print("\n" + "=" * 65)
    print(
        "VALIDATION COMPLETE "
        "(FAILURES ARE EXPECTED)"
    )
    print("=" * 65)


if __name__ == "__main__":
    run_validation()