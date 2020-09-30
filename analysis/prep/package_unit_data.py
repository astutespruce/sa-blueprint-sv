"""
Extract summary unit data created using tabulate_area.py and postprocess to join
into vector tiles.

The following code compacts values in a few ways.  These were tested against
versions of the vector tiles that retained individual integer columns, and the
compacted version here ended up being smaller.

Blueprint and corridors were encoded to a pipe-delimited series of percents * 10
(to preserve 1 decimal place in frontend), omitting any 0 values:
<value0>|<value1>|...

Each indicator was encoded to a pipe-delimited series of percents * 10, then
any indicators present were merged into a single comma-delimited string.
Indicators that were not present were omitted.
Note: indicators are keyed based on their index within the indicators array;
this must be used in the frontend in same order and must remain in consistent
order.

Continuous indicators were encoded into an index:<avg> comma-delimited string.
Indicators that were not present were omitted (0 values are meaningful here).
All values are converted to integers.

Time-series values (SLR, urban) were converted to percent * 10 then delta encoded
into caret-delimited strings:
<baseline>^<delta_value0>^<delta_value1>

Areas where there were no values present were converted to empty strings.  Areas
where there was no change from the baseline just include the baseline.


Values that could have multiple key:value entries (ownership, protection) are dictionary-encoded:
FED:<fed_%>,LOC:<loc_%>,...

Counties are encoded as:
<FIPS>:state|county,<FIPS>|...


"""

from pathlib import Path
import csv

import numpy as np
import pandas as pd


from analysis.constants import INDICATOR_INDEX, URBAN_YEARS, DEBUG
from analysis.lib.attribute_encoding import encode_values, delta_encode_values


data_dir = Path("data")
results_dir = data_dir / "results"
out_dir = data_dir / "for_tiles"

### HUC12
working_dir = results_dir / "huc12"

print("Reading HUC12 units...")
huc12 = pd.read_feather(
    data_dir / "inputs/summary_units" / "huc12.feather", columns=["id", "name", "acres"]
).set_index("id")
huc12.acres = huc12.acres.round().astype("uint")
huc12["type"] = "subwatershed"


print("Encoding HUC12 Blueprint & indicator values...")
blueprint = pd.read_feather(results_dir / "huc12/blueprint.feather").set_index("id")

# Unpack blueprint values
blueprint_cols = [c for c in blueprint.columns if c.startswith("blueprint_")]
corridor_cols = [c for c in blueprint.columns if c.startswith("corridors_")]
blueprint_total = blueprint[blueprint_cols].sum(axis=1).rename("blueprint_total")
shape_mask = blueprint.shape_mask

# convert Blueprint to integer percents * 10, and pack into pipe-delimited string
blueprint_percent = encode_values(blueprint[blueprint_cols], shape_mask, 1000).rename(
    "blueprint"
)

# convert corridors to integer percents * 10, and pack into pipe-delimited string
corridors_percent = encode_values(blueprint[corridor_cols], shape_mask, 1000).rename(
    "corridors"
)

indicators = dict()
# serialized id is based on position
for i, id in enumerate(INDICATOR_INDEX.keys()):
    cols = [c for c in blueprint.columns if c.startswith(id) and not c.endswith("avg")]
    values = blueprint[cols]

    # drop indicators that are not present in this area
    # if only 0 values are present, ignore this indicator
    ix = values[cols[1:]].sum(axis=1) > 0
    indicators[i] = encode_values(values.loc[ix], shape_mask.loc[ix], 1000).rename(i)

# encode to dict-encoded value <i>:<percents>,...
# dropping any that are not present in a given record
indicators = (
    pd.DataFrame(indicators)
    .fillna("")
    .apply(lambda g: ",".join((f"{k}:{v}" for k, v in g.items() if v)), axis=1)
    .rename("indicators")
)

indicator_avgs = dict()
for i, id in enumerate(INDICATOR_INDEX.keys()):
    col = f"{id}_avg"
    if col in blueprint.columns:
        # all averages should be unsigned integer where present
        indicator_avgs[i] = blueprint[col].apply(
            lambda v: str(round(v)) if not pd.isnull(v) else ""
        )

indicator_avgs = (
    pd.DataFrame(indicator_avgs)
    .apply(lambda g: ",".join((f"{k}:{v}" for k, v in g.items() if v)), axis=1)
    .rename("indicator_avg")
)

blueprint_df = (
    blueprint[["shape_mask"]]
    .round()
    .astype("uint")
    .join(blueprint_total.round().astype("uint"))
    .join(blueprint_percent)
    .join(corridors_percent)
    .join(indicators)
    .join(indicator_avgs)
).fillna("")


### Convert SLR and urban to integer acres, and delta encode
print("Encoding SLR values...")
slr = (
    pd.read_feather(working_dir / "slr.feather").set_index("id").round().astype("uint")
)

slr = delta_encode_values(
    slr.drop(columns=["shape_mask"]), slr.shape_mask, 1000
).rename("slr")


print("Encoding urban values...")
urban = (
    pd.read_feather(working_dir / "urban.feather")
    .set_index("id")
    .round()
    .astype("uint")
)

urban = delta_encode_values(
    urban.drop(columns=["shape_mask"]), urban.shape_mask, 1000
).rename("urban")

