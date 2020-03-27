from pathlib import Path

from geofeather import from_geofeather, to_geofeather


working_dir = Path("data/summary_units")

huc12 = from_geofeather(working_dir / "huc12_prj.feather")[
    ["HUC12", "geometry"]
].rename(columns={"HUC12": "id"})
marine = from_geofeather(working_dir / "marine_blocks_prj.feather")[["id", "geometry"]]

# TODO: simplify (slightly): try to get rid of overlaps between units

# Create consolidated summary units file as WGS84
df = (
    huc12.append(marine, ignore_index=True, sort=False)
    .reset_index(drop=True)
    .to_crs("EPSG:4326")
)
to_geofeather(df, working_dir / "units.feather")


# Create GeoJSONSeq file for vector tiles
df.to_file(working_dir / "units.geojson", driver="GeoJSONSeq")
