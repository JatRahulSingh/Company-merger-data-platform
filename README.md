# Company Merger Data Platform

An end-to-end **Data Engineering + Analytics + AI** project that simulates the acquisition of one retail company by another and builds a unified analytics platform using:

- AWS S3
- Azure Databricks
- Apache Spark / PySpark
- Delta Lake
- Medallion Architecture
- Unity Catalog
- Power BI
- Python
- Ollama
- Qwen2.5-Coder
- SQLGlot
- Pytest

The project covers the complete lifecycle from raw source-system ingestion to data cleaning, entity resolution, dimensional modeling, business intelligence, and a local AI analytics assistant capable of querying the Gold layer using natural language.

---

# Project Overview

The project simulates a realistic company-merger scenario.

**Company A** is an established electronics retailer with relatively clean data.

**Company B** is acquired by Company A and has historical data containing inconsistencies such as:

- Duplicate customers
- Duplicate products
- Invalid emails
- Inconsistent city names
- Different date formats
- Invalid quantities
- Orphan foreign keys
- Product naming differences
- Different status values
- Different payment-method values
- Price formatting issues

The goal is to build a unified data platform that:

1. Ingests data from both companies.
2. Preserves raw source data.
3. Cleans and validates corrupted records.
4. Quarantines invalid records.
5. Resolves overlapping products between both companies.
6. Builds a canonical merged dataset.
7. Creates analytics-ready Gold tables.
8. Visualizes business performance in Power BI.
9. Allows users to query the data using natural language through a local LLM.

---

# Architecture

```text
                    COMPANY A                       COMPANY B
                        |                               |
                        |                               |
                    CSV Files                      Legacy CSV Files
                        |                               |
                        +---------------+---------------+
                                        |
                                        v
                                  AWS S3 Data Lake
                                        |
                                        v
                               Databricks Auto Loader
                                        |
                                        v
                                      BRONZE
                             Raw Source Preservation
                                        |
                        +---------------+---------------+
                        |                               |
                        v                               v
                 Company A Silver                Company B Silver
                   Clean/Trusted              Clean + Standardize
                                                    |
                                                    v
                                                Quarantine
                                                    |
                                                    v
                                          Entity Resolution
                                                    |
                                                    v
                                        Canonical Product Mapping
                                                    |
                        +---------------------------+
                        |
                        v
                                       GOLD LAYER
                              Dimensional Data Model
                        |
            +-----------+------------------+
            |                              |
            v                              v
        Power BI                  AI Analytics Assistant
                                         |
                                         v
                                      Ollama
                                         |
                                         v
                                   SQL Generator
                                         |
                                         v
                                   SQL Validator
                                         |
                                         v
                              Databricks SQL Warehouse
```

---

# Technology Stack

| Layer | Technology |
|---|---|
| Source Generation | Python, Pandas, Faker |
| Cloud Storage | AWS S3 |
| Data Processing | Databricks |
| Processing Engine | Apache Spark / PySpark |
| Storage Format | Delta Lake |
| Data Governance | Unity Catalog |
| Ingestion | Databricks Auto Loader |
| Architecture | Bronze / Silver / Gold |
| BI | Power BI |
| Local AI | Ollama |
| LLM | Qwen2.5-Coder 3B |
| SQL Validation | SQLGlot |
| Databricks Connectivity | Databricks SQL Connector |
| Authentication | Databricks CLI OAuth |
| Configuration | python-dotenv |
| Testing | Pytest |
| Version Control | Git + GitHub |

---

# Data Sources

## Company A

Company A represents the established organization.

The generated source data contains approximately:

- 10,000 customers
- 200 products
- 60,000 orders
- 149,000+ order items

The source follows a relatively clean schema.

### Customers

```text
customer_id
customer_name
email
city
state
signup_date
```

### Products

```text
product_id
product_name
category
unit_price
```

### Orders

```text
order_id
customer_id
order_date
order_status
payment_method
```

