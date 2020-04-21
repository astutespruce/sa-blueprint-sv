# South Atlantic Conservation Blueprint Custom Reporting

Use case: user uploads shapefile (AOI) representing a small area, this generates a custom PDF report including maps and summaries of overlap with Blueprint and indicators.

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
tippecanoe -f -pg -z 15 -o ./tiles/units.mbtiles -l "units" ./data/summary_units/units.geojson
```

### Region mask

Mask was created using `util/prep_boundaries.py` then converted to vector tiles using tippecanoe:

```
tippecanoe -f -pg -z 8 -o ./tiles/sa_mask.mbtiles -l "mask" ./data/boundaries/mask.geojson
```

### Ownership

TNC Secured Lands 2018 were downloaded from: https://www.conservationgateway.org/ConservationByGeography/NorthAmerica/UnitedStates/edc/reportsdata/terrestrial/secured/Pages/default.aspx
on 3/23/2020.

Render to vector tiles:

```
tippecanoe -f -pg -z 15 -o ./tiles/ownership.mbtiles -l "ownership" ./data/boundaries/ownership.geojson
```

### Merged tiles

```
tile-join -f -o ./tiles/sa_units.mbtiles ./tiles/sa_mask.mbtiles ./tiles/units.mbtiles
```

## Installation issues

Weasyprint is used to generate PDF files. It depends on `cairocffi` which sometimes does not install correctly.

Run `pip install --no-cache-dir cairocffi` to correctly install it.

## API

### Starting background jobs and API server

Background jobs use `arq` which relies on `redis` installed on the host.

On MacOS, start `redis`:

```
redis-server /usr/local/etc/redis.conf
```

To start `arq` with reload capability:

```
arq api.worker.WorkerSettings --watch ./api
```

To start the API in development mode:

```
uvicorn api:app --reload --port 5000
```

### API requests

To make custom report requests using HTTPie:

```
http -f POST :5000/api/reports/custom/ name="<area name>" token=="<token from .env>" file@<filename>.zip
```

This creates a background job and returns:

```
{
    "job": "<job_id>"
}
```

To query job status:

```
http :5000/reports/status/<job_id>
```

To download PDF from a successful job:

```
http :5000/reports/results/<job_id>
```

This sets the `Content-Type` header to attachment and uses the passed-in name
for the filename.
