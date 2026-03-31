import os
import logging
import folium
from folium.plugins import MiniMap, Fullscreen
from src.data.utils import get_center

logger = logging.getLogger(__name__)

RISK_STYLE = {
    1: {"label": "Low Risk",      "color": "#00cc44"},
    2: {"label": "Moderate Risk", "color": "#ffaa00"},
    3: {"label": "High Risk",     "color": "#cc0000"},
}


def _to_risk_class(raw_risk) -> int:
    try:
        risk_val = int(raw_risk)
    except (TypeError, ValueError):
        return 3
    return risk_val if risk_val in RISK_STYLE else 3


def _render_risk_points(m: folium.Map, geojson_data: dict) -> None:
    features = geojson_data.get("features", [])
    layer = folium.FeatureGroup(name="Wildfire Risk")

    for feature in features:
        geometry = feature.get("geometry", {})
        if geometry.get("type") != "Point":
            continue

        coords = geometry.get("coordinates", [])
        if len(coords) != 2:
            continue

        lon, lat = coords
        properties = feature.get("properties", {})
        risk_class = _to_risk_class(properties.get("risk"))
        style = RISK_STYLE[risk_class]
        tooltip = f"Risk Class: {style['label']} ({risk_class})"

        folium.CircleMarker(
            location=[lat, lon],
            radius=4,
            color=style["color"],
            fill=True,
            fill_color=style["color"],
            fill_opacity=0.8,
            weight=0.8,
            tooltip=tooltip,
        ).add_to(layer)

    layer.add_to(m)


def build_risk_map(
    geojson_data: dict,
    config: dict,
    area_stats: dict | None = None,
) -> folium.Map:
    bbox = config["region"]["bbox"]
    center_lat, center_lon = get_center(bbox)
    region_name = config["region"]["name"]

    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=9,
        tiles="CartoDB positron",
    )

    _render_risk_points(m, geojson_data)

    legend_html = (
        "<div style=\""
        "position: fixed; bottom: 40px; left: 40px; z-index: 1000;"
        "background-color: white; padding: 12px 16px; border-radius: 8px;"
        "border: 2px solid #ccc; font-family: Arial, sans-serif; font-size: 13px;"
        "box-shadow: 2px 2px 6px rgba(0,0,0,0.3);"
        "\">"
        "<b>🔥 Wildfire Risk</b><br>"
        "<i style=\"background:#cc0000;width:14px;height:14px;display:inline-block;border-radius:3px;margin-right:6px;\"></i> High Risk<br>"
        "<i style=\"background:#ffaa00;width:14px;height:14px;display:inline-block;border-radius:3px;margin-right:6px;\"></i> Moderate Risk<br>"
        "<i style=\"background:#00cc44;width:14px;height:14px;display:inline-block;border-radius:3px;margin-right:6px;\"></i> Low Risk"
        "</div>"
    )
    m.get_root().html.add_child(folium.Element(legend_html))

    title_html = (
        "<div style=\""
        "position: fixed; top: 14px; left: 50%; transform: translateX(-50%);"
        "z-index: 1000; background: white; padding: 8px 20px; border-radius: 6px;"
        "border: 1px solid #aaa; font-family: Arial, sans-serif; font-size: 15px;"
        "font-weight: bold; box-shadow: 1px 1px 4px rgba(0,0,0,0.2);"
        "\">"
        f"🌍 Wildfire Risk Map — {region_name}"
        "</div>"
    )
    m.get_root().html.add_child(folium.Element(title_html))

    if area_stats:
        rows = "".join(
            f"<tr><td style='padding:2px 8px'>{k}</td>"
            f"<td style='padding:2px 8px;text-align:right'>{v:,}</td></tr>"
            for k, v in area_stats.items()
        )
        stats_html = (
            "<div style=\""
            "position: fixed; bottom: 40px; right: 40px; z-index: 1000;"
            "background: white; padding: 10px 14px; border-radius: 8px;"
            "border: 2px solid #ccc; font-family: Arial, sans-serif; font-size: 13px;"
            "box-shadow: 2px 2px 6px rgba(0,0,0,0.3);"
            "\">"
            "<b>Area Statistics (pixels)</b>"
            f"<table style=\"margin-top:6px\">{rows}</table>"
            "</div>"
        )
        m.get_root().html.add_child(folium.Element(stats_html))

    MiniMap(toggle_display=True).add_to(m)
    Fullscreen().add_to(m)
    folium.LayerControl().add_to(m)

    logger.info(f"Folium map built for region: {region_name}")
    return m


def save_map(fmap: folium.Map, output_path: str) -> None:
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    fmap.save(output_path)
    logger.info(f"Map saved to: {output_path}")
    print(f"  Map saved -> {output_path}")
