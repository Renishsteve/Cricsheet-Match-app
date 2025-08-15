import os
import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import argparse

def create_chart(query_name, query_result, out_dir):
    df = pd.DataFrame(query_result)
    if df.empty:
        print(f"No data for {query_name}")
        return

    plt.figure(figsize=(10, 6))
    sns.barplot(x=df.iloc[:, 0], y=df.iloc[:, 1])
    plt.xticks(rotation=45, ha='right')
    plt.title(query_name)
    plt.tight_layout()

    safe_name = "".join(c if c.isalnum() else "_" for c in query_name)
    file_path = os.path.join(out_dir, f"{safe_name}.png")
    plt.savefig(file_path)
    plt.close()
    print(f"✅ Saved chart: {file_path}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sql-results-file", required=True, help="Path to sql_results.json")
    parser.add_argument("--out-dir", required=True, help="Directory to save figures")
    args = parser.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)

    with open(args.sql_results_file, "r", encoding="utf-8") as f:
        sql_results = json.load(f)

    if isinstance(sql_results, dict):
        for query_name, query_result in sql_results.items():
            create_chart(query_name, query_result, args.out_dir)
    elif isinstance(sql_results, list):
        for entry in sql_results:
            create_chart(entry.get("query", "Unnamed Query"), entry.get("result", []), args.out_dir)
    else:
        print("❌ Unsupported sql_results format")

if __name__ == "__main__":
    main()