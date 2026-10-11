
CREATE TABLE IF NOT EXISTS weather_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    city TEXT NOT NULL,
    time TEXT NOT NULL,

    latitude REAL,
    longitude REAL,

    temperature_2m REAL,
    relative_humidity_2m REAL,
    precipitation REAL,
    wind_speed_10m REAL,

    loaded_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

    UNIQUE (city, time)
);

CREATE INDEX IF NOT EXISTS idx_weather_city_time
ON weather_records (city, time);
