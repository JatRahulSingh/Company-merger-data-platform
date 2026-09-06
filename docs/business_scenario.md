# Business Scenario

## Overview

Company A is an established electronics retail company that stores its transactional data in Amazon S3.

The objective is to build an analytics-ready data platform using Databricks, PySpark, Delta Lake, and Medallion Architecture.

Company A later acquires Company B, a smaller electronics retailer whose historical data contains multiple data-quality and schema-consistency issues.

The platform must clean, standardize, validate, and integrate Company B data with Company A data to create a unified analytical dataset.

## Source Entities

- Customers
- Products
- Orders
- Order Items

## Company A

Company A represents the primary organization.

Its source data is relatively clean and will be used to build the initial Bronze, Silver, and Gold layers.

## Company B

Company B represents the acquired organization.

Its data will intentionally contain realistic issues such as:

- Missing values
- Duplicate records
- Invalid dates
- Incorrect datatypes
- Inconsistent product names
- Different source-system IDs
- Inconsistent city and state names
- Invalid transaction amounts
- Orphan records
- Schema differences

## Target Architecture

Amazon S3 → Databricks Bronze → Silver → Gold

The Gold layer will power:

1. Power BI dashboards
2. A local LLM-based analytics assistant

## AI Analytics Assistant

Users will be able to ask natural-language business questions such as:

- What were total sales in December 2025?
- Which product generated the highest revenue?
- Which region had the strongest growth?
- What percentage of revenue came from the acquired company?