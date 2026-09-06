# Data Generation Plan

## Timeline

### Company A

Historical period:

January 2024 to December 2025.

Company A represents the primary organization and provides regular monthly source files.

### Company B

Historical period:

January 2025 to December 2025.

Company B represents the acquired organization.

Acquisition effective date:

July 1, 2025.

Historical Company B data will be migrated and integrated into the enterprise analytics platform.

---

## Approximate Data Volume

| Entity | Company A | Company B |
|---|---:|---:|
| Customers | 10,000 | 2,500 |
| Products | 200 | ~100 |
| Orders | 60,000 | 15,000 |
| Order Items | 120,000-180,000 | 30,000-45,000 |

---

## Company A File Delivery

Company A provides regular monthly data files.

Example:

orders_2025_01.csv  
orders_2025_02.csv  
orders_2025_03.csv

This will allow the platform to demonstrate incremental ingestion.

---

## Company B File Delivery

Company B provides legacy migration files during the acquisition.

Examples:

customers_legacy.csv  
products_legacy.csv  
orders_2025_H1.csv  
orders_2025_H2.csv  
order_items_2025_H1.csv  
order_items_2025_H2.csv

These datasets intentionally contain schema differences and data-quality problems.

---

## Product Overlap

A subset of Company B products represents the same real-world products already sold by Company A but uses different product IDs and naming conventions.

Example:

Company A:

P001 | Laptop Pro 15

Company B:

B101 | laptop pro15

These records must eventually map to the same enterprise product.

Company B will also contain genuinely new products that do not exist in Company A.

---

## Project Objective

The generated datasets must support:

- Incremental ingestion
- Medallion Architecture
- Data-quality validation
- Quarantine handling
- Entity resolution
- Company merger analytics
- Power BI reporting
- Natural-language analytics using a local LLM