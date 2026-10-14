
import pandas as pd

from src.ai_summary import generate_weather_summary, local_summary


def sample_metrics():
    return {
        "city": "Gorakhpur",
        "weather_date": "2026-10-13",
        "avg_temperature": 30.5,
        "min_temperature": 27.0,
        "max_temperature": 34.0,
        "avg_humidity": 65.0,
        "total_precipitation": 1.2,
        "avg_wind_speed": 8.0,
    }


def test_local_summary_uses_weather_metrics():
    summary = local_summary(sample_metrics())

    assert "Gorakhpur" in summary
    assert "2026-10-13" in summary
    assert "30.5" in summary


def test_missing_api_key_uses_fallback(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    result = generate_weather_summary(sample_metrics())

    assert result["method"] == "local_fallback"
    assert "Gorakhpur" in result["summary"]


def test_ai_failure_uses_fallback(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")

    def raise_error(*args, **kwargs):
        raise RuntimeError("Simulated provider failure")

    from openai import OpenAI

    monkeypatch.setattr(OpenAI, "__init__", raise_error)

    result = generate_weather_summary(sample_metrics())

    assert result["method"] == "local_fallback"
    assert "Gorakhpur" in result["summary"]

