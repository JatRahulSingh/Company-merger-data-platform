import random
from pathlib import Path
from datetime import date

import numpy as np
import pandas as pd
from faker import Faker


SEED = 84

random.seed(SEED)
np.random.seed(SEED)
fake = Faker("en_IN")
Faker.seed(SEED)


OUTPUT_DIR = Path("data_samples/company_b_generated")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


COMPANY_A_DIR = Path("data_samples/company_a_generated")


def load_company_a_products() -> pd.DataFrame:
    return pd.read_csv(
        COMPANY_A_DIR / "products.csv"
    )


def generate_company_b_customers(
    n_customers: int = 2500,
) -> pd.DataFrame:

    cities = {
        "Maharashtra": ["Mumbai", "Pune", "Nagpur"],
        "Karnataka": ["Bengaluru", "Mysuru"],
        "Rajasthan": ["Jaipur", "Jodhpur"],
        "Delhi": ["New Delhi"],
        "Telangana": ["Hyderabad"],
        "Tamil Nadu": ["Chennai", "Coimbatore"],
        "Andhra Pradesh": ["Visakhapatnam", "Vijayawada"],
        "Gujarat": ["Ahmedabad", "Surat"],
    }

    rows = []

    start_date = date(2024, 1, 1)
    end_date = date(2025, 12, 31)

    for i in range(1, n_customers + 1):

        state = random.choice(
            list(cities.keys())
        )

        city = random.choice(
            cities[state]
        )

        rows.append(
            {
                "cust_code": f"B-C{i:05d}",
                "full_name": fake.name(),
                "email_address": fake.email(),
                "location": city,
                "state_name": state,
                "registered_on": fake.date_between(
                    start_date=start_date,
                    end_date=end_date,
                ).strftime("%Y-%m-%d"),
            }
        )

    return pd.DataFrame(rows)


def generate_company_b_products(
    company_a_products: pd.DataFrame,
    n_products: int = 100,
    overlap_ratio: float = 0.70,
) -> pd.DataFrame:

    overlap_count = int(
        n_products * overlap_ratio
    )

    new_product_count = (
        n_products - overlap_count
    )

    rows = []

    # 70% are actually existing Company A products
    overlap_products = company_a_products.sample(
        n=overlap_count,
        random_state=SEED,
    )

    product_counter = 1

    for _, product in overlap_products.iterrows():

        rows.append(
            {
                "prd_code": f"B-P{product_counter:04d}",
                "prd_nm": product["product_name"],
                "prd_category": product["category"],
                "selling_price": str(
                    product["unit_price"]
                ),
                "company_a_product_id": product[
                    "product_id"
                ],
            }
        )

        product_counter += 1

    categories = [
        "Laptops",
        "Smartphones",
        "Accessories",
        "Wearables",
        "Monitors",
    ]

    new_names = [
        "Portable Speaker",
        "Gaming Controller",
        "Wireless Charger",
        "Laptop Stand",
        "Web Camera",
        "Portable SSD",
        "Tablet Pro",
        "Smart Ring",
    ]

    for _ in range(new_product_count):

        category = random.choice(categories)
        product_name = random.choice(new_names)

        model_number = random.randint(
            100,
            999,
        )

        price = random.randint(
            1000,
            80000,
        )

        rows.append(
            {
                "prd_code": f"B-P{product_counter:04d}",
                "prd_nm": (
                    f"{product_name} {model_number}"
                ),
                "prd_category": category,
                "selling_price": str(price),
                "company_a_product_id": None,
            }
        )

        product_counter += 1

    return pd.DataFrame(rows)

