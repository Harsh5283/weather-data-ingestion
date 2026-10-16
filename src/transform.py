
import json
import logging
from pathlib import Path
from src.config import CITY, CITY_SLUG, LATITUDE, LONGITUDE
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

MEASUREMENT_COLUMNS = [
    "temperature_2m",
    "relative_humidity_2m",
    "precipitation",
    "wind_speed_10m",
]


def load_latest_raw_data():
    files = sorted(RAW_DIR.glob(f"{CITY_SLUG}_*.json"))

    if not files:
        raise FileNotFoundError(
            f"No raw weather data found for {CITY}."
        )

    with files[-1].open("r", encoding="utf-8") as file:
        return json.load(file)

def transform_weather_data(data):
    hourly = data.get("hourly", {})
    timestamps = hourly.get("time", [])

    if not timestamps:
        raise ValueError("Weather data contains no timestamps.")

    df = pd.DataFrame(hourly)

    required_columns = ["time"] + MEASUREMENT_COLUMNS
    missing_columns = [
        column for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(f"Missing columns: {missing_columns}")

    df["city"] = data.get("city", CITY)
    df["latitude"] = data.get("latitude", LATITUDE)
    df["longitude"] = data.get("longitude", LONGITUDE)

    # Parse timestamps and discard records without valid timestamps.
    df["time"] = pd.to_datetime(df["time"], errors="coerce")
    df = df.dropna(subset=["time"]).copy()

    # Convert measurement columns to numeric values.
    for column in MEASUREMENT_COLUMNS:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    # Convert physically implausible measurements to missing values.
    df.loc[
        ~df["temperature_2m"].between(-90, 60),
        "temperature_2m",
    ] = float("nan")

    df.loc[
        ~df["relative_humidity_2m"].between(0, 100),
        "relative_humidity_2m",
    ] = float("nan")

    df.loc[
        df["precipitation"] < 0,
        "precipitation",
    ] = float("nan")

    df.loc[
        df["wind_speed_10m"] < 0,
        "wind_speed_10m",
    ] = float("nan")

    # Keep one record per city and timestamp.
    df = df.drop_duplicates(
        subset=["city", "time"],
        keep="last",
    )

    df = df.sort_values("time").reset_index(drop=True)

    return df


def main():
    data = load_latest_raw_data()
    original_count = len(data["hourly"]["time"])

    df = transform_weather_data(data)

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    output_file = PROCESSED_DIR / "weather_clean.csv"
    df.to_csv(output_file, index=False)

    logging.info("Raw records: %d", original_count)
    logging.info("Clean records: %d", len(df))
    logging.info("Duplicate/invalid timestamp rows removed: %d",
                 original_count - len(df))
    logging.info("Missing measurements:\n%s",
                 df[MEASUREMENT_COLUMNS].isna().sum().to_string())
    logging.info("Saved cleaned data to %s", output_file)


if __name__ == "__main__":
    main()
