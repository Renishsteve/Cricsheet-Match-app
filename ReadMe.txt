📄 README:

🏏 Cricsheet Match Data Analysis Project

This project is an end-to-end cricket analytics pipeline that downloads real match data from Cricsheet, processes it, stores it in a database, runs analytical SQL queries, and generates visualizations — all in one click.


----------

📌 Prjct Summary:

1. Download JSON match files for multiple formats (Test, ODI, T20, IPL) using Selenium.


2. Transform raw JSON into structured CSV and Parquet files.


3. Load the processed data into a SQLite database.


4. Analyze the data by running 20 predefined SQL queries.


5. Visualize the results with automatic EDA charts.




---

📂 Project Structure

Cricsheet-match-app/
│
├── scrapper.py               # Downloads JSON match data into data/raw
├── transform_json.py         # Converts JSON to CSV/Parquet
├── load_to_db.py              # Loads CSV data into SQLite DB
├── run_sql_analyses.py        # Runs queries.sql and saves results to sql_results.json
├── eda.py                     # Creates charts from sql_results.json
├── run_all.py                 # Master script to run everything in sequence
├── queries.sql                # List of 20 SQL queries for analysis
│
├── data/
│   ├── raw/                   # Downloaded JSON files
│   └── processed/             # Flattened CSV and Parquet files
│
├── cricket.db                 # SQLite database (created after loading)
├── sql_results.json           # Results of SQL queries
├── figures/                   # Generated charts
│
└── README.md                  # This file


---

⚙️ Requirements



pip install pandas matplotlib seaborn sqlalchemy selenium


---

🚀 Run Procedure:



The easiest way to run everything is with:

python run_all.py

This will do as below:-

1. Step 0: Scrape latest match data (scrapper.py)


2. Step 1: Transform JSON → CSV/Parquet (transform_json.py)


3. Step 2: Load CSV into SQLite database (load_to_db.py)


4. Step 3: Run all SQL queries (run_sql_analyses.py)


5. Step 4: Wait for sql_results.json to be ready


6. Step 5: Generate visualizations (eda.py)




---

Run Steps Manually

If you want to run each step individually:

# Step 0: Scrape data
python scrapper.py

# Step 1: Transform JSONs
python transform_json.py --input-dir data/raw --output data/processed/flattened.parquet --also-csv

# Step 2: Load into DB
python load_to_db.py --csv-prefix data/processed/flattened --db sqlite:///cricket.db

# Step 3: Run SQL analyses
python run_sql_analyses.py --db sqlite:///cricket.db --sql-file queries.sql --out sql_results.json

# Step 4: Generate EDA plots
python eda.py --sql-results-file sql_results.json --out-dir figures


---

📊 Output

sql_results.json — Stores the output of all SQL queries in JSON format.

figures/ — Contains .png charts for each query.

cricket.db — SQLite database with cleaned cricket match data.