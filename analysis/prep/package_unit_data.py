"""
Extract summary unit data created using tabulate_area.py and postprocess to join
into vector tiles.

The following code compacts values in a few ways.  These were tested against
versions of the vector tiles that retained individual integer columns, and the
compacted version here ended up being smaller.

Time-series values (SLR, urban) were delta encoded, and combined with the analysis area into a string:
<shape_mask>/<acres at 0 ft>|<delta acres at 1ft>|<delta acres between 1ft and 2ft>|...

Values that could have multiple key:value entries (ownership, protection) are dictionary-encoded:
FED:<fed_acres>,LOC: <loc_acres>,...

Counties are encoded as:
<FIPS>|state|county,<FIPS>|...


"""

from pathlib import Path
import csv

import numpy as np
import pandas as pd
from geofeather.pygeos import from_geofeather


data_dir = Path("data/derived")

### HUC12
working_dir = data_dir / "huc12"
id_field = "HUC12"
units = pd.read_feather(
    working_dir / "huc12.feather", columns=["HUC12", "name", "acres"]
).set_index(id_field)
units.acres = units.acres.round().astype("uint")

blueprint = pd.read_feather(working_dir / "blueprint.feather").set_index(id_field)



# TODO: convert indicators actually present in a HUC12 into i1v1|i1v2|...,i2v1|i2v2|...

### Convert SLR and urban to integer acres, and delta encode
# values are encoded as:
# <shape_mask>/<acres at 0 ft>|<delta acres at 1ft>|<delta acres between 1ft and 2ft>|...
slr = (
    pd.read_feather(working_dir / "slr.feather")
    .set_index(id_field)
    .round()
    .astype("uint")
)
delta = slr[slr.columns[2:]].values - slr[slr.columns[1:-1]].values
slr = pd.Series(
    slr.shape_mask.astype(str)
    + "/"
    + slr["0"].astype(str)
    + "|"
    + np.apply_along_axis(lambda r: "|".join(str(v) for v in r), 1, delta),
    name="slr",
)

urban = (
    pd.read_feather(working_dir / "urban.feather")
    .set_index(id_field)
    .round()
    .astype("uint")
)
delta = urban[urban.columns[2:]].values - urban[urban.columns[1:-1]].values
urban = pd.Series(
    urban.shape_mask.astype(str)
    + "/"
    + urban.urban.astype(str)
    + "|"
    + np.apply_along_axis(lambda r: "|".join(str(v) for v in r), 1, delta),
    name="urban",
)


### Dictionary encode ownership and protection for each HUC12:
# FED:<fed_acres>,LOC: <loc_acres>, ...
ownership = pd.read_feather(working_dir / "ownership.feather").set_index(id_field)
ownership = pd.Series(
    (ownership.FEE_ORGTYP + ":" + ownership.acres.round().astype("uint").astype("str"))
    .groupby(level=0)
    .apply(lambda r: ",".join(v for v in r)),
    name="ownership",
)

protection = pd.read_feather(working_dir / "protection.feather").set_index(id_field)
protection = pd.Series(
    (
        protection.GAP_STATUS.astype("str")
        + ":"
        + protection.acres.round().astype("uint").astype("str")
    )
    .groupby(level=0)
    .apply(lambda r: ",".join(v for v in r)),
    name="protection",
)

### Convert counties into a string per HUC12, dividing fields by "|" and entries by ","
# <FIPS>|state|county,<FIPS>|...
counties = pd.Series(
    pd.read_feather(working_dir / "counties.feather")
    .set_index(id_field)
    .apply(lambda r: "|".join((str(v) for v in r.values)), axis=1)
    .groupby(level=0)
    .apply(lambda g: ",".join((v for v in g.values))),
    name="counties",
)


out = (
    units.join(slr, how="left")
    .join(urban, how="left")
    .join(ownership, how="left")
    .join(protection, how="left")
    .join(counties, how="left")
    .fillna("")
)

out.to_csv(
    working_dir / "tile_attributes.csv", index_label="id", quoting=csv.QUOTE_NONNUMERIC
)
