
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
GROUP BY city, DATE(time)
ORDER BY weather_date;
