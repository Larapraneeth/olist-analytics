# Olist Analytics Platform

End-to-end analytics engineering project on the Olist Brazilian e-commerce dataset (100K orders, 9 relational tables), built on a modern open-source data stack.

```
Kaggle CSVs → dlt (ingestion) → DuckDB (warehouse) → dbt (models + tests) → dashboard
                                        ↑
              GitHub Actions CI/CD: tests block PRs, merges auto-deploy docs
```

## Stack

| Layer | Tool |
|---|---|
| Ingestion | dlt |
| Warehouse | DuckDB |
| Transformation + tests | dbt Core (dbt-duckdb) |
| SQL linting | sqlfluff |
| CI/CD | GitHub Actions |
| Docs / lineage | dbt docs, auto-published to GitHub Pages |

## Setup (Windows PowerShell)

```powershell
# 1. Create and activate a virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 2. Install dependencies
pip install -r requirements.txt

# 3. Kaggle credentials: place kaggle.json in C:\Users\<you>\.kaggle\
#    (Kaggle → Settings → API → Create New Token)

# 4. Download the dataset
python ingestion/download_data.py

# 5. Ingest into the DuckDB warehouse
python ingestion/ingest.py
#    add --cleanup to delete raw CSVs afterwards and save ~120MB disk

# 6. Build and test all dbt models
$env:DBT_PROFILES_DIR = "$PWD\dbt"
cd dbt
dbt build
cd ..
```

Expected result: `PASS=30 WARN=0 ERROR=0` — 4 models built, 26 data tests passed.

## Explore the warehouse

```powershell
python -c "import duckdb; con = duckdb.connect('warehouse/olist.duckdb'); print(con.sql('select order_status, count(*) as orders, round(sum(order_total),2) as revenue from main_marts.fct_orders group by 1 order by 2 desc'))"
```

## Project structure

```
olist-analytics/
├── .github/workflows/
│   ├── ci.yml            # PR: ingest → dbt build (tests) → sqlfluff lint
│   └── cd.yml            # main + daily cron: rebuild warehouse, publish dbt docs to Pages
├── ingestion/
│   ├── download_data.py  # Kaggle download (idempotent)
│   └── ingest.py         # dlt pipeline: 9 CSVs → DuckDB `raw` schema
├── dbt/
│   ├── models/staging/   # typed, renamed 1:1 views over raw + source tests
│   └── models/marts/     # fct_orders: order-grain revenue & delivery metrics
├── warehouse/            # olist.duckdb (gitignored)
└── data/raw/             # Kaggle CSVs (gitignored)
```

## CI/CD

- **CI (every pull request):** downloads data, rebuilds the warehouse from scratch, runs every dbt model and test, lints all SQL. Any failure blocks the merge.
- **CD (every merge to main + daily 02:30 UTC):** production rebuild, uploads the warehouse as a versioned artifact, generates dbt documentation (lineage graph included) and deploys it to GitHub Pages.

Required repo secrets: `KAGGLE_USERNAME`, `KAGGLE_KEY`.
Required repo setting: Settings → Pages → Source = **GitHub Actions**.

## Roadmap

- [ ] Marts: `dim_customers`, `dim_products`, `fct_order_payments`
- [ ] Cohort retention, RFM segmentation, delivery-SLA analysis
- [ ] Evidence.dev dashboard deployed alongside dbt docs
- [ ] Executive insight memo with quantified recommendations
