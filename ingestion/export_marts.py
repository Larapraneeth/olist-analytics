"""Export mart tables from DuckDB to CSVs for Power BI."""

from pathlib import Path

import duckdb

EXPORT_DIR = Path("exports")
MARTS = ["fct_orders"]  # add dim_customers, fct_order_payments as we build them


def main() -> None:
    EXPORT_DIR.mkdir(exist_ok=True)
    con = duckdb.connect("warehouse/olist.duckdb", read_only=True)
    for table in MARTS:
        out = EXPORT_DIR / f"{table}.csv"
        con.sql(f"copy main_marts.{table} to '{out.as_posix()}' (header, delimiter ',')")
        print(f"exported {out}")


if __name__ == "__main__":
    main()