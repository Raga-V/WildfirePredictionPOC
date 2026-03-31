import logging
from src.data.utils import load_config, setup_logging
from src.data.ingestion import initialize_gee, get_sentinel2_collection, get_median_composite
from src.data.preprocessing import preprocess_collection
from src.features.ndvi import compute_ndvi_composite, get_ndvi_statistics
from src.risk.mapping import classify_ndvi_to_risk, risk_to_geojson, get_risk_area_stats
from src.visualization.map import build_risk_map, save_map

logger = logging.getLogger(__name__)


def run_pipeline(config: dict | None = None) -> str:
    if config is None:
        config = load_config()

    log_file = config["output"]["log_file"]
    setup_logging(log_file=log_file)
    logger.info("=== Wildfire Risk MVP Pipeline Started ===")

    logger.info("[Step 1/5] Ingesting Sentinel-2 imagery...")
    initialize_gee(config)
    raw_collection, aoi = get_sentinel2_collection(config)

    logger.info("[Step 2/5] Preprocessing: cloud masking + band selection...")
    processed_collection = preprocess_collection(raw_collection, config)
    composite = get_median_composite(processed_collection, aoi)

    logger.info("[Step 3/5] Computing NDVI...")
    ndvi_image = compute_ndvi_composite(composite, config)
    stats = get_ndvi_statistics(ndvi_image, aoi)
    logger.info(f"NDVI Stats: {stats}")

    logger.info("[Step 4/5] Classifying NDVI into risk categories...")
    risk_image = classify_ndvi_to_risk(ndvi_image, config)
    risk_cfg = config.get("risk", {})
    geojson_data = risk_to_geojson(
        risk_image,
        aoi,
        scale=risk_cfg.get("geojson_sample_scale", 500),
        max_features=risk_cfg.get("geojson_max_features", 4000),
    )
    area_stats = get_risk_area_stats(risk_image, aoi)

    logger.info("[Step 5/5] Generating wildfire risk map...")
    risk_map = build_risk_map(geojson_data, config, area_stats=area_stats)
    output_path = config["output"]["map_file"]
    save_map(risk_map, output_path)

    logger.info(f"=== Pipeline Complete. Map saved to: {output_path} ===")
    return output_path


if __name__ == "__main__":
    result_path = run_pipeline()
    print(f"\nDone! Open your risk map at: {result_path}")
