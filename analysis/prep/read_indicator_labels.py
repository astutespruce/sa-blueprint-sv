from pathlib import Path

from pyogrio import read_dataframe


src_dir = Path("source_data/original_indicators")


for filename in src_dir.glob("*.tif.vat.dbf"):
    df = read_dataframe(filename, read_geometry=False).rename(
        columns={"descript": "description"}
    )
    if "description" in df.columns:
        # continuous indicators don't have descriptions
        df.description = df.description.apply(lambda x: x.split(" = ")[1])
        df[["Value", "description"]].to_csv(
            src_dir / f"{filename.name.split('.')[0]}_attributes.csv",
            index=False,
            header=False,
        )

