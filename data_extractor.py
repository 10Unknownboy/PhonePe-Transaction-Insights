"""
PhonePe Pulse — Data Extractor
Reads JSON files from pulse/data/ and inserts directly into MySQL.

Usage:  python data_extractor.py
"""

import os
import json
import mysql.connector

# Database Connection Settings
MYSQL_HOST     = "localhost"
MYSQL_USER     = "root"
MYSQL_PASSWORD = "pass@123"
MYSQL_DB       = "phonepe_pulse"

# Path to the cloned pulse repo data folder
DATA_PATH = os.path.join(os.path.dirname(__file__), "pulse", "data")

# All 9 tables in the database
ALL_TABLES = [
    "aggregated_transaction", "aggregated_user", "aggregated_insurance",
    "map_transaction", "map_user", "map_insurance",
    "top_transaction", "top_user", "top_insurance",
]


def get_connection():
    """Connect to MySQL server (no database selected)."""
    return mysql.connector.connect(
        host=MYSQL_HOST, user=MYSQL_USER, password=MYSQL_PASSWORD
    )


def get_db_connection():
    """Connect to the phonepe_pulse database."""
    return mysql.connector.connect(
        host=MYSQL_HOST, user=MYSQL_USER, password=MYSQL_PASSWORD,
        database=MYSQL_DB
    )


def create_database():
    """
    Initialize the MySQL database and create all required tables.
    Uses 'CREATE DATABASE IF NOT EXISTS' for idempotency.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(f"CREATE DATABASE IF NOT EXISTS {MYSQL_DB}")
    conn.close()

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""CREATE TABLE IF NOT EXISTS aggregated_transaction (
        id INT AUTO_INCREMENT PRIMARY KEY,
        state VARCHAR(100), year INT, quarter INT,
        transaction_type VARCHAR(100),
        transaction_count BIGINT,
        transaction_amount DOUBLE,
        INDEX idx_agg_txn (state, year, quarter)
    )""")

    cur.execute("""CREATE TABLE IF NOT EXISTS aggregated_user (
        id INT AUTO_INCREMENT PRIMARY KEY,
        state VARCHAR(100), year INT, quarter INT,
        brand VARCHAR(100),
        user_count BIGINT,
        user_percentage DOUBLE,
        INDEX idx_agg_user (state, year, quarter)
    )""")

    cur.execute("""CREATE TABLE IF NOT EXISTS aggregated_insurance (
        id INT AUTO_INCREMENT PRIMARY KEY,
        state VARCHAR(100), year INT, quarter INT,
        insurance_type VARCHAR(100),
        insurance_count BIGINT,
        insurance_amount DOUBLE,
        INDEX idx_agg_ins (state, year, quarter)
    )""")

    cur.execute("""CREATE TABLE IF NOT EXISTS map_transaction (
        id INT AUTO_INCREMENT PRIMARY KEY,
        state VARCHAR(100), year INT, quarter INT,
        district VARCHAR(100),
        transaction_count BIGINT,
        transaction_amount DOUBLE,
        INDEX idx_map_txn (state, year, quarter)
    )""")

    cur.execute("""CREATE TABLE IF NOT EXISTS map_user (
        id INT AUTO_INCREMENT PRIMARY KEY,
        state VARCHAR(100), year INT, quarter INT,
        district VARCHAR(100),
        registered_users BIGINT,
        app_opens BIGINT,
        INDEX idx_map_user (state, year, quarter)
    )""")

    cur.execute("""CREATE TABLE IF NOT EXISTS map_insurance (
        id INT AUTO_INCREMENT PRIMARY KEY,
        state VARCHAR(100), year INT, quarter INT,
        district VARCHAR(100),
        insurance_count BIGINT,
        insurance_amount DOUBLE,
        INDEX idx_map_ins (state, year, quarter)
    )""")

    cur.execute("""CREATE TABLE IF NOT EXISTS top_transaction (
        id INT AUTO_INCREMENT PRIMARY KEY,
        state VARCHAR(100), year INT, quarter INT,
        entity_name VARCHAR(100),
        entity_type VARCHAR(20),
        transaction_count BIGINT,
        transaction_amount DOUBLE,
        INDEX idx_top_txn (entity_type, state, year, quarter)
    )""")

    cur.execute("""CREATE TABLE IF NOT EXISTS top_user (
        id INT AUTO_INCREMENT PRIMARY KEY,
        state VARCHAR(100), year INT, quarter INT,
        entity_name VARCHAR(100),
        entity_type VARCHAR(20),
        registered_users BIGINT,
        INDEX idx_top_user (entity_type, state, year, quarter)
    )""")

    cur.execute("""CREATE TABLE IF NOT EXISTS top_insurance (
        id INT AUTO_INCREMENT PRIMARY KEY,
        state VARCHAR(100), year INT, quarter INT,
        entity_name VARCHAR(100),
        entity_type VARCHAR(20),
        insurance_count BIGINT,
        insurance_amount DOUBLE,
        INDEX idx_top_ins (entity_type, state, year, quarter)
    )""")

    conn.commit()
    conn.close()
    print("Database and tables created.")


