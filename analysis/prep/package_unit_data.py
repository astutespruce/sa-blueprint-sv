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
FED:<fed_acres>,LOC:<loc_acres>,...

Counties are encoded as:
<FIPS>|state|county,<FIPS>|...


"""

from pathlib import Path
import csv

import numpy as np
import pandas as pd


from analysis.constants import INDICATOR_INDEX, URBAN_YEARS


def encode_values(df, total, scale=100):
    """Convert a dataframe from acres to integer scalar values:
    scale * value / total

    This can be used to express percent where scale = 100

    Values are packed into a pipe-delimited string with 0 values omitted, e.g.,
    '10|20|70||'

    Parameters
    ----------
    df : DataFrame
        Note: only includes columns to be divided by total.
    total : number
        Must be greater than 0.

    Returns
    -------
    Series
        Contains string for each record with pipe-delimited values.  If
        max encoded value across all bins is 0, an empty string is returned instead.
    """
    return (
        (scale * df.divide(total, axis=0))
        .round()
        .astype("uint")
        .apply(lambda r: "|".join(str(v or "") for v in r) if r.max() else "", axis=1)
    )


def delta_encode_values(df, total, scale=100):
    """Convert a dataframe from acres to delta-encoded integer scalar values,
    where original values are first scaled.

    This can be used to express percent where scale = 100.

    Values are packed into a caret-delimited string with 0 values omitted, e.g.,
    '<baseline_value>^<delta_value1>^<delta_value2>...'

    If there is no change from the baseline value, only that value is returned

    Parameters
    ----------
    df : DataFrame
        Note: only includes columns to be divided by total.
    total : number
        Must be greater than 0.

    Returns
    -------
    Series
        Contains string for each record with caret-delimited values.  If
        max encoded value across all bins is 0, an empty string is returned instead.
    """
    scaled = (scale * df.divide(total, axis=0)).round().astype("uint")

    # calculate delta values
    delta = scaled[scaled.columns[1:]].subtract(
        scaled[scaled.columns[:-1]].values, axis=0
    )

    # caret must be escaped
    nochange = "\^" * len(delta.columns)

    return (
        scaled[[scaled.columns[0]]]
        .join(delta)
        .apply(lambda r: "^".join(str(v or "") for v in r) if r.max() else "", axis=1)
        .str.replace(nochange, "")
    )


data_dir = Path("data")
results_dir = data_dir / "results"

### HUC12
working_dir = results_dir / "huc12"

print("Reading HUC12 units...")
huc12 = pd.read_feather(
    data_dir / "inputs/summary_units" / "huc12.feather", columns=["id", "name", "acres"]
).set_index("id")
huc12.acres = huc12.acres.round().astype("uint")


print("Encoding HUC12 Blueprint & indicator values...")
blueprint = pd.read_feather(results_dir / "huc12/blueprint.feather").set_index("id")

# Unpack blueprint values
blueprint_cols = [c for c in blueprint.columns if c.startswith("blueprint_")]
corridor_cols = [c for c in blueprint.columns if c.startswith("corridors_")]
blueprint_total = blueprint[blueprint_cols].sum(axis=1).rename("blueprint_total")

# convert Blueprint to integer percents * 10, and pack into pipe-delimited string
blueprint_percent = encode_values(
    blueprint[blueprint_cols], blueprint_total, 1000
).rename("blueprint")

# convert corridors to integer percents * 10, and pack into pipe-delimited string
corridors_percent = encode_values(
    blueprint[corridor_cols], blueprint_total, 1000
).rename("corridors")

indicators = dict()
# serialized id is based on position
for i, id in enumerate(INDICATOR_INDEX.keys()):
    cols = [c for c in blueprint.columns if c.startswith(id) and not c.endswith("avg")]
    indicators[i] = encode_values(blueprint[cols], blueprint_total, 1000).rename(i)

# encode to dict-encoded value <i>:<percents>,...
# dropping any that are not present in a given record
indicators = (
    pd.DataFrame(indicators)
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
    .rename("indicator_avgs")
)

blueprint_df = (
    pd.DataFrame(blueprint_total.round().astype("uint"))
    .join(blueprint_percent)
    .join(corridors_percent)
    .join(indicators)
    .join(indicator_avgs)
)


### Convert SLR and urban to integer acres, and delta encode
print("Encoding SLR values...")
slr = (
    pd.read_feather(working_dir / "slr.feather").set_index("id").round().astype("uint")
)

slr = delta_encode_values(slr.drop(columns=["shape_mask"]), slr.shape_mask, 1000)


print("Encoding urban values...")
urban = (
    pd.read_feather(working_dir / "urban.feather")
    .set_index("id")
    .round()
    .astype("uint")
)

urban = delta_encode_values(urban.drop(columns=["shape_mask"]), urban.shape_mask, 1000)

### Dictionary encode ownership and protection for each HUC12:
# FED:<fed_acres>,LOC: <loc_acres>, ...
ownership = pd.read_feather(working_dir / "ownership.feather").set_index("id")
ownership = pd.Series(
    (ownership.FEE_ORGTYP + ":" + ownership.acres.round().astype("uint").astype("str"))
    .groupby(level=0)
    .apply(lambda r: ",".join(v for v in r)),
    name="ownership",
)

protection = pd.read_feather(working_dir / "protection.feather").set_index("id")
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
    .set_index("id")
    .apply(lambda r: "|".join((str(v) for v in r.values)), axis=1)
    .groupby(level=0)
    .apply(lambda g: ",".join((v for v in g.values))),
    name="counties",
)


out = (
    huc12.join(blueprint_df, how="left")
    .join(slr, how="left")
    .join(urban, how="left")
    .join(ownership, how="left")
    .join(protection, how="left")
    .join(counties, how="left")
    .fillna("")
)

out.to_csv(
    working_dir / "tile_attributes.csv", index_label="id", quoting=csv.QUOTE_NONNUMERIC
)


### TODO: marine
