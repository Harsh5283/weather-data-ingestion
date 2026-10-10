
import json
import logging
from datetime import datetime, timezone
from pathlib import Path

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"

API_URL = "https://api.open-meteo.com/v1/forecast"

PARAMS = {
    "latitude": 26.7606,
    "longitude": 83.3732,
    "hourly": [
        "temperature_2m",
        "relative_humidity_2m",
        "precipitation",
        "wind_speed_10m",
    ],
    "past_days": 2,
    "forecast_days": 1,
    "timezone": "Asia/Kolkata",
}

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)


def fetch_weather():
    session = requests.Session()

    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"],
    )

    session.mount("https://", HTTPAdapter(max_retries=retry_strategy))

    response = session.get(
        API_URL,
        params=PARAMS,
        timeout=20,
    )
    response.raise_for_status()

    data = response.json()

    if "hourly" not in data or "time" not in data["hourly"]:
        raise ValueError("Invalid API response: hourly data is missing")

    return data


def save_raw_data(data):
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    output_file = RAW_DIR / f"gorakhpur_{timestamp}.json"

    with output_file.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=2)

    logging.info("Saved raw weather data to %s", output_file)
    logging.info("Hourly records received: %d", len(data["hourly"]["time"]))


def main():
    try:
        logging.info("Fetching weather data for Gorakhpur...")
        data = fetch_weather()
        save_raw_data(data)
        logging.info("Ingestion completed successfully.")

    except (requests.RequestException, ValueError) as error:
        logging.error("Ingestion failed: %s", error)
        raise


if __name__ == "__main__":
    main()
