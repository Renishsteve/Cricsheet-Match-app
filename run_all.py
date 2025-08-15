import subprocess
import os
import sys
import time

# Directory where run_all.py is located (Cricsheet-match-app)
APP_DIR = os.path.dirname(os.path.abspath(__file__))
SQL_RESULTS_PATH = os.path.join(APP_DIR, "sql_results.json")
FIGURES_DIR = os.path.join(APP_DIR, "figures")

print(f"📂 Running pipeline from: {APP_DIR}")

steps = [
    [sys.executable, "scrapper.py"],
    [sys.executable, "transform_json.py",
        "--input-dir", "data/raw",
        "--output", "data/processed/flattened.parquet",
        "--also-csv"],
    [sys.executable, "load_to_db.py",
        "--csv-prefix", "data/processed/flattened",
        "--db", "sqlite:///cricket.db"],
    [sys.executable, "run_sql_analyses.py",
        "--db", "sqlite:///cricket.db",
        "--sql-file", "queries.sql",
        "--out", SQL_RESULTS_PATH],
    "WAIT_FOR_SQL_RESULTS",
    [sys.executable, "eda.py",
        "--sql-results-file", SQL_RESULTS_PATH,
        "--out-dir", FIGURES_DIR]
]

for cmd in steps:
    if cmd == "WAIT_FOR_SQL_RESULTS":
        print(f"\n⏳ Waiting for {SQL_RESULTS_PATH} to be ready...")
        for _ in range(30):  # wait up to 30s
            if os.path.exists(SQL_RESULTS_PATH) and os.path.getsize(SQL_RESULTS_PATH) > 0:
                print("✅ sql_results.json is ready!")
                break
            time.sleep(1)
        else:
            print("❌ sql_results.json was not created in time!")
            sys.exit(1)
        continue

    print(f"\n▶ Running: {' '.join(str(c) for c in cmd)}")
    result = subprocess.run(cmd, cwd=APP_DIR)
    if result.returncode != 0:
        print(f"❌ Step failed: {' '.join(str(c) for c in cmd)}")
        sys.exit(1)
    print(f"✅ Finished: {cmd[1]}")

print("\n🎯 Pipeline execution finished successfully!")