def _iter_country_and_state(base_path):
    """
    Yield (label, year, quarter, filepath) for every JSON file
    under country-level and state-level folders.
    label = 'india' for country-level, or the folder name for states.
    """
    # Use os.path to ensure cross-platform compatibility
    if not os.path.exists(base_path):
        return

    # Country-level: base_path/<year>/<q>.json
    for year_name in os.listdir(base_path):
        year_path = os.path.join(base_path, year_name)
        if not os.path.isdir(year_path) or year_name == "state":
            continue
        for qf in os.listdir(year_path):
            yield "india", int(year_name), int(qf.split(".")[0]), os.path.join(year_path, qf)

    # State-level: base_path/state/<state>/<year>/<q>.json
    state_dir = os.path.join(base_path, "state")
    if not os.path.exists(state_dir):
        return
    for state_name in os.listdir(state_dir):
        sp = os.path.join(state_dir, state_name)
        if not os.path.isdir(sp):
            continue
        for year_name in os.listdir(sp):
            yp = os.path.join(sp, year_name)
            if not os.path.isdir(yp):
                continue
            for qf in os.listdir(yp):
                yield state_name, int(year_name), int(qf.split(".")[0]), os.path.join(yp, qf)


def extract_and_insert_aggregated_transaction(cur):
    """
    Parse aggregated transaction JSON files and bulk-insert into MySQL.
    Files are located under: pulse/data/aggregated/transaction/country/india/
    """
    rows = []
    base = os.path.join(DATA_PATH, "aggregated", "transaction", "country", "india")
    for label, year, quarter, fpath in _iter_country_and_state(base):
        with open(fpath) as f:
            data = json.load(f)
        for item in data.get("data", {}).get("transactionData", []):
            pi = item["paymentInstruments"][0]
            rows.append((
                label, year, quarter,
                item["name"], pi["count"], round(pi["amount"], 2),
            ))
    if rows:
        cur.executemany(
            """INSERT INTO aggregated_transaction
               (state, year, quarter, transaction_type, transaction_count, transaction_amount)
               VALUES (%s, %s, %s, %s, %s, %s)""", rows
        )
    print(f"  ➜ aggregated_transaction: {len(rows)} rows inserted")


def extract_and_insert_aggregated_user(cur):
    """Extract aggregated user (device brand) data from JSON and insert into MySQL."""
    rows = []
    base = os.path.join(DATA_PATH, "aggregated", "user", "country", "india")
    for label, year, quarter, fpath in _iter_country_and_state(base):
        with open(fpath) as f:
            data = json.load(f)
        for d in (data.get("data", {}).get("usersByDevice") or []):
            rows.append((
                label, year, quarter,
                d.get("brand", "Unknown"), d.get("count", 0), round(d.get("percentage", 0), 2),
            ))
    if rows:
        cur.executemany(
            """INSERT INTO aggregated_user
               (state, year, quarter, brand, user_count, user_percentage)
               VALUES (%s, %s, %s, %s, %s, %s)""", rows
        )
    print(f"  ➜ aggregated_user: {len(rows)} rows inserted")


