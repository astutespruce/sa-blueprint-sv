#!/bin/bash

TMPDIR="/tmp"
TILEDIR="tiles"
DATADIR="data"

# Create tiles from summary units
echo "Processing summary units..."
# ogr2ogr -f GeoJSONSeq $TMPDIR/units.geojson $DATADIR/summary_units/units.gpkg units -progress
# tippecanoe -f -pg -P -Z 8 -z 14 -ai -o $TMPDIR/units.mbtiles -l "units" $TMPDIR/units.geojson

# Create tiles from boundary and mask
echo "Processing boundary..."
# ogr2ogr -f GeoJSONSeq $TMPDIR/sa_mask.geojson $DATADIR/boundaries/sa_mask.gpkg sa_mask -progress
# tippecanoe -f -pg -P -Z 0 -z 8 -ai -o $TMPDIR/sa_mask.mbtiles -l "mask" $TMPDIR/sa_mask.geojson

# ogr2ogr -f GeoJSONSeq $TMPDIR/sa_boundary.geojson $DATADIR/boundaries/sa_boundary.gpkg sa_boundary -progress
# tippecanoe -f -pg -P -Z 0 -z 8 -ai -o $TMPDIR/sa_boundary.mbtiles -l "boundary" $TMPDIR/sa_boundary.geojson


# TODO: merge tiles




# Create tiles from states
echo "Processing states..."
# ogr2ogr -t_srs EPSG:4326 -f GeoJSONSeq -select STATEFP $TMPDIR/states.geojson source_data/boundaries/tl_2019_us_state.shp
# tippecanoe -f -pg -Z 0 -z 5 -o $TILEDIR/states.mbtiles -l states /tmp/states.geojson


# Create tiles from protected areas
echo "Processing protected areas..."
ogr2ogr -t_srs EPSG:4326 -f GeoJSONSeq $TMPDIR/ownership.geojson $DATADIR/boundaries/ownership.gpkg -progress
tippecanoe -f -pg -z 15 -o $TILEDIR/ownership.mbtiles -l "ownership" $TMPDIR/ownership.geojson
