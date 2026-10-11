
import logging
import traceback

from src.ingest import fetch_weather, save_raw_data
from src.transform import transform_weather_data
from src.database import (
    initialize_database,
    get_connection,
    start_pipeline_run,
    finish_pipeline_run,
)
from src.metrics import generate_daily_metrics

import pandas as pd

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)


def load_dataframe(df):
    """Insert or update cleaned weather records in SQLite."""
    columns = [
        "city",
        "time",
        "latitude",
        "longitude",
        "temperature_2m",
        "relative_humidity_2m",
        "precipitation",
        "wind_speed_10m",
    ]

    df = df[columns].copy()
    df["time"] = pd.to_datetime(
        df["time"], errors="coerce"
    ).dt.strftime("%Y-%m-%d %H:%M:%S")

    df = df.dropna(subset=["city", "time"])

    sql = """
        INSERT INTO weather_records (
            city, time, latitude, longitude,
            temperature_2m, relative_humidity_2m,
            precipitation, wind_speed_10m
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(city, time) DO UPDATE SET
            latitude = excluded.latitude,
            longitude = excluded.longitude,
            temperature_2m = excluded.temperature_2m,
            relative_humidity_2m = excluded.relative_humidity_2m,
            precipitation = excluded.precipitation,
            wind_speed_10m = excluded.wind_speed_10m
    """

    records = [
        tuple(None if pd.isna(value) else value for value in row)
        for row in df.itertuples(index=False, name=None)
    ]

    with get_connection() as connection:
        connection.executemany(sql, records)

    return len(records)


def run_pipeline():
    initialize_database()
    run_id = start_pipeline_run()
    processed_count = 0

    try:
        logging.info("Starting weather pipeline")

        # 1. Fetch and preserve raw data.
        raw_data = fetch_weather()
        save_raw_data(raw_data)

        # 2. Transform and validate records.
        df = transform_weather_data(raw_data)

        # 3. Load curated records into SQL.
        processed_count = load_dataframe(df)

        # 4. Generate daily weather metrics.
        generate_daily_metrics()

        finish_pipeline_run(
            run_id,
            "SUCCESS",
            records_processed=processed_count,
        )

        logging.info(
            "Pipeline completed successfully. Records processed: %d",
            processed_count,
        )

    except Exception as error:
        finish_pipeline_run(
            run_id,
            "FAILED",
            records_processed=processed_count,
            error_message=str(error)[:1000],
        )
        logging.exception("Pipeline failed")
        raise


if __name__ == "__main__":
    run_pipeline()