### Order Items

```text
order_item_id
order_id
product_id
quantity
unit_price
discount_pct
```

---

# Company B

Company B represents the acquired organization.

The source contains intentionally inconsistent historical data.

Approximate source volume:

- 2,550 customer records
- 105 product records
- 15,000 orders
- 37,000+ order items

Examples of intentionally introduced data-quality problems include:

```text
Duplicate customer records
Duplicate product records
Invalid email addresses
Missing values
Inconsistent date formats
Invalid product references
Invalid customer references
Invalid quantities
Different category formats
Different order status values
Different payment-method formats
```

This allows the project to demonstrate realistic data-quality engineering.

---

# Medallion Architecture

The Databricks implementation follows the Medallion Architecture.

```text
Raw Files
   |
   v
BRONZE
   |
   v
SILVER
   |
   v
GOLD
```

---

# Bronze Layer

The Bronze layer preserves the source data with minimal transformation.

Databricks Auto Loader is used for incremental ingestion.

Additional metadata columns are added:

```text
_source_system
_source_file
_source_path
_file_modification_time
_ingested_at
```

Bronze tables retain source-system values so that the original data remains traceable.

---

# Silver Layer

The Silver layer performs:

- Data type conversion
- Date parsing
- Email validation
- Standardization
- Deduplication
- Foreign-key validation
- Category normalization
- Order-status normalization
- Payment-method normalization
- Quarantine handling

Invalid records are not silently discarded.

Instead they are written to dedicated quarantine tables with a reason explaining why each record failed validation.

Example quarantine reasons include:

```text
INVALID_EMAIL
INVALID_ORDER_DATE
INVALID_CUSTOMER_REFERENCE
INVALID_PRODUCT_REFERENCE
INVALID_QUANTITY
INVALID_PRICE
```

---

# Data Quarantine

A major design principle in this project is:

> Bad data should be explainable, traceable, and recoverable.

Instead of simply dropping invalid records, they are stored separately.

Example:

```text
Raw Company B Orders
        |
        v
Validation Rules
    /        \
 Valid      Invalid
   |           |
   v           v
Silver     Quarantine
```

This allows bad records to be investigated or repaired later.

---

# Entity Resolution

One of the most important parts of the merger is identifying Company B products that already exist in Company A.

Company B contains:

- Products that already exist in Company A
- New products that do not exist in Company A

The entity-resolution logic compares normalized product attributes.

The initial matching process produced ambiguous matches for some products.

Those cases were resolved using:

```text
Category Match
+
Minimum Price Difference
```

A deterministic window function selects the best match.

Final result:

```text
70 Company B products matched existing Company A products
30 Company B products identified as new products
```

A product crosswalk table is created:

```text
workspace.silver.product_crosswalk
```

Example:

```text
company_b_product_id
company_b_product_name
company_a_product_id
company_a_product_name
match_type
canonical_product_id
```

Match types include:

```text
MATCHED_EXISTING_PRODUCT
NEW_PRODUCT
```

---

# Canonical Product Model

Existing Company B products reuse the canonical Company A product ID.

New Company B products receive deterministic IDs.

Example:

```text
BNEW_<company_b_product_id>
```

The final unified product master contains approximately:

```text
230 canonical products
```

---

# Gold Layer

The Gold layer contains analytics-ready dimensional models.

Main tables:

```text
workspace.gold.dim_customer

workspace.gold.dim_product

workspace.gold.fact_sales
```

---

# Customer Dimension

`dim_customer` contains canonical customer IDs.

Example:

```text
A_C001234
B_B-C00123
```

Important columns include:

```text
customer_id
source_customer_id
customer_name
email
city
state
signup_date
source_system
```

---

# Product Dimension

`dim_product` contains the canonical product master after entity resolution.

Important columns:

```text
product_id
product_name
category
catalog_unit_price
source_system
```

---

# Sales Fact Table

`fact_sales` is built at the order-item grain.

