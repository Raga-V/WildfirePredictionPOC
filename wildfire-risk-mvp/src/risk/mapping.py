import ee
import logging

logger = logging.getLogger(__name__)

RISK_HIGH = 3
RISK_MODERATE = 2
RISK_LOW = 1

RISK_LABELS = {
    RISK_HIGH: "High",
    RISK_MODERATE: "Moderate",
    RISK_LOW: "Low",
}


def classify_ndvi_to_risk(ndvi_image: ee.Image, config: dict) -> ee.Image:
    thresholds = config["ndvi"]["thresholds"]
    low_min = thresholds["low_risk_min"]
    mod_min = thresholds["moderate_risk_min"]

    ndvi = ndvi_image.select("NDVI")

    risk = (
        ee.Image(RISK_HIGH)
        .where(ndvi.gte(mod_min), RISK_MODERATE)
        .where(ndvi.gte(low_min), RISK_LOW)
        .rename("risk")
        .updateMask(ndvi_image.select("NDVI").mask())
    )

    logger.info(
        f"Risk classification applied. Thresholds -> High: NDVI < {mod_min}, "
        f"Moderate: {mod_min} to {low_min}, Low: NDVI >= {low_min}"
    )
    return risk


def risk_to_geojson(
    risk_image: ee.Image,
    aoi: ee.Geometry,
    scale: int = 500,
    max_features: int = 4000,
    seed: int = 42,
) -> dict:
    sample = risk_image.sample(
        region=aoi,
        scale=scale,
        geometries=True,
        numPixels=max_features,
        seed=seed,
        tileScale=4,
    )
    sample = sample.limit(max_features)

    geojson = sample.getInfo()
    feature_count = len(geojson.get("features", []))
    logger.info(f"Sampled {feature_count} risk points from the classified image.")
    return geojson


def get_risk_area_stats(
    risk_image: ee.Image, aoi: ee.Geometry, scale: int = 100
) -> dict:
    freq = risk_image.reduceRegion(
        reducer=ee.Reducer.frequencyHistogram(),
        geometry=aoi,
        scale=scale,
        maxPixels=1e9,
    ).getInfo()

    raw = freq.get("risk", {})
    stats = {RISK_LABELS.get(int(k), k): v for k, v in raw.items()}
    logger.info(f"Risk area statistics: {stats}")
    return stats
