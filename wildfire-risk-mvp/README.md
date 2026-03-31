# Wildfire Risk MVP

An end-to-end geospatial analytics pipeline that uses Sentinel-2 imagery from Google Earth Engine (GEE) to generate NDVI-based wildfire risk maps and expose results through both a CLI and a REST API.

This repository is prepared as a GSoC 2026 proposal artifact: it demonstrates an implementable baseline, reproducible workflow, and a clear path to scale into a production-grade wildfire risk platform.

## Problem Statement

Wildfire management teams need early, location-specific indicators of vegetation stress and fuel dryness. Existing systems are often expensive, hard to reproduce, or tightly coupled to specific infrastructure.

This MVP addresses that gap by providing:

- A transparent and reproducible NDVI-based risk workflow.
- Config-driven regional analysis for rapid experimentation.
- Interactive map outputs for non-technical stakeholders.
- API access for integration with dashboards and downstream services.

## Goals

- Build a modular wildfire risk pipeline from ingestion to visualization.
- Keep methods interpretable and configurable.
- Minimize local compute burden by using cloud geospatial processing (GEE).
- Provide deployment-friendly interfaces (CLI and FastAPI).

## Current Scope (MVP)

- Data source: Sentinel-2 Surface Reflectance (harmonized) from GEE.
- Feature: NDVI from NIR/Red bands.
- Risk model: rule-based thresholds on NDVI.
- Output: interactive Folium HTML map with risk-colored sample points.
- Service: optional FastAPI endpoints to run and fetch results.

## Pipeline Architecture

```
Sentinel-2 (GEE)
      |
      v
[1] Ingestion (src/data/ingestion.py)
      |
      v
[2] Preprocessing (src/data/preprocessing.py)
      |
      v
[3] NDVI Computation (src/features/ndvi.py)
      |
      v
[4] Risk Mapping (src/risk/mapping.py)
      |
      v
[5] Visualization (src/visualization/map.py)
      |
      v
outputs/maps/wildfire_risk_map.html
```

## Repository Layout

```
wildfire-risk-mvp/
├── run.py
├── requirements.txt
├── README.md
├── config/
│   └── config.yaml
├── src/
│   ├── main.py
│   ├── data/
│   │   ├── ingestion.py
│   │   ├── preprocessing.py
│   │   └── utils.py
│   ├── features/
│   │   └── ndvi.py
│   ├── risk/
│   │   └── mapping.py
│   └── visualization/
│       └── map.py
├── api/
│   └── app.py
└── outputs/
    ├── logs/
    └── maps/
```

## Methodology

1. Ingest Sentinel-2 imagery over a configured bounding box and date range.
2. Apply QA60 cloud and cirrus masking and scale reflectance values.
3. Compute NDVI using:

$$
NDVI = \frac{NIR - Red}{NIR + Red}
$$

4. Classify NDVI into wildfire risk levels.
5. Sample and render geospatial risk points onto an interactive Folium map.

## Risk Classes

| NDVI Range | Risk Level | Map Color |
|---|---|---|
| $NDVI < 0.2$ | High | Red |
| $0.2 \le NDVI < 0.4$ | Moderate | Orange |
| $NDVI \ge 0.4$ | Low | Green |

Thresholds are configurable in [config/config.yaml](config/config.yaml).

## Configuration

Core settings live in [config/config.yaml](config/config.yaml):

- `region.bbox`: geographic area of interest.
- `dates.start`, `dates.end`: temporal window.
- `gee.project`: GCP project for Earth Engine initialization.
- `sentinel2.cloud_cover_threshold`: image filtering quality.
- `ndvi.thresholds`: risk mapping thresholds.
- `risk.geojson_sample_scale`, `risk.geojson_max_features`: output map density/performance controls.

## Setup

### 1. Create and activate a virtual environment

```bash
python -m venv .venv
```

Windows (PowerShell):

```bash
.venv\Scripts\Activate.ps1
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Authenticate Earth Engine

```bash
earthengine authenticate
```

### 4. Set GEE project

Option A: Set `gee.project` in [config/config.yaml](config/config.yaml).

Option B: Set an environment variable:

```bash
set EE_PROJECT=your-gcp-project-id
```

or

```bash
set GOOGLE_CLOUD_PROJECT=your-gcp-project-id
```

## Usage

### Run via CLI

```bash
python run.py
```

Run with custom config:

```bash
python run.py --config path/to/custom_config.yaml
```

Output map:

- [outputs/maps/wildfire_risk_map.html](outputs/maps/wildfire_risk_map.html)

### Run via API (optional)

```bash
uvicorn api.app:app --reload
```

Open docs: `http://localhost:8000/docs`

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/` | Health check |
| POST | `/run` | Trigger pipeline run |
| GET | `/map` | Download latest generated map |
| GET | `/stats` | Retrieve last run statistics (if available) |

## Reproducibility Notes

- Keep the same `region`, `date range`, and thresholds for comparable runs.
- Use fixed sampling settings (`risk.geojson_sample_*`) to control map output size.
- Earth Engine collection behavior may vary if upstream datasets are revised.

## Limitations (Current MVP)

- NDVI-only risk estimation can miss meteorological and topographic drivers.
- Rule-based thresholds are region dependent and need local calibration.
- Output is a risk indicator, not a fire spread simulator.
- Statistics endpoint depends on persisted run artifacts.

## GSoC 2026 Proposal Roadmap

### Phase 1: Baseline hardening

- Add automated validation checks and benchmark runs for selected AOIs.
- Improve configuration schema validation and error reporting.
- Improve API response contracts and output metadata.

### Phase 2: Model enrichment

- Add additional predictors (LST, slope, aspect, wind, humidity proxies).
- Introduce temporal compositing and anomaly features.
- Evaluate multiple risk scoring strategies.

### Phase 3: Evaluation and calibration

- Compare predicted risk with historical fire events.
- Report confusion-aware metrics and calibration curves.
- Add region-specific threshold tuning workflows.

### Phase 4: Productization

- Containerize pipeline and API.
- Add CI checks and artifact versioning.
- Prepare deployment documentation and demo dashboard integration.

## Deliverables for GSoC

- Documented and reproducible wildfire risk pipeline.
- Improved, extensible risk modeling module.
- Evaluation framework with measurable metrics.
- Deployment-ready API workflow with clear usage docs.

## Why This Matters

This project aims to bridge remote sensing and practical decision support by making wildfire risk estimation open, reproducible, and easy to integrate. It can serve as a foundation for community-driven, region-adaptable wildfire analytics in public-interest contexts.

## Tech Stack

- `earthengine-api`
- `numpy`
- `pyyaml`
- `folium`
- `fastapi`
- `uvicorn`
- `pydantic`

## License and Contribution

If this repository is used for a formal GSoC submission, include project license details and contribution guidelines in separate files (`LICENSE`, `CONTRIBUTING.md`) before final submission.