It contains approximately:

```text
184,852 rows
```

Important columns include:

```text
order_item_id
order_id
customer_id
product_id
order_date
order_status
payment_method
quantity
unit_price
discount_pct
gross_amount
discount_amount
net_amount
recognized_revenue
source_system
```

---

# Revenue Logic

Revenue is defined using:

```text
recognized_revenue
```

Business rule:

```text
Completed Order
    recognized_revenue = net_amount

Cancelled Order
    recognized_revenue = 0

Returned Order
    recognized_revenue = 0
```

This business rule is also enforced inside the AI analytics layer.

---

# Gold KPI Tables

Additional Gold KPI tables include:

```text
workspace.gold.kpi_monthly_sales

workspace.gold.kpi_category_performance

workspace.gold.kpi_product_performance

workspace.gold.kpi_company_comparison

workspace.gold.kpi_customer_performance
```

These support business reporting and Power BI analysis.

---

# Power BI Dashboard

The Gold layer is connected to Power BI through the Databricks SQL Warehouse.

The dashboard contains four pages.

## 1. Executive Sales Overview

Includes:

- Total Revenue
- Total Orders
- Average Order Value
- Total Customers
- Monthly Revenue Trend
- Revenue by Company
- Revenue by Category
- Order Status Breakdown

---

## 2. Product & Category Analysis

Includes:

- Top Products by Revenue
- Top Products by Units Sold
- Revenue by Category
- Units Sold by Category
- Category filters
- Company filters

---

## 3. Customer & Regional Analysis

Includes:

- Top Customers by Revenue
- Revenue by State
- Customers by State
- Top Cities by Revenue
- State filters
- Company filters

---

## 4. Merger Performance Comparison

Includes:

- Monthly Revenue by Company
- Revenue comparison
- Order comparison
- Average Order Value comparison
- Order Status Mix by Company

---

# AI Analytics Assistant

The project also includes a local AI analytics assistant.

The assistant allows users to ask business questions using plain English.

Example:

```text
Which product category generated the highest total revenue?
```

The assistant converts this into SQL:

```sql
SELECT
    dp.category,
    SUM(fs.recognized_revenue) AS total_revenue
FROM workspace.gold.fact_sales fs
JOIN workspace.gold.dim_product dp
    ON fs.product_id = dp.product_id
GROUP BY dp.category
ORDER BY total_revenue DESC
LIMIT 1;
```

The SQL is validated before execution.

Databricks returns the actual result.

The assistant then produces a natural-language response such as:

```text
Laptops generated the highest total revenue,
at approximately ₹2.89 billion.
```

---

# AI Architecture

```text
User Question
      |
      v
Local Ollama LLM
      |
      v
SQL Generator
      |
      v
SQL Validator
      |
      v
Databricks SQL Warehouse
      |
      v
Gold Tables
      |
      v
Query Result
      |
      v
Python Result Formatter
      |
      v
Ollama Answer Generator
      |
      v
Natural-Language Answer
```

The LLM never directly controls the database.

It only proposes SQL.

Python validates the SQL before Databricks receives it.

---

# AI Safety Layer

LLM-generated SQL is treated as untrusted input.

The SQL validator enforces several rules.

## SELECT-Only

Queries such as:

```sql
DELETE
UPDATE
INSERT
DROP
ALTER
CREATE
```

are rejected.

---

## Single Statement

Multiple SQL statements are rejected.

Example:

```sql
SELECT * FROM workspace.gold.fact_sales;

DROP TABLE workspace.gold.fact_sales;
```

is blocked.

---

## Gold Table Allowlist

The AI assistant can only access:

```text
workspace.gold.fact_sales
workspace.gold.dim_product
workspace.gold.dim_customer
```

Bronze and Silver tables are blocked.

---

## Fully Qualified Table Names

The LLM must use full Databricks table names.

Correct:

```sql
workspace.gold.fact_sales
```

Incorrect:

