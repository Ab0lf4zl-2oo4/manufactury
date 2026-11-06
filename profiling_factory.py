import pandas as pd
import sqlalchemy as sq
from pathlib import Path
assets=pd.read_csv('assets.csv')
failure=pd.read_csv('failure_events.csv')
sensor_rd=pd.read_csv('sensor_readings.csv')
sites=pd.read_csv('sites.csv')
work_o=pd.read_csv('work_orders.csv')

SERVER = r"DESKTOP-JKUS70M"
DATABASE = "factory"

CONNECTION_STRING = (
    f"mssql+pyodbc://@{SERVER}/{DATABASE}"
    "?driver=ODBC+Driver+18+for+SQL+Server"
    "&trusted_connection=yes"
    "&TrustServerCertificate=yes"
)


# -----------------------------
# 2. Create database engine
# -----------------------------

def create_db_engine():
    return sq.create_engine(
        CONNECTION_STRING,
        fast_executemany=True
    )


# -----------------------------
# 3. Load CSV into SQL Server
# -----------------------------

def load_csv_to_sql(csv_path, table_name):
    csv_path = Path(csv_path)

    if not csv_path.exists():
        print(f"ERROR: CSV file not found: {csv_path}")
        return

    engine = create_db_engine()

    try:
        print(f"\nReading: {csv_path}")

        df = pd.read_csv(csv_path)

        print(f"Rows found: {len(df):,}")
        print(f"Loading into staging.{table_name} ...")

        df.to_sql(
            name=table_name,
            con=engine,
            schema="staging",
            if_exists="append",
            index=False,
            chunksize=1000
        )

        print(
            f"SUCCESS: staging.{table_name} "
            f"loaded with {len(df):,} rows."
        )

    except Exception as error:
        print(f"ERROR loading {table_name}:")
        print(error)

    finally:
        engine.dispose()


# -----------------------------
# 4. CSV file paths
# -----------------------------


files_to_load = {
    "assets": "assets.csv",
    "failure": "failure_events.csv",
    "sensor_rd": "sensor_readings.csv",
    "sites": "sites.csv",
    "w_o": "work_orders.csv"
}


# -----------------------------
# 5. Load all remaining tables
# -----------------------------

if __name__ == "__main__":
    for table_name, csv_path in files_to_load.items():
        load_csv_to_sql(csv_path, table_name)

    print("\nCSV loading process finished.")