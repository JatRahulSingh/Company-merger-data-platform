import random
from pathlib import Path
from datetime import date

import numpy as np
import pandas as pd
from faker import Faker


SEED = 42

random.seed(SEED)
np.random.seed(SEED)
fake = Faker("en_IN")
Faker.seed(SEED)


OUTPUT_DIR = Path("data_samples/company_a_generated")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def generate_products(n_products: int = 200) -> pd.DataFrame:
    categories = {
        "Laptops": [
            "Laptop Pro",
            "UltraBook",
            "Gaming Laptop",
            "Business Laptop",
        ],
        "Smartphones": [
            "Smartphone X",
            "Smartphone Pro",
            "Smartphone Lite",
            "Smartphone Max",
        ],
        "Accessories": [
            "Wireless Headphones",
            "Mechanical Keyboard",
            "Gaming Mouse",
            "USB-C Hub",
        ],
        "Wearables": [
            "Smart Watch",
            "Fitness Band",
            "Wireless Earbuds",
        ],
        "Monitors": [
            "Gaming Monitor",
            "4K Monitor",
            "Office Monitor",
        ],
    }

    rows = []

    product_id = 1

    while len(rows) < n_products:
        category = random.choice(list(categories.keys()))
        base_name = random.choice(categories[category])

        model_number = random.randint(100, 999)

        product_name = f"{base_name} {model_number}"

        if category == "Laptops":
            price = random.randint(45000, 150000)
        elif category == "Smartphones":
            price = random.randint(15000, 100000)
        elif category == "Accessories":
            price = random.randint(500, 15000)
        elif category == "Wearables":
            price = random.randint(1500, 30000)
        else:
            price = random.randint(8000, 70000)

        rows.append(
            {
                "product_id": f"P{product_id:04d}",
                "product_name": product_name,
                "category": category,
                "unit_price": float(price),
            }
        )

        product_id += 1

    return pd.DataFrame(rows)


def generate_customers(n_customers: int = 10_000) -> pd.DataFrame:
    cities = {
        "Maharashtra": ["Mumbai", "Pune", "Nagpur"],
        "Karnataka": ["Bengaluru", "Mysuru", "Mangaluru"],
        "Rajasthan": ["Jaipur", "Jodhpur", "Udaipur"],
        "Delhi": ["New Delhi"],
        "Telangana": ["Hyderabad", "Warangal"],
        "Tamil Nadu": ["Chennai", "Coimbatore"],
        "Andhra Pradesh": ["Visakhapatnam", "Vijayawada"],
        "Gujarat": ["Ahmedabad", "Surat"],
    }

    start_date = date(2023, 1, 1)
    end_date = date(2025, 12, 31)

    rows = []

    for i in range(1, n_customers + 1):
        state = random.choice(list(cities.keys()))
        city = random.choice(cities[state])

        rows.append(
            {
                "customer_id": f"C{i:06d}",
                "customer_name": fake.name(),
                "email": fake.email(),
                "city": city,
                "state": state,
                "signup_date": fake.date_between(
                    start_date=start_date,
                    end_date=end_date,
                ),
            }
        )

    return pd.DataFrame(rows)

def generate_orders(
    customers_df: pd.DataFrame,
    n_orders: int = 60_000,
) -> pd.DataFrame:

    start_date = date(2024, 1, 1)
    end_date = date(2025, 12, 31)

    statuses = [
        "Completed",
        "Completed",
        "Completed",
        "Completed",
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

    customers = customers_df.copy()

    customers["signup_date"] = pd.to_datetime(
        customers["signup_date"]
    ).dt.date

    rows = []

    for i in range(1, n_orders + 1):

        order_date = fake.date_between(
            start_date=start_date,
            end_date=end_date,
        )

        # Pick only a customer who already existed
        while True:
            customer = customers.sample(1).iloc[0]

            if customer["signup_date"] <= order_date:
                break

        rows.append(
            {
                "order_id": f"O{i:07d}",
                "customer_id": customer["customer_id"],
                "order_date": order_date,
                "order_status": random.choice(statuses),
                "payment_method": random.choice(payment_methods),
            }
        )

    return pd.DataFrame(rows)


def generate_order_items(
    orders_df: pd.DataFrame,
    products_df: pd.DataFrame,
) -> pd.DataFrame:

    rows = []

    order_item_counter = 1

    for _, order in orders_df.iterrows():

        # Each order contains between 1 and 4 products
        number_of_items = random.randint(1, 4)

        selected_products = products_df.sample(
            n=number_of_items,
            replace=False,
        )

        for _, product in selected_products.iterrows():

            quantity = random.choices(
                population=[1, 2, 3, 4],
                weights=[70, 20, 8, 2],
                k=1,
            )[0]

            discount_pct = random.choices(
                population=[0, 5, 10, 15, 20],
                weights=[60, 15, 15, 7, 3],
                k=1,
            )[0]

            # Simulate transaction price varying slightly
            # from current catalogue price
            price_variation = random.uniform(0.90, 1.05)

            transaction_price = round(
                product["unit_price"] * price_variation,
                2,
            )

            rows.append(
                {
                    "order_item_id": f"OI{order_item_counter:08d}",
                    "order_id": order["order_id"],
                    "product_id": product["product_id"],
                    "quantity": quantity,
                    "unit_price": transaction_price,
                    "discount_pct": float(discount_pct),
                }
            )

            order_item_counter += 1

    return pd.DataFrame(rows)

if __name__ == "__main__":

    print("Generating Company A data...")

    products_df = generate_products()
    customers_df = generate_customers()

    print("Generating orders...")
    orders_df = generate_orders(customers_df)

    print("Generating order items...")
    order_items_df = generate_order_items(
        orders_df,
        products_df,
    )

    products_df.to_csv(
        OUTPUT_DIR / "products.csv",
        index=False,
    )

    customers_df.to_csv(
        OUTPUT_DIR / "customers.csv",
        index=False,
    )

    orders_df.to_csv(
        OUTPUT_DIR / "orders.csv",
        index=False,
    )

    order_items_df.to_csv(
        OUTPUT_DIR / "order_items.csv",
        index=False,
    )

    print()
    print("Company A data generated successfully.")
    print(f"Products:    {len(products_df):,}")
    print(f"Customers:   {len(customers_df):,}")
    print(f"Orders:      {len(orders_df):,}")
    print(f"Order Items: {len(order_items_df):,}")