import argparse
import sqlite3
import json

def main():
    parser = argparse.ArgumentParser(description="Run SQL analyses")
    parser.add_argument("--db", required=True, help="Database connection string (e.g., sqlite:///file.db)")
    parser.add_argument("--sql-file", required=True, help="Path to .sql file containing queries")
    parser.add_argument("--out", required=True, help="Path to save JSON results")
    args = parser.parse_args()

    # Extract actual DB path from sqlite:///path
    db_path = args.db.replace("sqlite:///", "")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    with open(args.sql_file, "r", encoding="utf-8") as f:
        sql_content = f.read()

    # Split queries by semicolon, but keep only non-empty ones
    queries = [q.strip() for q in sql_content.split(";") if q.strip()]

    results = []
    for i, query in enumerate(queries, start=1):
        try:
            cursor.execute(query)
            rows = cursor.fetchall()
            cols = [desc[0] for desc in cursor.description] if cursor.description else []
            results.append({
                "query": f"Query {i}",
                "result": [dict(zip(cols, row)) for row in rows]
            })
            print(f"✅ Executed Query {i}")
        except Exception as e:
            print(f"❌ Error in Query {i}: {e}")

    conn.close()

    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4)

    print(f"Saved results to {args.out}")

if __name__ == "__main__":
    main()