def extract_and_insert_aggregated_insurance(cur):
    """Extract aggregated insurance data from JSON and insert into MySQL."""
    rows = []
    base = os.path.join(DATA_PATH, "aggregated", "insurance", "country", "india")
    for label, year, quarter, fpath in _iter_country_and_state(base):
        with open(fpath) as f:
            data = json.load(f)
        for item in data.get("data", {}).get("transactionData", []):
            pi = item["paymentInstruments"][0]
            rows.append((
                label, year, quarter,
                item["name"], pi["count"], round(pi["amount"], 2),
            ))
    if rows:
        cur.executemany(
            """INSERT INTO aggregated_insurance
               (state, year, quarter, insurance_type, insurance_count, insurance_amount)
               VALUES (%s, %s, %s, %s, %s, %s)""", rows
        )
    print(f"  ➜ aggregated_insurance: {len(rows)} rows inserted")


def extract_and_insert_map_transaction(cur):
    """Extract map-level transaction data (district hover) from JSON and insert into MySQL."""
    rows = []
    base = os.path.join(DATA_PATH, "map", "transaction", "hover", "country", "india")
    for label, year, quarter, fpath in _iter_country_and_state(base):
        with open(fpath) as f:
            data = json.load(f)
        for item in data.get("data", {}).get("hoverDataList", []):
            m = item["metric"][0]
            rows.append((
                label, year, quarter,
                item["name"], m["count"], round(m["amount"], 2),
            ))
    if rows:
        cur.executemany(
            """INSERT INTO map_transaction
               (state, year, quarter, district, transaction_count, transaction_amount)
               VALUES (%s, %s, %s, %s, %s, %s)""", rows
        )
    print(f"  ➜ map_transaction: {len(rows)} rows inserted")


def extract_and_insert_map_user(cur):
    """Extract map-level user data (registered users, app opens) from JSON and insert into MySQL."""
    rows = []
    base = os.path.join(DATA_PATH, "map", "user", "hover", "country", "india")
    for label, year, quarter, fpath in _iter_country_and_state(base):
        with open(fpath) as f:
            data = json.load(f)
        for name, vals in data.get("data", {}).get("hoverData", {}).items():
            rows.append((
                label, year, quarter,
                name, vals.get("registeredUsers", 0), vals.get("appOpens", 0),
            ))
    if rows:
        cur.executemany(
            """INSERT INTO map_user
               (state, year, quarter, district, registered_users, app_opens)
               VALUES (%s, %s, %s, %s, %s, %s)""", rows
        )
    print(f"  ➜ map_user: {len(rows)} rows inserted")


def extract_and_insert_map_insurance(cur):
    """Extract map-level insurance data (district hover) from JSON and insert into MySQL."""
    rows = []
    base = os.path.join(DATA_PATH, "map", "insurance", "hover", "country", "india")
    for label, year, quarter, fpath in _iter_country_and_state(base):
        with open(fpath) as f:
            data = json.load(f)
        for item in data.get("data", {}).get("hoverDataList", []):
            m = item["metric"][0]
            rows.append((
                label, year, quarter,
                item["name"], m["count"], round(m["amount"], 2),
            ))
    if rows:
        cur.executemany(
            """INSERT INTO map_insurance
               (state, year, quarter, district, insurance_count, insurance_amount)
               VALUES (%s, %s, %s, %s, %s, %s)""", rows
        )
    print(f"  ➜ map_insurance: {len(rows)} rows inserted")


def _extract_top_entities(d, entity_key, entity_type, use_metric=True):
    """Helper to extract states/districts/pincodes from top-level JSON data."""
    rows = []
    for s in (d.get(entity_key) or []):
        if use_metric:
            name = s["entityName"]
            m = s["metric"]
            rows.append((name, entity_type, m["count"], round(m["amount"], 2)))
        else:
            rows.append((s["name"], entity_type, s["registeredUsers"]))
    return rows


