#!/bin/bash

TMPDIR="/tmp"
TILEDIR="tiles"
TILEINPUTS="data/for_tiles"

# Create tiles from summary units
echo "Processing summary units..."
tippecanoe -f -pg -P -Z 8 -z 14 -ai -o $TMPDIR/units.mbtiles -l "units" $TILEINPUTS/units.geojson

# TODO: merge tiles with attributes






# Create tiles from boundary and mask
echo "Processing boundary..."
tippecanoe -f -pg -P -Z 0 -z 8 -ai -o $TMPDIR/sa_mask.mbtiles -l "mask" $TILEINPUTS/sa_mask.geojson
tippecanoe -f -pg -P -Z 0 -z 8 -ai -o $TMPDIR/sa_boundary.mbtiles -l "boundary" $TILEINPUTS/sa_boundary.geojson


# Join units and boundaries together
# FIXME: use output of merge with attributes above for units
echo "Merging tilesets..."
tile-join -f -pg -o $TILEDIR/map_units.mbtiles $TMPDIR/sa_mask.mbtiles $TMPDIR/sa_boundary.mbtiles $TMPDIR/units.mbtiles



# Create tiles from states
echo "Processing states..."
ogr2ogr -t_srs EPSG:4326 -f GeoJSONSeq -select STATEFP $TMPDIR/states.geojson source_data/boundaries/tl_2019_us_state.shp
tippecanoe -f -pg -Z 0 -z 5 -o $TILEDIR/states.mbtiles -l states /tmp/states.geojson


# Create tiles from protected areas
echo "Processing protected areas..."
tippecanoe -f -pg -P -z 15 -o $TILEDIR/ownership.mbtiles -l "ownership" $TILEINPUTS/ownership.geojson
