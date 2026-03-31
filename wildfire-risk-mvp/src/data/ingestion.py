import ee
import os
import logging
from src.data.utils import load_config

logger = logging.getLogger(__name__)


def initialize_gee(config: dict | None = None) -> None:
    project = None
    if config:
        project = config.get("gee", {}).get("project")

    if not project:
        project = os.getenv("EE_PROJECT") or os.getenv("GOOGLE_CLOUD_PROJECT")

    try:
        if project:
            ee.Initialize(project=project)
            logger.info(f"Google Earth Engine initialized successfully with project '{project}'.")
        else:
            ee.Initialize()
            logger.info("Google Earth Engine initialized successfully.")
    except Exception as e:
        if not project:
            logger.error(
                "GEE initialization failed: %s. Set gee.project in config/config.yaml "
                "or define EE_PROJECT/GOOGLE_CLOUD_PROJECT.",
                e,
            )
        else:
            logger.error(f"GEE initialization failed for project '{project}': {e}")
        raise


def get_sentinel2_collection(config: dict) -> ee.ImageCollection:
    bbox = config["region"]["bbox"]
    aoi = ee.Geometry.Rectangle(
        [bbox["west"], bbox["south"], bbox["east"], bbox["north"]]
    )

    start_date = config["dates"]["start"]
    end_date = config["dates"]["end"]
    cloud_threshold = config["sentinel2"]["cloud_cover_threshold"]
    collection_id = config["sentinel2"]["collection"]

    logger.info(
        f"Fetching {collection_id} from {start_date} to {end_date} "
        f"over {config['region']['name']} (cloud <= {cloud_threshold}%)"
    )

    collection = (
        ee.ImageCollection(collection_id)
        .filterBounds(aoi)
        .filterDate(start_date, end_date)
        .filter(ee.Filter.lte("CLOUDY_PIXEL_PERCENTAGE", cloud_threshold))
    )

    count = collection.size().getInfo()
    logger.info(f"Found {count} images after filtering.")

    if count == 0:
        raise ValueError(
            "No images found for the specified region, dates, and cloud threshold. "
            "Try relaxing the cloud cover threshold or expanding the date range."
        )

    return collection, aoi


def get_median_composite(collection: ee.ImageCollection, aoi: ee.Geometry) -> ee.Image:
    composite = collection.median().clip(aoi)
    logger.info("Median composite created.")
    return composite


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    config = load_config()
    initialize_gee(config)
    collection, aoi = get_sentinel2_collection(config)
    composite = get_median_composite(collection, aoi)
    print("Composite image bands:", composite.bandNames().getInfo())
