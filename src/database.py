
import sqlite3
from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "weather.db"
SCHEMA_PATH = BASE_DIR / "sql" / "schema.sql"


def get_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(DB_PATH)
    connection.execute("PRAGMA foreign_keys = ON")

    return connection



def initialize_database():
    with get_connection() as connection:
        schema = SCHEMA_PATH.read_text(encoding="utf-8")
        connection.executescript(schema)

        runs_schema_path = BASE_DIR / "sql" / "pipeline_runs.sql"
        runs_schema = runs_schema_path.read_text(encoding="utf-8")
        connection.executescript(runs_schema)

    print(f"Database initialized: {DB_PATH}")


def load_cleaned_weather():
    csv_path = BASE_DIR / "data" / "processed" / "weather_clean.csv"

    if not csv_path.exists():
        raise FileNotFoundError(
            f"Cleaned data not found: {csv_path}"
        )

    df = pd.read_csv(csv_path)

    required = [
        "time",
        "city",
        "latitude",
        "longitude",
        "temperature_2m",
        "relative_humidity_2m",
        "precipitation",
        "wind_speed_10m",
    ]

    missing = set(required) - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    df = df[required].copy()
    df["time"] = pd.to_datetime(
        df["time"], errors="coerce"
    ).dt.strftime("%Y-%m-%d %H:%M:%S")

    df = df.dropna(subset=["time", "city"])

    columns = ", ".join(required)
    placeholders = ", ".join(["?"] * len(required))

    sql = f"""
        INSERT INTO weather_records ({columns})
        VALUES ({placeholders})
        ON CONFLICT(city, time) DO UPDATE SET
            latitude = excluded.latitude,
            longitude = excluded.longitude,
            temperature_2m = excluded.temperature_2m,
            relative_humidity_2m = excluded.relative_humidity_2m,
            precipitation = excluded.precipitation,
            wind_speed_10m = excluded.wind_speed_10m
    """

    records = [
        tuple(
            None if pd.isna(value) else value
            for value in row
        )
        for row in df.itertuples(index=False, name=None)
    ]

    with get_connection() as connection:
        connection.executemany(sql, records)

        count = connection.execute(
            "SELECT COUNT(*) FROM weather_records"
        ).fetchone()[0]

    print(f"Records processed: {len(records)}")
    print(f"Total unique records in database: {count}")


def start_pipeline_run():
    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO pipeline_runs (status)
            VALUES ('RUNNING')
            """
        )
        return cursor.lastrowid


def finish_pipeline_run(
    run_id,
    status,
    records_processed=0,
    error_message=None,
):
    with get_connection() as connection:
        connection.execute(
            """
            UPDATE pipeline_runs
            SET completed_at = CURRENT_TIMESTAMP,
                status = ?,
                records_processed = ?,
                error_message = ?
            WHERE run_id = ?
            """,
            (status, records_processed, error_message, run_id),
        )



if __name__ == "__main__":
    initialize_database()
    load_cleaned_weather()

