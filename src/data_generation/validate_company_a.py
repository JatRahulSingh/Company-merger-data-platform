from pathlib import Path

import pandas as pd


DATA_DIR = Path("data_samples/company_a_generated")


def load_data():
    customers = pd.read_csv(
        DATA_DIR / "customers.csv",
        parse_dates=["signup_date"],
    )

    products = pd.read_csv(
        DATA_DIR / "products.csv",
    )

    orders = pd.read_csv(
        DATA_DIR / "orders.csv",
        parse_dates=["order_date"],
    )

    order_items = pd.read_csv(
        DATA_DIR / "order_items.csv",
    )

    return customers, products, orders, order_items


def check_primary_key_duplicates(df, column_name, table_name):
    duplicate_count = df[column_name].duplicated().sum()

    if duplicate_count == 0:
        print(f"[PASS] {table_name}: no duplicate {column_name}")
    else:
        print(
            f"[FAIL] {table_name}: "
            f"{duplicate_count} duplicate {column_name} values found"
        )


def check_required_nulls(df, columns, table_name):
    failed = False

    for column in columns:
        null_count = df[column].isna().sum()

        if null_count > 0:
            print(
                f"[FAIL] {table_name}: "
                f"{null_count} null values found in {column}"
            )
            failed = True

    if not failed:
        print(f"[PASS] {table_name}: required columns contain no nulls")


def check_foreign_key(
    child_df,
    child_column,
    parent_df,
    parent_column,
    relationship_name,
):
    invalid_rows = child_df[
        ~child_df[child_column].isin(parent_df[parent_column])
    ]

    invalid_count = len(invalid_rows)

    if invalid_count == 0:
        print(f"[PASS] {relationship_name}")
    else:
        print(
            f"[FAIL] {relationship_name}: "
            f"{invalid_count} invalid foreign keys found"
        )


def check_order_after_signup(customers, orders):
    merged = orders.merge(
        customers[["customer_id", "signup_date"]],
        on="customer_id",
        how="left",
    )

    invalid_rows = merged[
        merged["order_date"] < merged["signup_date"]
    ]

    invalid_count = len(invalid_rows)

    if invalid_count == 0:
        print("[PASS] All orders occur on or after customer signup")
    else:
        print(
            f"[FAIL] {invalid_count} orders occurred "
            "before customer signup"
        )


def check_positive_values(order_items):
    invalid_quantity = order_items[
        order_items["quantity"] <= 0
    ]

    invalid_price = order_items[
        order_items["unit_price"] <= 0
    ]

    if len(invalid_quantity) == 0:
        print("[PASS] All quantities are greater than 0")
    else:
        print(
            f"[FAIL] {len(invalid_quantity)} "
            "order items have invalid quantities"
        )

    if len(invalid_price) == 0:
        print("[PASS] All unit prices are greater than 0")
    else:
        print(
            f"[FAIL] {len(invalid_price)} "
            "order items have invalid unit prices"
        )


def check_discount_range(order_items):
    invalid_discount = order_items[
        (order_items["discount_pct"] < 0)
        | (order_items["discount_pct"] > 100)
    ]

    invalid_count = len(invalid_discount)

    if invalid_count == 0:
        print("[PASS] All discounts are between 0 and 100")
    else:
        print(
            f"[FAIL] {invalid_count} "
            "order items have invalid discount percentages"
        )


def print_dataset_summary(
    customers,
    products,
    orders,
    order_items,
):
    print("\nDATASET SUMMARY")
    print("-" * 50)

    print(f"Customers:   {len(customers):,}")
    print(f"Products:    {len(products):,}")
    print(f"Orders:      {len(orders):,}")
    print(f"Order Items: {len(order_items):,}")


def run_validation():
    customers, products, orders, order_items = load_data()

    print("=" * 60)
    print("COMPANY A DATA VALIDATION")
    print("=" * 60)

    print("\n1. PRIMARY KEY CHECKS")
    print("-" * 60)

    check_primary_key_duplicates(
        customers,
        "customer_id",
        "customers",
    )

    check_primary_key_duplicates(
        products,
        "product_id",
        "products",
    )

    check_primary_key_duplicates(
        orders,
        "order_id",
        "orders",
    )

    check_primary_key_duplicates(
        order_items,
        "order_item_id",
        "order_items",
    )

    print("\n2. REQUIRED COLUMN NULL CHECKS")
    print("-" * 60)

    check_required_nulls(
        customers,
        [
            "customer_id",
            "customer_name",
            "email",
            "city",
            "state",
            "signup_date",
        ],
        "customers",
    )

    check_required_nulls(
        products,
        [
            "product_id",
            "product_name",
            "category",
            "unit_price",
        ],
        "products",
    )

    check_required_nulls(
        orders,
        [
            "order_id",
            "customer_id",
            "order_date",
            "order_status",
            "payment_method",
        ],
        "orders",
    )

    check_required_nulls(
        order_items,
        [
            "order_item_id",
            "order_id",
            "product_id",
            "quantity",
            "unit_price",
            "discount_pct",
        ],
        "order_items",
    )

    print("\n3. FOREIGN KEY CHECKS")
    print("-" * 60)

    check_foreign_key(
        orders,
        "customer_id",
        customers,
        "customer_id",
        "orders.customer_id -> customers.customer_id",
    )

    check_foreign_key(
        order_items,
        "order_id",
        orders,
        "order_id",
        "order_items.order_id -> orders.order_id",
    )

    check_foreign_key(
        order_items,
        "product_id",
        products,
        "product_id",
        "order_items.product_id -> products.product_id",
    )

    print("\n4. BUSINESS RULE CHECKS")
    print("-" * 60)

    check_order_after_signup(
        customers,
        orders,
    )

    check_positive_values(
        order_items,
    )

    check_discount_range(
        order_items,
    )

    print_dataset_summary(
        customers,
        products,
        orders,
        order_items,
    )

    print("\n" + "=" * 60)
    print("VALIDATION COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    run_validation()