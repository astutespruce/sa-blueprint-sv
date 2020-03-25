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
