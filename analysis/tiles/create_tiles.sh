#!/bin/bash

TMPDIR="/tmp"
TILEDIR="tiles"
TILEINPUTS="data/for_tiles"


# Create tiles from states
echo "Processing states..."
ogr2ogr -t_srs EPSG:4326 -f GeoJSONSeq -select STATEFP $TMPDIR/states.geojson source_data/boundaries/tl_2020_us_state.shp
tippecanoe -f -pg -Z 0 -z 5 --detect-shared-borders -o $TILEDIR/states.mbtiles -l states /tmp/states.geojson

# Create tiles from protected areas
echo "Processing protected areas..."
tippecanoe -f -pg -P -z 15 --detect-shared-borders -o $TILEDIR/sa_ownership.mbtiles -l "ownership" $TILEINPUTS/ownership.geojson

# NOTE: mask is only used for backend reports and never zoomed very far
tippecanoe -f -pg -P -Z 0 -z 8 -ai -o $TILEDIR/sa_mask.mbtiles -l "mask" $TILEINPUTS/sa_mask.geojson

# Create tiles from summary units
echo "Processing summary units..."
tippecanoe -f -pg -P -Z 7 -z 14 --detect-shared-borders -ai -o $TMPDIR/units.mbtiles -l "units" $TILEINPUTS/units.geojson

# Merge in attributes
tile-join -f -pg -o $TMPDIR/unit_atts.mbtiles $TMPDIR/units.mbtiles -c $TILEINPUTS/unit_atts.csv


# Create tiles from boundary
echo "Processing boundary..."
tippecanoe -f -pg -P -Z 0 -z 14 -ai -o $TMPDIR/sa_boundary.mbtiles -l "boundary" $TILEINPUTS/sa_boundary.geojson


# Join units and boundaries together
echo "Merging tilesets..."
tile-join -f -pg -o $TILEDIR/sa_map_units.mbtiles $TMPDIR/sa_boundary.mbtiles $TMPDIR/unit_atts.mbtiles