```sql
fact_sales
```

---

## Revenue Business Rule

Revenue questions must use:

```text
recognized_revenue
```

Queries attempting to use:

```text
net_amount
gross_amount
unit_price
discount_amount
```

as business revenue are rejected.

---

# Customer Semantic Rules

The assistant distinguishes between:

```text
All customers
```

and:

```text
Customers who actually purchased
```

For example:

```text
How many customers are there in Company B?
```

uses:

```text
workspace.gold.dim_customer
```

while:

```text
How many Company B customers placed orders?
```

uses:

```text
workspace.gold.fact_sales
```

This prevents technically valid but semantically incorrect SQL.

---

# Result-Size Protection

Detail queries must include a limit.

The maximum allowed result size is:

```text
50 rows
```

For example:

```text
Show me every sales record
```

is rejected.

The assistant instead asks the user to request a smaller sample.

Example:

```text
Show me 20 sales records
```

---

# Defense in Depth

Two separate result-size protections are implemented.

```text
SQL Validator
      |
      | Prevents oversized queries
      v
Databricks
      |
      v
Analytics Engine
      |
      | Prevents >50 rows entering Python
      v
AI Answer Generator
```

This ensures accidental large queries cannot overwhelm the local application or LLM.

---

# Local LLM

The project uses:

```text
Ollama
+
qwen2.5-coder:3b
```

The model runs locally.

This keeps the AI component lightweight and avoids requiring external LLM API keys.

---

# Example AI Questions

The assistant can answer questions such as:

```text
Which product category generated the highest revenue?

What was the total revenue for Company A?

What was the total revenue for Company B?

How many distinct orders did Company A have?

Which product generated the most revenue?

Which state generated the highest revenue?

How many customers are there in Company B?

How many Company B customers placed orders?

Compare the revenue of Company A and Company B.

Show the top 5 product categories by revenue.

Show me 20 sales records.
```

---

# Example Results

Some example analytical results from the project include:

```text
Company A Revenue
≈ ₹6.36 billion

Company B Revenue
≈ ₹645.62 million

Highest Revenue Category
Laptops
≈ ₹2.89 billion

Company A Orders
60,000

Company B customers in customer master
2,500

Company B purchasing customers
2,302
```

---

# Automated Testing

The project includes automated tests using `pytest`.

The tests cover:

- SQL safety validation
- Revenue business rules
- Customer semantic rules
- Unauthorized tables
- Multiple statements
- Result limits
- Detail-query limits
- Local LLM SQL generation
- Databricks SQL connectivity

Current test result:

```text
18 passed
```

Run all tests using:

```bash
python -m pytest -v
```

---

# Project Structure

```text
company-merger-data-platform/
│
├── ai/
│   ├── __init__.py
│   ├── analytics_engine.py
│   ├── answer_generator.py
│   ├── chatbot.py
│   ├── query_validator.py
│   └── sql_generator.py
│
├── tests/
│   ├── test_ai_query_pipeline.py
│   ├── test_analytics_engine.py
│   ├── test_query_validator.py
│   └── test_sql_generator.py
│
├── scripts/
│   ├── check_databricks_connection.py
│   └── check_ollama.py
│
├── src/
│   └── data_generation/
│       ├── generate_company_a.py
│       ├── generate_company_b.py
│       ├── prepare_source_files.py
│       ├── validate_company_a.py
│       ├── validate_company_b.py
│       └── validate_source_delivery.py
│
├── notebooks/
│   ├── 00_environment_test.ipynb
│   ├── 02_bronze_company_a.ipynb
│   ├── 03_bronze_company_b.ipynb
│   ├── 04_silver_company_a.ipynb
│   ├── 05_silver_company_b.ipynb
│   ├── 06_entity_resolution.ipynb
│   └── 07_gold_model.ipynb
│
├── dashboard/
│   └── company_merger_dashboard.pbix
│
├── data_samples/
├── docs/
├── configs/
│
├── pytest.ini
├── requirements.txt
├── .gitignore
└── README.md
```

