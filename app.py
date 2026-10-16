
from flask import Flask, render_template, request
import requests

app = Flask(__name__)

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"


@app.route("/", methods=["GET", "POST"])
def home():
    weather = None
    forecast = []
    error = None
    city = ""

    if request.method == "POST":
        city = request.form.get("city", "").strip()

        if not city:
            error = "Please enter a city name."
        else:
            try:
                geo_response = requests.get(
                    GEOCODING_URL,
                    params={
                        "name": city,
                        "count": 10,
                        "language": "en",
                        "format": "json",
                    },
                    timeout=10,
                )
                geo_response.raise_for_status()
                locations = geo_response.json().get("results", [])

                if not locations:
                    error = f"No location found for '{city}'. Try another city."
                else:
                    # Prefer an exact city-name match when available.
                    location = next(
                        (
                            item for item in locations
                            if item["name"].casefold() == city.casefold()
                        ),
                        locations[0],
                    )

                    weather_response = requests.get(
                        WEATHER_URL,
                        params={
                            "latitude": location["latitude"],
                            "longitude": location["longitude"],
                            "current": (
                                "temperature_2m,"
                                "relative_humidity_2m,"
                                "apparent_temperature,"
                                "precipitation,"
                                "wind_speed_10m"
                            ),
                            "daily": (
                                "weather_code,"
                                "temperature_2m_max,"
                                "temperature_2m_min,"
                                "precipitation_sum"
                            ),
                            "timezone": "auto",
                            "forecast_days": 7,
                        },
                        timeout=10,
                    )
                    weather_response.raise_for_status()
                    data = weather_response.json()

                    current = data.get("current", {})
                    daily = data.get("daily", {})

                    weather = {
                        "city": location["name"],
                        "region": location.get("admin1", ""),
                        "country": location.get("country", ""),
                        "temperature": current.get("temperature_2m"),
                        "feels_like": current.get("apparent_temperature"),
                        "humidity": current.get("relative_humidity_2m"),
                        "precipitation": current.get("precipitation"),
                        "wind_speed": current.get("wind_speed_10m"),
                    }

                    dates = daily.get("time", [])
                    highs = daily.get("temperature_2m_max", [])
                    lows = daily.get("temperature_2m_min", [])
                    rain = daily.get("precipitation_sum", [])
                    codes = daily.get("weather_code", [])

                    forecast = [
                        {
                            "date": dates[i],
                            "max_temp": highs[i],
                            "min_temp": lows[i],
                            "precipitation": rain[i],
                            "weather_code": codes[i] if i < len(codes) else None,
                        }
                        for i in range(min(len(dates), len(highs), len(lows), len(rain)))
                    ]

            except requests.RequestException:
                error = (
                    "Unable to retrieve weather data. "
                    "Check your internet connection and try again."
                )
            except (ValueError, KeyError, IndexError):
                error = "The weather service returned unexpected data."

    return render_template(
        "index.html",
        weather=weather,
        forecast=forecast,
        error=error,
        city=city,
    )


if __name__ == "__main__":
    app.run(debug=True)
