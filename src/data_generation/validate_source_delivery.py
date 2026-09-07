from pathlib import Path

import pandas as pd


SOURCE_DIR = Path("data_samples/source_delivery")

COMPANY_A_DIR = SOURCE_DIR / "company_a" / "raw"
COMPANY_B_DIR = SOURCE_DIR / "company_b" / "raw"


def count_rows_in_files(folder: Path):
    total_rows = 0
    file_count = 0

    for file_path in folder.glob("*.csv"):
        df = pd.read_csv(file_path)

        total_rows += len(df)
        file_count += 1

    return file_count, total_rows


def validate_company_a():
    print("\nCOMPANY A SOURCE DELIVERY")
    print("-" * 60)

    customers = pd.read_csv(
        COMPANY_A_DIR
        / "customers"
        / "customers_master.csv"
    )

    products = pd.read_csv(
        COMPANY_A_DIR
        / "products"
        / "products_master.csv"
    )

    order_file_count, order_count = count_rows_in_files(
        COMPANY_A_DIR / "orders"
    )

    item_file_count, item_count = count_rows_in_files(
        COMPANY_A_DIR / "order_items"
    )

    print(f"Customers:         {len(customers):,}")
    print(f"Products:          {len(products):,}")
    print(f"Order files:       {order_file_count}")
    print(f"Orders:            {order_count:,}")
    print(f"Order-item files:  {item_file_count}")
    print(f"Order Items:       {item_count:,}")

    expected_customers = 10_000
    expected_products = 200
    expected_orders = 60_000
    expected_order_items = 149_837

    print()

    if len(customers) == expected_customers:
        print("[PASS] Company A customer count matches")
    else:
        print("[FAIL] Company A customer count mismatch")

    if len(products) == expected_products:
        print("[PASS] Company A product count matches")
    else:
        print("[FAIL] Company A product count mismatch")

    if order_count == expected_orders:
        print("[PASS] Company A order count matches")
    else:
        print("[FAIL] Company A order count mismatch")

    if item_count == expected_order_items:
        print("[PASS] Company A order-item count matches")
    else:
        print("[FAIL] Company A order-item count mismatch")


def validate_company_b():
    print("\nCOMPANY B SOURCE DELIVERY")
    print("-" * 60)

    customers = pd.read_csv(
        COMPANY_B_DIR
        / "customers"
        / "customers_legacy.csv"
    )

    products = pd.read_csv(
        COMPANY_B_DIR
        / "products"
        / "products_legacy.csv"
    )

    order_file_count, order_count = count_rows_in_files(
        COMPANY_B_DIR / "orders"
    )

    item_file_count, item_count = count_rows_in_files(
        COMPANY_B_DIR / "order_items"
    )

    print(f"Customers:         {len(customers):,}")
    print(f"Products:          {len(products):,}")
    print(f"Order files:       {order_file_count}")
    print(f"Orders:            {order_count:,}")
    print(f"Order-item files:  {item_file_count}")
    print(f"Order Items:       {item_count:,}")

    expected_customers = 2_550
    expected_products = 105
    expected_orders = 15_000
    expected_order_items = 37_158

    print()

    if len(customers) == expected_customers:
        print("[PASS] Company B customer count matches")
    else:
        print("[FAIL] Company B customer count mismatch")

    if len(products) == expected_products:
        print("[PASS] Company B product count matches")
    else:
        print("[FAIL] Company B product count mismatch")

    if order_count == expected_orders:
        print("[PASS] Company B order count matches")
    else:
        print("[FAIL] Company B order count mismatch")

    if item_count == expected_order_items:
        print("[PASS] Company B order-item count matches")
    else:
        print("[FAIL] Company B order-item count mismatch")


def run_validation():
    print("=" * 60)
    print("SOURCE DELIVERY RECONCILIATION")
    print("=" * 60)

    validate_company_a()
    validate_company_b()

    print("\n" + "=" * 60)
    print("RECONCILIATION COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    run_validation()