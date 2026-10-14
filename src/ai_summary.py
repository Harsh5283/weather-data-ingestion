
import logging
import os

import pandas as pd

logger = logging.getLogger(__name__)


def build_weather_prompt(metrics: dict) -> str:
    """Build a prompt using the supplied daily weather metrics."""
    return f"""
You are a weather data analyst. Write a concise summary in 2-3 sentences.
Use only the figures provided. Do not invent forecasts, causes, or safety advice.

City: {metrics.get("city", "Unknown")}
Date: {metrics.get("weather_date", "Unknown")}
Average temperature: {metrics.get("avg_temperature")} °C
Minimum temperature: {metrics.get("min_temperature")} °C
Maximum temperature: {metrics.get("max_temperature")} °C
Average humidity: {metrics.get("avg_humidity")} %
Total precipitation: {metrics.get("total_precipitation")}
Average wind speed: {metrics.get("avg_wind_speed")}
""".strip()


def local_summary(metrics: dict) -> str:
    """Generate a deterministic summary without an external AI service."""
    city = metrics.get("city", "Unknown city")
    weather_date = metrics.get("weather_date", "Unknown date")

    parts = [f"Weather summary for {city} on {weather_date}."]

    fields = [
        ("avg_temperature", "Average temperature", "°C"),
        ("avg_humidity", "Average humidity", "%"),
        ("total_precipitation", "Total precipitation", ""),
        ("avg_wind_speed", "Average wind speed", ""),
    ]

    for key, label, unit in fields:
        value = metrics.get(key)

        if value is not None and pd.notna(value):
            parts.append(f"{label}: {value}{' ' + unit if unit else ''}.")
        else:
            parts.append(f"{label}: unavailable.")

    return " ".join(parts)


def generate_weather_summary(metrics: dict) -> dict:
    """Try the configured AI provider; fall back safely if unavailable."""
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        logger.info("No AI API key configured; using local summary.")
        return {
            "summary": local_summary(metrics),
            "method": "local_fallback",
        }

    try:
        from openai import OpenAI

        client = OpenAI(api_key=api_key)
        response = client.responses.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
            input=build_weather_prompt(metrics),
        )

        summary = response.output_text.strip()
        if not summary:
            raise ValueError("The AI provider returned an empty summary.")

        return {"summary": summary, "method": "ai"}

    except Exception:
        logger.exception("AI summary failed; using local fallback.")
        return {
            "summary": local_summary(metrics),
            "method": "local_fallback",
        }
