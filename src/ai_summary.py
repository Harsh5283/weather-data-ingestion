
import json
import logging
from pathlib import Path

import pandas as pd

from src.ai_summary import generate_weather_summary
from src.database import get_connection
from src.metrics import METRICS_QUERY

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "data" / "processed"

logging.basicConfig(level=logging.INFO)


def main():
    with get_connection() as connection:
        metrics = pd.read_sql_query(METRICS_QUERY, connection)

    if metrics.empty:
        raise ValueError("No daily weather metrics available.")

    # Generate a summary for the most recent date.
    latest = metrics.iloc[-1].to_dict()
    result = generate_weather_summary(latest)

    output = {
        "city": latest["city"],
        "date": latest["weather_date"],
        "method": result["method"],
        "summary": result["summary"],
    }

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_DIR / "weather_summary.json"

    output_path.write_text(
        json.dumps(output, indent=2, allow_nan=False),
        encoding="utf-8",
    )

    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