---

# Local Setup

## 1. Clone the repository

```bash
git clone https://github.com/JatRahulSingh/Company-merger-data-platform.git
```

```bash
cd Company-merger-data-platform
```

---

## 2. Create a virtual environment

Windows:

```bash
python -m venv .venv
```

Activate:

```bash
.venv\Scripts\activate
```

---

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

# Ollama Setup

Install Ollama and download the model:

```bash
ollama pull qwen2.5-coder:3b
```

Verify:

```bash
ollama list
```

Test Ollama:

```bash
python scripts/check_ollama.py
```

---

# Databricks Authentication

The project uses Databricks CLI OAuth authentication.

Authenticate using:

```bash
databricks auth login \
  --host https://<your-databricks-workspace> \
  --profile company-merger
```

This stores authentication securely outside the repository.

No Databricks access token is committed to GitHub.

---

# Environment Configuration

Create a local `.env` file in the repository root:

```env
DATABRICKS_PROFILE=company-merger
DATABRICKS_HTTP_PATH=<your-sql-warehouse-http-path>
```

`.env` is excluded from Git using `.gitignore`.

Never commit credentials or access tokens.

---

# Test Databricks Connectivity

Run:

```bash
python scripts/check_databricks_connection.py
```

---

# Run the AI Assistant

From the repository root:

```bash
python -m ai.chatbot
```

Example:

```text
COMPANY MERGER ANALYTICS ASSISTANT

Ask questions about sales, customers, products, and companies.
Type 'exit' to close the assistant.

You: Which category had the highest revenue?

Assistant:
Laptops had the highest revenue, at ₹2.89 billion.
```

---

# Run Automated Tests

```bash
python -m pytest -v
```

Expected result:

```text
18 passed
```

---

# Key Engineering Concepts Demonstrated

This project demonstrates:

- Cloud data lake architecture
- Batch ingestion
- Databricks Auto Loader
- Spark transformations
- Delta Lake
- Medallion architecture
- Data-quality validation
- Quarantine patterns
- Referential-integrity checks
- Entity resolution
- Canonical master-data mapping
- Dimensional modeling
- Star schema design
- Power BI analytics
- Databricks SQL Warehouse
- OAuth authentication
- Local LLM integration
- Natural-language-to-SQL
- LLM guardrails
- SQL AST parsing
- Business-semantic validation
- Defense-in-depth security
- Automated testing
- Git-based project organization

---

# Important Design Principle

The LLM is **not the source of truth**.

```text
LLM
→ understands language

Python
→ enforces rules

Databricks
→ provides facts
```

The assistant generates SQL, but the actual business result always comes from the Databricks Gold layer.

---

# Future Improvements

Potential future enhancements include:

- Web-based chatbot UI
- Streamlit interface
- Conversation memory
- Additional Gold KPI tables
- Semantic model layer
- More advanced entity-resolution algorithms
- Embedding-based product matching
- Role-based AI access
- Read-only Databricks service principal
- Query logging and observability
- SQL execution timeout controls
- Cost monitoring
- CI/CD pipeline
- GitHub Actions automated tests
- Automated deployment
- Larger local or hosted LLM support

---

# Project Status

```text
Data Generation             ✅
AWS S3 Data Lake            ✅
Bronze Layer                ✅
Silver Layer                ✅
Quarantine                  ✅
Entity Resolution           ✅
Canonical Product Mapping   ✅
Gold Star Schema            ✅
Gold KPI Tables             ✅
Power BI Dashboard          ✅
Databricks SQL Integration  ✅
Local LLM Integration       ✅
SQL Safety Validator        ✅
AI Analytics Assistant      ✅
Automated Tests             ✅
```

---

# Author

**Rahul**

Data Engineering / Analytics / AI Portfolio Project

---

# License

This project was created for educational and portfolio purposes.
