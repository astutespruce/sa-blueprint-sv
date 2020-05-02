# South Atlantic Blueprint Simple Viewer - Data Prep

## Indicator and Threats within area of interest

Indicators and blueprint are aligned to the same grid

NOTE: threats are not aligned to the same grid; urbanization is on a 60m grid and SLR is 2-15m depending on area.

## Data

GeoTIFFs of the blueprint and all indicators were provided by SA staff for prior versions of the Blueprint Simple Viewer.

GeoTIFFs of the marine and inland hubs & corridors were provided by SA staff on 3/13/2020.

Urbanization grids were converted to indexed grids to simplify calculations. See `util/preprocess_grids.py`.

SA staff provided SLR files on 3/10/2020. These are a series of GeoTIFF files for small areas along the coast, with
varying footprints and resolution. To use here, we constructed a VRT using GDAL, and used the average resolution.

States were downloaded from: https://www.census.gov/cgi-bin/geo/shapefiles/index.php?year=2019&layergroup=States+%28and+equivalent%29

Counties were downloaded from: https://www.census.gov/cgi-bin/geo/shapefiles/index.php?year=2018&layergroup=Counties+%28and+equivalent%29

### Sea Level Rise

Data were obtained from Amy Keister on 3/10/2020. She exported individual
Geotiffs created from the source files created in her processing chain for
mosiacking SLR data obtained from NOAA (https://coast.noaa.gov/slrdata/).

Values are coded 0-6 for the amount of sea level rise that would impact a given
area. Values are cumulative, so a value of 6 means that the area is also
inundated by 1-5 meters.

A VRT is created from the individual source TIF files using GDAL.

From within `data/threats/slr` directory:

```
gdalbuildvrt -overwrite -resolution lowest slr.vrt *.tif
```

To assist with checking if a given area of interest overlaps SLR data, the
bounds of all SLR files are extracted to a dataset using
`util/extract_slr_bounds.py`.

## Tiles

### State boundaries

Used for overview map in report.

Rendered to vector tiles:

```bash
ogr2ogr -t_srs EPSG:4326 -f GeoJSONSeq -select STATEFP /tmp/states.json tl_2019_us_state.shp
tippecanoe -f -pg -z0 -z5 -o ../../../tiles/states.mbtiles -l states /tmp/states.json
```

### County boundaries

Used for finding local LTAs working in area on LTA Alliance website.

Extracted within South Atlantic region using `util/prep_boundaries.py`.

### Summary units

Summary units where consolidated using `util/prep_boundaries.py` then
converted to vector tiles using tippecanoe:

```
tippecanoe -f -pg -z 15 -o ./tiles/units.mbtiles -l "units" /tmp/units.geojson
```

### Region mask

Mask was created using `util/prep_boundaries.py` then converted to vector tiles using tippecanoe:

```
tippecanoe -f -pg -z 8 -o ./tiles/sa_mask.mbtiles -l "mask" /tmp/mask.geojson
```

### Ownership

TNC Secured Lands 2018 were downloaded from: https://www.conservationgateway.org/ConservationByGeography/NorthAmerica/UnitedStates/edc/reportsdata/terrestrial/secured/Pages/default.aspx
on 3/23/2020.

Render to vector tiles:

```
tippecanoe -f -pg -z 15 -o ./tiles/ownership.mbtiles -l "ownership" /tmp/ownership.geojson
```

### Merged tiles

```
tile-join -f -o ./tiles/sa_units.mbtiles ./tiles/sa_mask.mbtiles ./tiles/units.mbtiles
```
