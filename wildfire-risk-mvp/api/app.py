import os
import json
import logging
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

from src.data.utils import load_config
from src.main import run_pipeline

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Wildfire Risk MVP API",
    description="Run the NDVI-based wildfire risk pipeline and retrieve results.",
    version="1.0.0",
)

_last_run: dict = {}

BASE_DIR = Path(__file__).resolve().parents[1]

class RunRequest(BaseModel):
    region_name: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    cloud_cover_threshold: Optional[int] = None


class RunResponse(BaseModel):
    status: str
    map_path: str
    message: str

@app.get("/", summary="Health check")
def health_check():
    return {"status": "ok", "service": "Wildfire Risk MVP API"}


@app.post("/run", response_model=RunResponse, summary="Run the pipeline")
def run(request: RunRequest):
    try:
        config = load_config()

        if request.region_name:
            config["region"]["name"] = request.region_name
        if request.start_date:
            config["dates"]["start"] = request.start_date
        if request.end_date:
            config["dates"]["end"] = request.end_date
        if request.cloud_cover_threshold is not None:
            config["sentinel2"]["cloud_cover_threshold"] = request.cloud_cover_threshold

        map_path = run_pipeline(config)
        _last_run["map_path"] = map_path

        stats_path = BASE_DIR / "outputs" / "logs" / "area_stats.json"
        if stats_path.exists():
            with open(stats_path) as f:
                _last_run["stats"] = json.load(f)

        return RunResponse(
            status="success",
            map_path=map_path,
            message=f"Pipeline completed. Map saved to {map_path}",
        )

    except Exception as e:
        logger.exception("Pipeline failed")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/map", summary="Download the latest risk map")
def get_map():
    config = load_config()
    map_path = BASE_DIR / config["output"]["map_file"]

    if not map_path.exists():
        raise HTTPException(
            status_code=404,
            detail="No map found. Run the pipeline first via POST /run.",
        )

    return FileResponse(
        path=str(map_path),
        media_type="text/html",
        filename="wildfire_risk_map.html",
    )


@app.get("/stats", summary="Get last run area statistics")
def get_stats():
    stats = _last_run.get("stats")
    if not stats:
        raise HTTPException(
            status_code=404,
            detail="No statistics available. Run the pipeline first via POST /run.",
        )
    return JSONResponse(content=stats)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.app:app", host="0.0.0.0", port=8000, reload=True)