def corrupt_customer_data(customers_df: pd.DataFrame) -> pd.DataFrame:
    df = customers_df.copy()

    # 1. Missing emails
    missing_email_idx = df.sample(
        frac=0.05,
        random_state=101,
    ).index

    df.loc[
        missing_email_idx,
        "email_address",
    ] = None

    # 2. Invalid email formats
    invalid_email_idx = df.drop(
        index=missing_email_idx
    ).sample(
        frac=0.03,
        random_state=102,
    ).index

    df.loc[
        invalid_email_idx,
        "email_address",
    ] = "invalid-email"

    # 3. City variations
    bengaluru_idx = df[
        df["location"] == "Bengaluru"
    ].sample(
        frac=0.60,
        random_state=103,
    ).index

    bengaluru_variants = [
        "Bangalore",
        "BLR",
        "bengaluru",
    ]

    for idx in bengaluru_idx:
        df.loc[idx, "location"] = random.choice(
            bengaluru_variants
        )

    # 4. State casing inconsistencies
    state_case_idx = df.sample(
        frac=0.08,
        random_state=104,
    ).index

    for idx in state_case_idx:
        value = df.loc[
            idx,
            "state_name",
        ]

        df.loc[
            idx,
            "state_name",
        ] = random.choice(
            [
                value.lower(),
                value.upper(),
            ]
        )

    # 5. Mixed registration date formats
    date_idx = df.sample(
        frac=0.12,
        random_state=105,
    ).index

    for idx in date_idx:
        value = pd.to_datetime(
            df.loc[
                idx,
                "registered_on",
            ]
        )

        df.loc[
            idx,
            "registered_on",
        ] = random.choice(
            [
                value.strftime("%d/%m/%Y"),
                value.strftime("%m-%d-%Y"),
                value.strftime("%d-%b-%Y"),
            ]
        )

    # 6. Duplicate customer records
    duplicates = df.sample(
        n=50,
        random_state=106,
    ).copy()

    df = pd.concat(
        [
            df,
            duplicates,
        ],
        ignore_index=True,
    )

    return df


def corrupt_product_data(products_df: pd.DataFrame) -> pd.DataFrame:
    df = products_df.copy()

    # 1. Product-name variations
    name_idx = df.sample(
        frac=0.30,
        random_state=201,
    ).index

    for idx in name_idx:
        value = df.loc[
            idx,
            "prd_nm",
        ]

        transformation = random.choice(
            [
                "lower",
                "remove_spaces",
                "hyphen",
            ]
        )

        if transformation == "lower":
            value = value.lower()

        elif transformation == "remove_spaces":
            value = value.replace(
                " ",
                "",
            )

        elif transformation == "hyphen":
            value = value.replace(
                " ",
                "-",
            )

        df.loc[
            idx,
            "prd_nm",
        ] = value

    # 2. Category inconsistencies
    category_idx = df.sample(
        frac=0.15,
        random_state=202,
    ).index

    for idx in category_idx:
        value = df.loc[
            idx,
            "prd_category",
        ]

        df.loc[
            idx,
            "prd_category",
        ] = random.choice(
            [
                value.lower(),
                value.upper(),
                value.rstrip("s"),
            ]
        )

    # 3. Price formatting issues
    price_idx = df.sample(
        frac=0.25,
        random_state=203,
    ).index

    for idx in price_idx:
        price = float(
            df.loc[
                idx,
                "selling_price",
            ]
        )

        price = int(price)

        format_type = random.choice(
            [
                "rupee",
                "comma",
                "plain",
            ]
        )

        if format_type == "rupee":
            df.loc[
                idx,
                "selling_price",
            ] = f"₹{price:,}"

        elif format_type == "comma":
            df.loc[
                idx,
                "selling_price",
            ] = f"{price:,}"

        else:
            df.loc[
                idx,
                "selling_price",
            ] = str(price)

    # 4. Missing prices
    missing_price_idx = df.sample(
        frac=0.05,
        random_state=204,
    ).index

    df.loc[
        missing_price_idx,
        "selling_price",
    ] = None

    # 5. Duplicate products
    duplicates = df.sample(
        n=5,
        random_state=205,
    ).copy()

    df = pd.concat(
        [
            df,
            duplicates,
        ],
        ignore_index=True,
    )

    return df
def generate_company_b_orders(
    customers_base_df: pd.DataFrame,
    n_orders: int = 15_000,
) -> pd.DataFrame:

    start_date = date(2025, 1, 1)
    end_date = date(2025, 12, 31)

    statuses = [
        "Completed",
        "Cancelled",
        "Returned",
    ]

    payment_methods = [
        "UPI",
        "Credit Card",
        "Debit Card",
        "Net Banking",
        "Cash on Delivery",
    ]

    customers = customers_base_df.copy()

    customers["registered_on"] = pd.to_datetime(
        customers["registered_on"]
    ).dt.date

    rows = []

    for i in range(1, n_orders + 1):

        order_date = fake.date_between(
            start_date=start_date,
            end_date=end_date,
        )

        while True:
            customer = customers.sample(1).iloc[0]

            if customer["registered_on"] <= order_date:
                break

        rows.append(
            {
                "txn_id": f"B-T{i:07d}",
                "cust_code": customer["cust_code"],
                "txn_date": order_date.strftime("%Y-%m-%d"),
                "txn_status": random.choice(statuses),
                "payment_type": random.choice(payment_methods),
            }
        )

    return pd.DataFrame(rows)


