import argparse
import pandas as pd
from sqlalchemy import create_engine

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv-prefix", required=True, help="Prefix for CSV files (without _matches.csv etc.)")
    parser.add_argument("--db", default="sqlite:///cricket.db", help="Database connection string")
    args = parser.parse_args()

    engine = create_engine(args.db)

    pd.read_csv(args.csv_prefix + "_matches.csv").to_sql("matches", engine, if_exists="replace", index=False)
    pd.read_csv(args.csv_prefix + "_innings.csv").to_sql("innings", engine, if_exists="replace", index=False)
    pd.read_csv(args.csv_prefix + "_deliveries.csv").to_sql("deliveries", engine, if_exists="replace", index=False)

    print("Data loaded into DB:", args.db)

if __name__ == "__main__":
    main()
