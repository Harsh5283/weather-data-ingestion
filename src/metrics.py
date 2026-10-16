
from pathlib import Path

import pandas as pd

from src.database import get_connection

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "data" / "processed"

METRICS_QUERY = """
SELECT
    city,
    DATE(time) AS weather_date,
    ROUND(AVG(temperature_2m), 2) AS avg_temperature,
    ROUND(MIN(temperature_2m), 2) AS min_temperature,
    ROUND(MAX(temperature_2m), 2) AS max_temperature,
    ROUND(AVG(relative_humidity_2m), 2) AS avg_humidity,
    ROUND(SUM(precipitation), 2) AS total_precipitation,
    ROUND(AVG(wind_speed_10m), 2) AS avg_wind_speed,
    COUNT(*) AS observation_count
FROM weather_records
WHERE LOWER(TRIM(city)) = LOWER(TRIM(?))
GROUP BY city, DATE(time)
ORDER BY weather_date;
"""


def generate_daily_metrics(city="Bareilly"):
    with get_connection() as connection:
        metrics = pd.read_sql_query(
            METRICS_QUERY,
            connection,
            params=(city,)
        )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    output_file = OUTPUT_DIR / "daily_weather_metrics.csv"
    metrics.to_csv(output_file, index=False)

    print(f"Daily summaries generated for {city}: {len(metrics)}")
    print(metrics.to_string(index=False))
    print(f"\nSaved to: {output_file}")

    return metrics


if __name__ == "__main__":
    generate_daily_metrics()