def generate_company_b_order_items(
    orders_base_df: pd.DataFrame,
    products_base_df: pd.DataFrame,
) -> pd.DataFrame:

    rows = []

    line_counter = 1

    for _, order in orders_base_df.iterrows():

        number_of_items = random.randint(1, 4)

        selected_products = products_base_df.sample(
            n=number_of_items,
            replace=False,
        )

        for _, product in selected_products.iterrows():

            quantity = random.choices(
                population=[1, 2, 3, 4],
                weights=[70, 20, 8, 2],
                k=1,
            )[0]

            sale_price = float(product["selling_price"])

            discount = random.choice(
                [0, 5, 10, 15, 20]
            )

            rows.append(
                {
                    "txn_line_id": f"B-L{line_counter:08d}",
                    "txn_id": order["txn_id"],
                    "prd_code": product["prd_code"],
                    "qty": str(quantity),
                    "sale_price": str(
                        round(sale_price, 2)
                    ),
                    "discount": str(discount),
                }
            )

            line_counter += 1

    return pd.DataFrame(rows)
def corrupt_order_data(orders_df: pd.DataFrame) -> pd.DataFrame:
    df = orders_df.copy()

    # 1. Mixed date formats
    date_idx = df.sample(
        frac=0.15,
        random_state=301,
    ).index

    for idx in date_idx:
        value = pd.to_datetime(
            df.loc[idx, "txn_date"]
        )

        df.loc[idx, "txn_date"] = random.choice(
            [
                value.strftime("%d/%m/%Y"),
                value.strftime("%m-%d-%Y"),
                value.strftime("%d-%b-%Y"),
            ]
        )

    # 2. Invalid dates
    invalid_date_idx = df.sample(
        frac=0.01,
        random_state=302,
    ).index

    df.loc[
        invalid_date_idx,
        "txn_date",
    ] = "31/02/2025"

    # 3. Status inconsistencies
    status_idx = df.sample(
        frac=0.20,
        random_state=303,
    ).index

    status_map = {
        "Completed": [
            "complete",
            "COMPLETED",
            "done",
        ],
        "Cancelled": [
            "cancel",
            "CANCELLED",
        ],
        "Returned": [
            "return",
            "RETURNED",
        ],
    }

    for idx in status_idx:
        current = df.loc[idx, "txn_status"]

        df.loc[
            idx,
            "txn_status",
        ] = random.choice(
            status_map[current]
        )

    # 4. Payment inconsistencies
    payment_idx = df.sample(
        frac=0.15,
        random_state=304,
    ).index

    payment_map = {
        "UPI": ["upi", "GPay", "PhonePe"],
        "Credit Card": ["credit_card", "CC"],
        "Debit Card": ["debit_card", "DC"],
        "Net Banking": ["netbanking", "NB"],
        "Cash on Delivery": ["COD", "cash"],
    }

    for idx in payment_idx:
        current = df.loc[idx, "payment_type"]

        df.loc[
            idx,
            "payment_type",
        ] = random.choice(
            payment_map[current]
        )

    # 5. Unknown customer IDs
    orphan_idx = df.sample(
        frac=0.01,
        random_state=305,
    ).index

    df.loc[
        orphan_idx,
        "cust_code",
    ] = "UNKNOWN_CUSTOMER"

    return df


