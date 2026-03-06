# PhonePe Transaction Insights

A beginner-friendly data analysis project that extracts PhonePe Pulse data, loads it into MySQL, and visualizes it with an interactive Streamlit dashboard featuring India maps.

## Tech Stack

- **Python** — Data extraction & analysis
- **MySQL** — Database storage
- **Pandas** — DataFrames
- **Matplotlib** — Charts (bar, pie, line, area)
- **Plotly** — India choropleth maps
- **Streamlit** — Web dashboard

## Project Structure

```
PhonePe-Transaction-Insights/
├── pulse/                  # PhonePe Pulse data (cloned repo)
├── sql_queries/            # SQL queries organized by section
│   ├── 00_database_setup.sql
│   ├── 01_overview.sql
│   ├── 02_transaction_analysis.sql
│   ├── 03_user_analysis.sql
│   ├── 04_insurance_analysis.sql
│   ├── 05_top_charts.sql
│   └── 06_business_case_studies.sql
├── data_extractor.py       # Extracts JSON → DataFrames → MySQL
├── dashboard.py            # Streamlit dashboard
├── requirements.txt        # Python dependencies
└── README.md               # This file
```

## Setup Instructions

### Step 1: Create Virtual Environment

```bash
python -m venv .env
```

Activate it:

- **Windows**: `.env\Scripts\activate`
- **Mac/Linux**: `source .env/bin/activate`

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: MySQL Setup

Make sure MySQL is running on your machine. The project uses:

- **Host**: localhost
- **User**: root
- **Password**: pass@123

If your password is different, update it in `data_extractor.py` and `dashboard.py`.

### Step 4: Extract Data & Load into MySQL

```bash
python data_extractor.py
```

This will:
1. Create the `phonepe_pulse` database
2. Create 9 tables (aggregated, map, top — for transactions, users, insurance)
3. Build Pandas DataFrames from all JSON files
4. Load all data into MySQL

### Step 5: Run the Dashboard

```bash
streamlit run dashboard.py
```

Open `http://localhost:8501` in your browser.

## Dashboard Sections

| Section | Description |
|---------|-------------|
| **Overview** | Key metrics, India map, payment category breakdown |
| **Transaction Analysis** | Yearly/quarterly trends, payment types, top states |
| **User Analysis** | User map, device brands, brand trends |
| **Insurance Analysis** | Insurance map, trends, top states |
| **Top Charts** | Top 10 states & districts for all categories |
| **Business Case Studies** | 5 detailed case studies with insights |

## Business Case Studies Covered

1. **Decoding Transaction Dynamics** — Payment category trends & YoY growth
2. **Device Dominance & User Engagement** — Device brand analysis across states
3. **Insurance Penetration & Growth** — Insurance adoption trends
4. **Transaction Analysis for Market Expansion** — Identifying expansion targets
5. **User Engagement & Growth Strategy** — Engagement ratios & growth patterns

## SQL Queries

Queries are organized in the `sql_queries/` folder by dashboard section:

| File | Section |
|------|---------|
| `00_database_setup.sql` | CREATE DATABASE, 9 CREATE TABLE, TRUNCATE |
| `01_overview.sql` | Overview KPIs, India map, payment categories |
| `02_transaction_analysis.sql` | Transaction trends, payment types, top states |
| `03_user_analysis.sql` | User map, device brands, engagement |
| `04_insurance_analysis.sql` | Insurance map, trends, growth |
| `05_top_charts.sql` | Top 10 states & districts |
| `06_business_case_studies.sql` | All 5 case study queries |

Run them in MySQL Workbench or any MySQL client.

## Data Source

[PhonePe Pulse GitHub Repository](https://github.com/PhonePe/pulse)
