import ee
import logging

logger = logging.getLogger(__name__)


def mask_s2_clouds(image: ee.Image) -> ee.Image:
    qa = image.select("QA60")

    cloud_bit_mask = 1 << 10
    cirrus_bit_mask = 1 << 11

    mask = (
        qa.bitwiseAnd(cloud_bit_mask).eq(0)
        .And(qa.bitwiseAnd(cirrus_bit_mask).eq(0))
    )

    return image.updateMask(mask).divide(10000).copyProperties(
        image, ["system:time_start"]
    )


def apply_cloud_masking(collection: ee.ImageCollection) -> ee.ImageCollection:
    masked = collection.map(mask_s2_clouds)
    logger.info("Cloud masking applied to image collection.")
    return masked


def select_bands(image: ee.Image, bands: list[str]) -> ee.Image:
    return image.select(bands)


def preprocess_collection(
    collection: ee.ImageCollection, config: dict
) -> ee.ImageCollection:
    nir_band = config["sentinel2"]["bands"]["nir"]
    red_band = config["sentinel2"]["bands"]["red"]

    masked = apply_cloud_masking(collection)
    processed = masked.map(lambda img: select_bands(img, [red_band, nir_band, "QA60"]))
    logger.info(f"Preprocessing complete. Selected bands: {red_band}, {nir_band}.")
    return processed
