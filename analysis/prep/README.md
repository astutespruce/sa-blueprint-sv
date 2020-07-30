# South Atlantic Blueprint Simple Viewer - Data Prep

## Data

GeoTIFFs of the blueprint and all indicators were provided by SA staff on 7/27/2020.
GeoTIFFs of the marine and inland hubs & corridors were provided by SA staff on 3/13/2020.

Other data were downloaded as described below.

### SA Blueprint analysis extent

### Blueprint & indicators

Most indicators and the Blueprint are mapped at a resolution of 30m.

The 3 marine and 1 estuarine indicators were originally mapped at 200m. These were
resampled to 30m for consistency with the other indicators.

### Summary units

Blueprint data were summarized to HUC12 subwatersheds and marine lease blocks.

HUC12 subwatershed boundaries were downloaded for WBD_02, WBD_03, WBD_05, WBD_06 from: http://prd-tnm.s3-website-us-west-2.amazonaws.com/?prefix=StagedProducts/Hydrography/WBD/HU2/GDB/
on 7/24/2020.

HUC12 units that fell within the SA Blueprint boundary were selected from these datasets.

Marine lease blocks were carried over from Blueprint 2.2.

Summary units were prepared using `analysis/prepare_summary_units.py`. This script extracted the summary units and created two sets outputs for each, plus an aggregated
dataset for tile creation:

-   `/summary_units/<huc12|marine_blocks>.feather` are the projected datasets for use in spatial analysis
-   `/results/<huc12|marine_blocks>/<huc12|marine_blocks>_wgs84.feather` are the WGS84 versions for use in mapping
-   `/summary_units/units_wgs84.gpkg` is the combined WGS 84 units for tile creation.

### States and counties

State and county information is used to determine which land trusts may be active
in a given subwatershed. State boundaries are used in the locator map in the report.

States were downloaded from: https://www.census.gov/cgi-bin/geo/shapefiles/index.php?year=2019&layergroup=States+%28and+equivalent%29

Counties were downloaded from: https://www.census.gov/cgi-bin/geo/shapefiles/index.php?year=2018&layergroup=Counties+%28and+equivalent%29

Processed using `util/prepare_boundaries.py`.

### Land ownership

TNC Secured Lands 2018 were downloaded from: https://www.conservationgateway.org/ConservationByGeography/NorthAmerica/UnitedStates/edc/reportsdata/terrestrial/secured/Pages/default.aspx
on 3/23/2020.

Processed using `util/prepare_boundaries.py`.

### Projected urbanization

NOTE: this is not aligned to the blueprint grid.

Urbanization grids were converted to indexed grids to simplify calculations. See `util/preprocess_grids.py`.

### Sea Level Rise

NOTE: this is not aligned to the blueprint grid.

Data were obtained from Amy Keister on 3/10/2020. She exported individual
Geotiffs created from the source files created in her processing chain for
mosiacking SLR data obtained from NOAA (https://coast.noaa.gov/slrdata/).

These are a series of GeoTIFF files
for small areas along the coast, with varying footprints and resolution. To use
here, we constructed a VRT using GDAL, and used the average resolution.

Values are coded 0-6 for the amount of sea level rise that would impact a given
area. Values are cumulative, so a value of 6 means that the area is also
inundated by 1-5 meters.

From within `data/threats/slr` directory:

```
gdalbuildvrt -overwrite -resolution lowest slr.vrt *.tif
```

To assist with checking if a given area of interest overlaps SLR data, the
bounds of all SLR files are extracted to a dataset using
`util/extract_slr_bounds.py`.

### Merged tiles

```
tile-join -f -pg -o ./tiles/sa_units.mbtiles ./tiles/sa_mask.mbtiles ./tiles/units.mbtiles
```

################ In progress

Create tile attributes for each summary unit in `package_unit_data.py`.

NOTE: unit are not shown in the map below Z10 (`-Z 8 -z 14`)

Attach to units:

```
tile-join -f -pg -o ./tiles/units_atts.mbtiles ./tiles/units.mbtiles -c ./data/derived/huc12/tile_attributes.csv
```
