# Source Data Model

## Company A

Company A is the primary organization. Its source data is relatively clean and follows a consistent schema.

---

## 1. Customers

| Column | Data Type | Description |
|---|---|---|
| customer_id | STRING | Unique identifier for each customer |
| customer_name | STRING | Full name of the customer |
| email | STRING | Customer email address |
| city | STRING | Customer city |
| state | STRING | Customer state |
| signup_date | DATE | Date the customer registered |

### Primary Key
`customer_id`

---

## 2. Products

| Column | Data Type | Description |
|---|---|---|
| product_id | STRING | Unique identifier for each product |
| product_name | STRING | Product name |
| category | STRING | Product category |
| unit_price | DECIMAL(10,2) | Standard selling price |

### Primary Key
`product_id`

---

## 3. Orders

| Column | Data Type | Description |
|---|---|---|
| order_id | STRING | Unique identifier for each order |
| customer_id | STRING | Customer who placed the order |
| order_date | DATE | Date the order was placed |
| order_status | STRING | Order status such as Completed, Cancelled or Returned |
| payment_method | STRING | Payment method used |

### Primary Key
`order_id`

### Foreign Key
`customer_id` → `customers.customer_id`

---

## 4. Order Items

| Column | Data Type | Description |
|---|---|---|
| order_item_id | STRING | Unique identifier for an order line |
| order_id | STRING | Order associated with the item |
| product_id | STRING | Product purchased |
| quantity | INTEGER | Number of units purchased |
| unit_price | DECIMAL(10,2) | Selling price at the time of the transaction |
| discount_pct | DECIMAL(5,2) | Discount percentage applied |

### Primary Key
`order_item_id`

### Foreign Keys
`order_id` → `orders.order_id`

`product_id` → `products.product_id`