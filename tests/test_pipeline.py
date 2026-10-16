
import math

import pytest

from src.transform import transform_weather_data


def sample_weather_data():
    return {
        "city": "Gorakhpur",
        "latitude": 26.7606,
        "longitude": 83.3732,
        "hourly": {
            "time": [
                "2026-10-11T10:00",
                "2026-10-11T11:00",
            ],
            "temperature_2m": [30.5, 31.0],
            "relative_humidity_2m": [65, 60],
            "precipitation": [0.0, 0.2],
            "wind_speed_10m": [8.0, 9.5],
        },
    }


def test_valid_weather_data_is_transformed():
    data = sample_weather_data()

    df = transform_weather_data(data)

    assert len(df) == 2
    assert df["city"].eq("Gorakhpur").all()
    assert df["temperature_2m"].tolist() == [30.5, 31.0]


def test_duplicate_timestamps_are_removed():
    data = sample_weather_data()

    # Add a duplicate observation at the first timestamp.
    for column in data["hourly"]:
        data["hourly"][column].append(data["hourly"][column][0])

    df = transform_weather_data(data)

    assert len(df) == 2
    assert not df.duplicated(["city", "time"]).any()


def test_missing_timestamps_raise_error():
    data = sample_weather_data()
    data["hourly"]["time"] = []

    with pytest.raises(ValueError, match="no timestamps"):
        transform_weather_data(data)


def test_invalid_humidity_becomes_missing():
    data = sample_weather_data()
    data["hourly"]["relative_humidity_2m"][0] = 150

    df = transform_weather_data(data)

    assert math.isnan(df.iloc[0]["relative_humidity_2m"])
    assert df.iloc[1]["relative_humidity_2m"] == 60
