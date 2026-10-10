
# Weather Data Ingestion — Architecture

## Objective
Build a Python-based pipeline that collects weather
data, preserves raw responses, validates measurements,
and prepares clean records for SQL storage and analysis.

## Data Source
Open-Meteo Forecast API.

## Current Pipeline
1. Fetch hourly weather data for Gorakhpur.
2. Save the original API response as JSON in data/raw/.
3. Load the JSON into Pandas.
4. Validate timestamps and weather measurements.
5. Remove duplicate city-and-timestamp records.
6. Save clean records to data/processed/weather_clean.csv.

## Technology Stack
- Python
- Requests
- Pandas
- SQLite (planned)
- Pytest (planned)

## Next Steps
- Create SQL tables and load curated records.
- Implement incremental ingestion and upserts.
- Add an AI-generated weather summary.
- Write automated tests.
