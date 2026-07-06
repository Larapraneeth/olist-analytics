"""Ingest Olist raw CSVs into a DuckDB warehouse using dlt.

Creates warehouse/olist.duckdb with all 9 tables in the `raw` schema.

Usage:
    python ingestion/ingest.py
    python ingestion/ingest.py --cleanup   (also deletes raw CSVs afterwards to save disk)
"""

import argparse
import sys
from pathlib import Path

import dlt
import pandas as pd

RAW_DIR = Path("data/raw")
WAREHOUSE_PATH = Path("warehouse/olist.duckdb")

# table_name -> source csv file
TABLES = {
    "orders": "olist_orders_dataset.csv",
    "order_items": "olist_order_items_dataset.csv",
    "customers": "olist_customers_dataset.csv",
    "products": "olist_products_dataset.csv",
    "sellers": "olist_sellers_dataset.csv",
    "order_payments": "olist_order_payments_dataset.csv",
    "order_reviews": "olist_order_reviews_dataset.csv",
    "geolocation": "olist_geolocation_dataset.csv",
    "product_category_translation": "product_category_name_translation.csv",
}

CHUNK_SIZE = 100_000  # stream large files in chunks to keep memory low


def make_resource(table_name: str, csv_path: Path):
    """Create a dlt resource that streams one CSV in chunks."""

    @dlt.resource(name=table_name, write_disposition="replace")
    def _resource():
        for chunk in pd.read_csv(csv_path, chunksize=CHUNK_SIZE):
            yield chunk

    return _resource


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--cleanup",
        action="store_true",
        help="Delete raw CSVs after successful load (saves ~120MB disk).",
    )
    args = parser.parse_args()

    missing = [f for f in TABLES.values() if not (RAW_DIR / f).exists()]
    if missing:
        print(f"ERROR: missing raw files: {missing}")
        print("Run:  python ingestion/download_data.py")
        sys.exit(1)

    WAREHOUSE_PATH.parent.mkdir(parents=True, exist_ok=True)

    pipeline = dlt.pipeline(
        pipeline_name="olist_ingestion",
        destination=dlt.destinations.duckdb(str(WAREHOUSE_PATH)),
        dataset_name="raw",
    )

    resources = [
        make_resource(name, RAW_DIR / filename)
        for name, filename in TABLES.items()
    ]

    load_info = pipeline.run(resources)
    print(load_info)

    if args.cleanup:
        for filename in TABLES.values():
            path = RAW_DIR / filename
            if path.exists():
                path.unlink()
        print("Raw CSVs deleted (re-download anytime with download_data.py).")

    print(f"\nDone. Warehouse ready at {WAREHOUSE_PATH}")


if __name__ == "__main__":
    main()
