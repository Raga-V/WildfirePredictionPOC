import ee
import logging

logger = logging.getLogger(__name__)


def compute_ndvi(image: ee.Image, nir_band: str = "B8", red_band: str = "B4") -> ee.Image:
    ndvi = image.normalizedDifference([nir_band, red_band]).rename("NDVI")
    return image.addBands(ndvi)


def compute_ndvi_composite(
    composite: ee.Image, config: dict
) -> ee.Image:
    nir_band = config["sentinel2"]["bands"]["nir"]
    red_band = config["sentinel2"]["bands"]["red"]

    ndvi_image = compute_ndvi(composite, nir_band=nir_band, red_band=red_band)
    logger.info(f"NDVI computed using bands NIR={nir_band}, Red={red_band}.")
    return ndvi_image


def get_ndvi_statistics(ndvi_image: ee.Image, aoi: ee.Geometry) -> dict:
    stats = ndvi_image.select("NDVI").reduceRegion(
        reducer=ee.Reducer.mean()
            .combine(ee.Reducer.min(), sharedInputs=True)
            .combine(ee.Reducer.max(), sharedInputs=True)
            .combine(ee.Reducer.stdDev(), sharedInputs=True),
        geometry=aoi,
        scale=10,
        maxPixels=1e9,
    )
    result = stats.getInfo()
    logger.info(f"NDVI statistics: {result}")
    return result
