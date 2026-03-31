# Wildfire Risk MVP

End-to-end geospatial analytics pipeline for NDVI-based wildfire risk mapping using Sentinel-2 imagery from Google Earth Engine.

This repository is prepared as a working proof-of-concept for a Google Summer of Code 2026 proposal focused on multimodal spatiotemporal wildfire risk prediction for Alaska.

[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Google Earth Engine](https://img.shields.io/badge/Google%20Earth%20Engine-4285F4?style=for-the-badge&logo=google-earth-engine&logoColor=white)](https://earthengine.google.com)
[![GSoC 2026](https://img.shields.io/badge/GSoC-2026-FF6F00?style=for-the-badge)](https://summerofcode.withgoogle.com)

## Overview

The MVP currently implements a reproducible baseline pipeline:

1. Ingest Sentinel-2 imagery from GEE.
2. Apply cloud and cirrus masking.
3. Compute NDVI.
4. Classify wildfire risk using configurable thresholds.
5. Visualize results as an interactive map.

It supports both CLI execution and REST API access.

Current scope: NDVI-based rule-engine risk mapping.

Planned GSoC extension: multimodal Sentinel-1 + Sentinel-2 + weather-driven spatiotemporal modeling.

## Features

- Sentinel-2 ingestion via Google Earth Engine
- Automated cloud and cirrus masking
- NDVI computation over selected AOI and time range
- Configurable wildfire risk classification
- Interactive Folium map with risk-colored points
- FastAPI endpoints for programmatic triggering and retrieval
- YAML-driven configuration for reproducible experiments

## Demo

![Wildfire Risk Map Demo](https://github.com/Raga-V/wildfire-risk-mvp/raw/main/outputs/maps/wildfire_risk_map.png)

Interactive Folium map showing NDVI-derived risk levels: High (Red), Moderate (Orange), Low (Green).

## Risk Classes

| NDVI Range | Risk Level | Map Color |
|---|---|---|
| $NDVI < 0.2$ | High | Red |
| $0.2 \le NDVI < 0.4$ | Moderate | Orange |
| $NDVI \ge 0.4$ | Low | Green |

Thresholds are configurable in `config/config.yaml`.

## Pipeline Architecture

```text
Sentinel-2 (GEE)
  -> Ingestion
  -> Preprocessing (cloud masking)
  -> NDVI Computation
  -> Risk Mapping (threshold-based)
  -> Interactive Folium Map + API Output
```

NDVI formula:

$$
NDVI = \frac{NIR - Red}{NIR + Red}
$$

## Tech Stack

| Layer | Technologies |
|---|---|
| Language | Python 3.10+ |
| Geospatial | Google Earth Engine, earthengine-api |
| Processing | NumPy, PyYAML |
| Visualization | Folium (Leaflet) |
| Backend | FastAPI, Uvicorn, Pydantic |
| Configuration | YAML |

## Quick Start

### 1. Clone repository

```bash
git clone https://github.com/Raga-V/wildfire-risk-mvp.git
cd wildfire-risk-mvp
```

### 2. Create and activate virtual environment

```bash
python -m venv .venv
```

Windows (PowerShell):

```bash
.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Authenticate Earth Engine

```bash
earthengine authenticate
```

### 5. Set GEE project

Choose one of the following:

- Set `gee.project` in `config/config.yaml`
- Set environment variable `EE_PROJECT`
- Set environment variable `GOOGLE_CLOUD_PROJECT`

### 6. Run pipeline

```bash
python run.py
```

Output map path:

- `outputs/maps/wildfire_risk_map.html`

## API Usage (Optional)

Run server:

```bash
uvicorn api.app:app --reload
```

Open API docs at:

- `http://localhost:8000/docs`

Endpoints:

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Health check |
| POST | `/run` | Trigger pipeline with optional overrides |
| GET | `/map` | Download latest generated map |
| GET | `/stats` | Return last run statistics |

## Project Structure

```text
wildfire-risk-mvp/
├── run.py
├── requirements.txt
├── README.md
├── config/
│   └── config.yaml
├── src/
│   ├── main.py
│   ├── data/
│   ├── features/
│   ├── risk/
│   └── visualization/
├── api/
│   └── app.py
└── outputs/
    ├── maps/
    └── logs/
```

## GSoC 2026 Roadmap

1. Baseline hardening, validation, and Alaska-specific AOIs
2. Add multimodal inputs (Sentinel-1 SAR, weather reanalysis)
3. Build spatiotemporal models (CNN-LSTM or ConvLSTM)
4. Implement strict pre-fire leakage prevention and evaluation protocols
5. Develop production-facing GIS dashboard and containerized deployment

## Full Proposal

If included in this repository, the full proposal PDF is available at:

- `docs/GSoC_Proposal.pdf`

## Author

Raga Gowtami Vinjanampati  
B.Tech Computer Science  
GitHub: [@Raga-V](https://github.com/Raga-V)

## Support

If this project helped you, consider starring the repository.
Made with ❤️ for better wildfire risk prediction in Alaska