def corrupt_order_item_data(
    order_items_df: pd.DataFrame,
) -> pd.DataFrame:

    df = order_items_df.copy()

    # 1. Negative or zero quantities
    bad_qty_idx = df.sample(
        frac=0.02,
        random_state=401,
    ).index

    for idx in bad_qty_idx:
        df.loc[
            idx,
            "qty",
        ] = random.choice(
            ["0", "-1", "-2"]
        )

    # 2. Price formatting issues
    price_idx = df.sample(
        frac=0.15,
        random_state=402,
    ).index

    for idx in price_idx:
        price = float(
            df.loc[idx, "sale_price"]
        )

        price_int = int(price)

        df.loc[
            idx,
            "sale_price",
        ] = random.choice(
            [
                f"₹{price_int:,}",
                f"{price_int:,}",
                str(price_int),
            ]
        )

    # 3. Discount format inconsistencies
    discount_idx = df.sample(
        frac=0.20,
        random_state=403,
    ).index

    for idx in discount_idx:
        value = float(
            df.loc[idx, "discount"]
        )

        df.loc[
            idx,
            "discount",
        ] = random.choice(
            [
                f"{int(value)}%",
                str(value / 100),
                str(int(value)),
            ]
        )

    # 4. Orphan order IDs
    orphan_order_idx = df.sample(
        frac=0.01,
        random_state=404,
    ).index

    df.loc[
        orphan_order_idx,
        "txn_id",
    ] = "UNKNOWN_ORDER"

    # 5. Invalid product IDs
    orphan_product_idx = df.sample(
        frac=0.01,
        random_state=405,
    ).index

    df.loc[
        orphan_product_idx,
        "prd_code",
    ] = "UNKNOWN_PRODUCT"

    return df


if __name__ == "__main__":

    print("Generating Company B base data...")

    # Load Company A products so Company B can contain
    # overlapping products that represent the same real-world items.
    company_a_products = load_company_a_products()

    # Generate clean/base Company B master data.
    customers_base_df = generate_company_b_customers()

    products_base_df = generate_company_b_products(
        company_a_products
    )

    # Inject customer and product data-quality issues.
    print("Injecting customer data-quality issues...")

    customers_dirty_df = corrupt_customer_data(
        customers_base_df
    )

    print("Injecting product data-quality issues...")

    products_dirty_df = corrupt_product_data(
        products_base_df
    )

    # Generate clean/base transactional data.
    print("Generating Company B orders...")

    orders_base_df = generate_company_b_orders(
        customers_base_df
    )

    print("Generating Company B order items...")

    order_items_base_df = generate_company_b_order_items(
        orders_base_df,
        products_base_df,
    )

    # Inject transactional data-quality issues.
    print("Injecting order data-quality issues...")

    orders_dirty_df = corrupt_order_data(
        orders_base_df
    )

    print("Injecting order-item data-quality issues...")

    order_items_dirty_df = corrupt_order_item_data(
        order_items_base_df
    )

    # ---------------------------------------------------------
    # SAVE BASE / CLEAN DATA
    # ---------------------------------------------------------

    customers_base_df.to_csv(
        OUTPUT_DIR / "customers_base.csv",
        index=False,
    )

    products_base_df.to_csv(
        OUTPUT_DIR / "products_base.csv",
        index=False,
    )

    orders_base_df.to_csv(
        OUTPUT_DIR / "orders_base.csv",
        index=False,
    )

    order_items_base_df.to_csv(
        OUTPUT_DIR / "order_items_base.csv",
        index=False,
    )

    # ---------------------------------------------------------
    # SAVE DIRTY / MIGRATION DATA
    # ---------------------------------------------------------

    customers_dirty_df.to_csv(
        OUTPUT_DIR / "customers_dirty.csv",
        index=False,
    )

    products_dirty_df.to_csv(
        OUTPUT_DIR / "products_dirty.csv",
        index=False,
    )

    orders_dirty_df.to_csv(
        OUTPUT_DIR / "orders_dirty.csv",
        index=False,
    )

    order_items_dirty_df.to_csv(
        OUTPUT_DIR / "order_items_dirty.csv",
        index=False,
    )

    # ---------------------------------------------------------
    # SUMMARY
    # ---------------------------------------------------------

    print()
    print("Company B data generated successfully.")
    print("-" * 50)

    print(f"Base customers:      {len(customers_base_df):,}")
    print(f"Dirty customers:     {len(customers_dirty_df):,}")

    print(f"Base products:       {len(products_base_df):,}")
    print(f"Dirty products:      {len(products_dirty_df):,}")

    print(f"Base orders:         {len(orders_base_df):,}")
    print(f"Dirty orders:        {len(orders_dirty_df):,}")

    print(
        f"Base order items:    "
        f"{len(order_items_base_df):,}"
    )

    print(
        f"Dirty order items:   "
        f"{len(order_items_dirty_df):,}"
    )