### Dictionary encode ownership and protection for each HUC12:
# FED:<fed_acres>,LOC: <loc_acres>, ...
ownership = (
    pd.read_feather(working_dir / "ownership.feather")
    .set_index("id")
    .join(huc12.acres.rename("total_acres"))
)

ownership["percent"] = (
    (1000 * ownership.acres / ownership.total_acres).round().astype("uint")
)
# drop anything at 0%
ownership = ownership.loc[ownership.percent > 0].copy()

ownership = pd.Series(
    (ownership.FEE_ORGTYP + ":" + ownership.percent.astype("str"))
    .groupby(level=0)
    .apply(lambda r: ",".join(v for v in r)),
    name="ownership",
)

protection = (
    pd.read_feather(working_dir / "protection.feather")
    .set_index("id")
    .join(huc12.acres.rename("total_acres"))
)

protection["percent"] = (
    (1000 * protection.acres / protection.total_acres).round().astype("uint")
)
# drop anything at 0%
protection = protection.loc[protection.percent > 0].copy()


protection = pd.Series(
    (protection.GAP_STATUS.astype("str") + ":" + protection.percent.astype("str"))
    .groupby(level=0)
    .apply(lambda r: ",".join(v for v in r)),
    name="protection",
)

### Convert counties into a dict encoded string per HUC12,
# dividing state and county by "|" and entries by ","
# <FIPS>:state|county,
counties = pd.Series(
    pd.read_feather(working_dir / "counties.feather")
    .set_index("id")
    .apply(
        lambda r: ":".join([r.values[0], "|".join((str(v) for v in r.values[1:]))]),
        axis=1,
    )
    .groupby(level=0)
    .apply(lambda g: ",".join((v for v in g.values))),
    name="counties",
)


huc12 = (
    huc12.join(blueprint_df, how="left")
    .join(slr, how="left")
    .join(urban, how="left")
    .join(ownership, how="left")
    .join(protection, how="left")
    .join(counties, how="left")
    .fillna("")
)


### Read in marine data
working_dir = results_dir / "marine_blocks"

print("Reading marine_blocks...")
marine = pd.read_feather(
    data_dir / "inputs/summary_units/marine_blocks.feather",
    columns=["id", "name", "acres"],
).set_index("id")
marine.acres = marine.acres.round().astype("uint")
marine["type"] = "marine lease block"


print("Encoding marine Blueprint & indicator values...")
blueprint = pd.read_feather(working_dir / "blueprint.feather").set_index("id")

# Unpack blueprint values
blueprint_cols = [c for c in blueprint.columns if c.startswith("blueprint_")]
corridor_cols = [c for c in blueprint.columns if c.startswith("corridors_")]
blueprint_total = blueprint[blueprint_cols].sum(axis=1).rename("blueprint_total")
shape_mask = blueprint.shape_mask

# convert Blueprint to integer percents * 10, and pack into pipe-delimited string
blueprint_percent = encode_values(blueprint[blueprint_cols], shape_mask, 1000).rename(
    "blueprint"
)

# convert corridors to integer percents * 10, and pack into pipe-delimited string
corridors_percent = encode_values(blueprint[corridor_cols], shape_mask, 1000).rename(
    "corridors"
)

indicators = dict()
# serialized id is based on position
for i, id in enumerate(INDICATOR_INDEX.keys()):
    cols = [c for c in blueprint.columns if c.startswith(id) and not c.endswith("avg")]
    values = blueprint[cols]

    # drop indicators that are not present in this area
    # if only 0 values are present, ignore this indicator
    ix = values[cols[1:]].sum(axis=1) > 0
    indicators[i] = encode_values(values.loc[ix], shape_mask.loc[ix], 1000).rename(i)

# encode to dict-encoded value <i>:<percents>,...
# dropping any that are not present in a given record
indicators = (
    pd.DataFrame(indicators)
    .fillna("")
    .apply(lambda g: ",".join((f"{k}:{v}" for k, v in g.items() if v)), axis=1)
    .rename("indicators")
)

indicator_avgs = dict()
for i, id in enumerate(INDICATOR_INDEX.keys()):
    col = f"{id}_avg"
    if col in blueprint.columns:
        # all averages should be unsigned integer where present
        indicator_avgs[i] = blueprint[col].apply(
            lambda v: str(round(v)) if not pd.isnull(v) else ""
        )

indicator_avgs = (
    pd.DataFrame(indicator_avgs)
    .apply(lambda g: ",".join((f"{k}:{v}" for k, v in g.items() if v)), axis=1)
    .rename("indicator_avg")
)

blueprint_df = (
    blueprint[["shape_mask"]]
    .round()
    .astype("uint")
    .join(blueprint_total.round().astype("uint"))
    .join(blueprint_percent)
    .join(corridors_percent)
    .join(indicators)
    .join(indicator_avgs)
)

marine = marine.join(blueprint_df, how="left").fillna("")


out = (
    huc12.reset_index()
    .append(marine.reset_index(), ignore_index=True, sort=False)
    .fillna("")
)


if DEBUG:
    out.to_feather("/tmp/tile_attributes.feather")


out.to_csv(out_dir / "unit_atts.csv", index=False, quoting=csv.QUOTE_NONNUMERIC)
