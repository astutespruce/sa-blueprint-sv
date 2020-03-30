# South Atlantic Conservation Blueprint Custom Reporting

Use case: user uploads shapefile (AOI) representing a small area, this generates a custom PDF report including maps and summaries of overlap with Blueprint and indicators.

## Indicator and Threats within area of interest

Indicators and blueprint are aligned to the same grid

NOTE: threats are not aligned to the same grid; urbanization is on a 60m grid and SLR is 2-15m depending on area.

## Data

GeoTIFFs of the blueprint and all indicators were provided by SA staff for prior versions of the Blueprint Simple Viewer.

Urbanization grids were converted to indexed grids to simplify calculations. See `util/preprocess_grids.py`.

SA staff provided SLR files on 3/10/2020. These are a series of GeoTIFF files for small areas along the coast, with
varying footprints and resolution. To use here, we constructed a VRT using GDAL, and used the average resolution.

TNC Secured Lands 2018 were downloaded from: https://www.conservationgateway.org/ConservationByGeography/NorthAmerica/UnitedStates/edc/reportsdata/terrestrial/secured/Pages/default.aspx
on 3/23/2020.

## Tiles

### State boundaries

Used for overview map in report.

Downloaded from: https://www.census.gov/cgi-bin/geo/shapefiles/index.php?year=2019&layergroup=States+%28and+equivalent%29

Rendered to vector tiles:

```bash
ogr2ogr -t_srs EPSG:4326 -f GeoJSONSeq -select STATEFP /tmp/states.json tl_2019_us_state.shp
tippecanoe -f -pg -z0 -z5 -o ../../../tiles/states.mbtiles -l states /tmp/states.json
```

### Summary units

Summary units where consolidated using `util/prep_summary_units.py` then
converted to vector tiles using tippecanoe:

```
tippecanoe -f -pg -z 15 -o ./tiles/units.mbtiles -l "units" ./data/summary_units/units.geojson
```

### Region mask

Mask was created using `util/prep_summary_units.py` then converted to vector tiles using tippecanoe:

```
tippecanoe -f -pg -z 8 -o ./tiles/sa_mask.mbtiles -l "mask" ./data/boundaries/mask.geojson
```

### Merged tiles

```
tile-join -f -o ./tiles/sa_units.mbtiles ./tiles/sa_mask.mbtiles ./tiles/units.mbtiles
```
