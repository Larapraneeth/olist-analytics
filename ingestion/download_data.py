"""Download the Olist dataset from Kaggle into data/raw/.

Requires Kaggle credentials, either as:
  - ~/.kaggle/kaggle.json  (local development), or
  - KAGGLE_USERNAME / KAGGLE_KEY environment variables (CI).

Usage:
    python ingestion/download_data.py
"""

import subprocess
import sys
from pathlib import Path

DATASET = "olistbr/brazilian-ecommerce"
RAW_DIR = Path("data/raw")

EXPECTED_FILES = [
    "olist_orders_dataset.csv",
    "olist_order_items_dataset.csv",
    "olist_customers_dataset.csv",
    "olist_products_dataset.csv",
    "olist_sellers_dataset.csv",
    "olist_order_payments_dataset.csv",
    "olist_order_reviews_dataset.csv",
    "olist_geolocation_dataset.csv",
    "product_category_name_translation.csv",
]


def main() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    # Skip the download if every file is already present.
    if all((RAW_DIR / f).exists() for f in EXPECTED_FILES):
        print("All raw files already present, skipping download.")
        return

    print(f"Downloading {DATASET} into {RAW_DIR} ...")
    subprocess.run(
        [
            "kaggle", "datasets", "download",
            "-d", DATASET,
            "-p", str(RAW_DIR),
            "--unzip",
        ],
        check=True,
    )

    missing = [f for f in EXPECTED_FILES if not (RAW_DIR / f).exists()]
    if missing:
        print(f"ERROR: download finished but files are missing: {missing}")
        sys.exit(1)

    print("Download complete.")


if __name__ == "__main__":
    main()
