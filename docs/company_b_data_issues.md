# Company B Data Issues

Company B is the acquired company. Its source data differs from Company A in both schema design and data quality.

The objective is to standardize Company B data before integrating it into the unified analytical model.

---

## 1. Customers

Company B source columns:

| Column | Data Type | Notes |
|---|---|---|
| cust_code | STRING | Customer identifier |
| full_name | STRING | Customer name |
| email_address | STRING | Email |
| location | STRING | City |
| state_name | STRING | State |
| registered_on | STRING | Signup date stored as text |

### Mapping to Company A

| Company B | Company A |
|---|---|
| cust_code | customer_id |
| full_name | customer_name |
| email_address | email |
| location | city |
| state_name | state |
| registered_on | signup_date |

### Data Quality Problems

- Duplicate customers
- Missing email addresses
- Invalid email formats
- City names such as `Bangalore`, `Bengaluru`, `BLR`
- State names with inconsistent casing
- Signup dates stored in multiple formats

---

## 2. Products

Company B source columns:

| Column | Data Type | Notes |
|---|---|---|
| prd_code | STRING | Product identifier |
| prd_nm | STRING | Product name |
| prd_category | STRING | Product category |
| selling_price | STRING | Price stored as text |

### Mapping to Company A

| Company B | Company A |
|---|---|
| prd_code | product_id |
| prd_nm | product_name |
| prd_category | category |
| selling_price | unit_price |

### Data Quality Problems

- Different product IDs from Company A
- Product-name variations
- Category inconsistencies
- Prices stored like `₹75,000`, `75000`, `75K`
- Missing prices
- Duplicate product records

---

## 3. Orders

Company B source columns:

| Column | Data Type | Notes |
|---|---|---|
| txn_id | STRING | Order identifier |
| cust_code | STRING | Customer identifier |
| txn_date | STRING | Order date |
| txn_status | STRING | Order status |
| payment_type | STRING | Payment method |

### Mapping to Company A

| Company B | Company A |
|---|---|
| txn_id | order_id |
| cust_code | customer_id |
| txn_date | order_date |
| txn_status | order_status |
| payment_type | payment_method |

### Data Quality Problems

- Invalid dates
- Mixed date formats
- Unknown customer IDs
- Status values such as `complete`, `COMPLETED`, `done`
- Payment values such as `UPI`, `upi`, `GPay`

---

## 4. Order Items

Company B source columns:

| Column | Data Type | Notes |
|---|---|---|
| txn_line_id | STRING | Order item identifier |
| txn_id | STRING | Order identifier |
| prd_code | STRING | Product identifier |
| qty | STRING | Quantity |
| sale_price | STRING | Transaction price |
| discount | STRING | Discount percentage |

### Mapping to Company A

| Company B | Company A |
|---|---|
| txn_line_id | order_item_id |
| txn_id | order_id |
| prd_code | product_id |
| qty | quantity |
| sale_price | unit_price |
| discount | discount_pct |

### Data Quality Problems

- Quantity stored as text
- Negative or zero quantities
- Prices with currency symbols
- Discounts such as `10%`, `0.10`, `10`
- Orphan order items
- Invalid product IDs