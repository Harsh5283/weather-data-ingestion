
# Weather Data Ingestion — Architecture

## Overview

The pipeline fetches weather observations from the Open-Meteo API,
stores the raw response, validates and transforms the data,
loads curated records into SQLite, calculates daily metrics,
and generates a concise weather summary.

## Data Flow

```mermaid
flowchart TD
    A[Open-Meteo Public API] --> B[Weather Ingestion]
    B --> C[Raw JSON Files]
    C --> D[Validation and Transformation]
    D --> E[Cleaned Weather CSV]
    E --> F[SQLite Database]
    F --> G[Daily Weather Metrics]
    G --> H[AI Summary Interface]
    H --> I{AI Available?}
    I -->|Yes| J[AI-Generated Summary]
    I -->|No or Failure| K[Local Fallback Summary]
    J --> L[weather_summary.json]
    K --> L
    F --> M[Pipeline Run Logs]
```

## Main Components

- **Ingestion:** Retrieves weather data from Open-Meteo and saves the raw response.
- **Transformation:** Parses timestamps, converts measurements to numeric values, handles invalid measurements, and removes duplicate records.
- **Database:** Stores curated weather records in SQLite using a unique city-and-timestamp key.
- **Metrics:** Calculates daily temperature, humidity, precipitation, and wind metrics.
- **AI summary:** Uses an isolated summary interface with a local fallback if the provider is unavailable.
- **Testing:** Validates data transformation, duplicate handling, invalid measurements, and AI fallback behavior.

## Reliability

- Retries are configured for selected transient API errors.
- Database upserts support repeated ingestion without duplicate city/timestamp records.
- Invalid measurements are handled during transformation.
- AI provider failures fall back to a local summary.
- Pipeline run status and errors can be recorded in SQLite.
