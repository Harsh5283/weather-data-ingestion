
import os
import re

CITY = os.getenv("WEATHER_CITY", "Bareilly").strip()
LATITUDE = float(os.getenv("WEATHER_LATITUDE", "28.3670"))
LONGITUDE = float(os.getenv("WEATHER_LONGITUDE", "79.4304"))

CITY_SLUG = re.sub(
    r"[^a-z0-9]+",
    "_",
    CITY.lower(),
).strip("_")