def extract_and_insert_top_transaction(cur):
    """Extract top transaction data (states, districts, pincodes) from JSON and insert into MySQL."""
    rows = []
    base = os.path.join(DATA_PATH, "top", "transaction", "country", "india")
    for label, year, quarter, fpath in _iter_country_and_state(base):
        with open(fpath) as f:
            data = json.load(f)
        d = data.get("data", {})
        for entity_key, entity_type in [("states", "state"), ("districts", "district"), ("pincodes", "pincode")]:
            for name, etype, count, amount in _extract_top_entities(d, entity_key, entity_type):
                rows.append((label, year, quarter, name, etype, count, amount))
    if rows:
        cur.executemany(
            """INSERT INTO top_transaction
               (state, year, quarter, entity_name, entity_type, transaction_count, transaction_amount)
               VALUES (%s, %s, %s, %s, %s, %s, %s)""", rows
        )
    print(f"  ➜ top_transaction: {len(rows)} rows inserted")


def extract_and_insert_top_user(cur):
    """Extract top user data (states, districts, pincodes) from JSON and insert into MySQL."""
    rows = []
    base = os.path.join(DATA_PATH, "top", "user", "country", "india")
    for label, year, quarter, fpath in _iter_country_and_state(base):
        with open(fpath) as f:
            data = json.load(f)
        d = data.get("data", {})
        for entity_key, entity_type in [("states", "state"), ("districts", "district"), ("pincodes", "pincode")]:
            for name, etype, users in _extract_top_entities(d, entity_key, entity_type, use_metric=False):
                rows.append((label, year, quarter, name, etype, users))
    if rows:
        cur.executemany(
            """INSERT INTO top_user
               (state, year, quarter, entity_name, entity_type, registered_users)
               VALUES (%s, %s, %s, %s, %s, %s)""", rows
        )
    print(f"  ➜ top_user: {len(rows)} rows inserted")


def extract_and_insert_top_insurance(cur):
    """Extract top insurance data (states, districts, pincodes) from JSON and insert into MySQL."""
    rows = []
    base = os.path.join(DATA_PATH, "top", "insurance", "country", "india")
    for label, year, quarter, fpath in _iter_country_and_state(base):
        with open(fpath) as f:
            data = json.load(f)
        d = data.get("data", {})
        for entity_key, entity_type in [("states", "state"), ("districts", "district"), ("pincodes", "pincode")]:
            for name, etype, count, amount in _extract_top_entities(d, entity_key, entity_type):
                rows.append((label, year, quarter, name, etype, count, amount))
    if rows:
        cur.executemany(
            """INSERT INTO top_insurance
               (state, year, quarter, entity_name, entity_type, insurance_count, insurance_amount)
               VALUES (%s, %s, %s, %s, %s, %s, %s)""", rows
        )
    print(f"  ➜ top_insurance: {len(rows)} rows inserted")


# --- Main Execution Script ---

if __name__ == "__main__":
    print("=" * 50)
    print("  PhonePe Pulse — Data Extractor")
    print("=" * 50)

    print("\n1. Creating database & tables ...")
    create_database()

    print("\n2. Truncating tables for clean load ...")
    conn = get_db_connection()
    cur = conn.cursor()
    for tbl in ALL_TABLES:
        cur.execute(f"TRUNCATE TABLE {tbl}")
    conn.commit()

    print("\n3. Extracting JSON data & inserting into MySQL ...\n")
    extract_and_insert_aggregated_transaction(cur)
    extract_and_insert_aggregated_user(cur)
    extract_and_insert_aggregated_insurance(cur)
    extract_and_insert_map_transaction(cur)
    extract_and_insert_map_user(cur)
    extract_and_insert_map_insurance(cur)
    extract_and_insert_top_transaction(cur)
    extract_and_insert_top_user(cur)
    extract_and_insert_top_insurance(cur)

    conn.commit()
    conn.close()

    print("\nAll data extracted and loaded into MySQL!")
    print(f"   Database : {MYSQL_DB}")
    print(f"   Host     : {MYSQL_HOST}")





