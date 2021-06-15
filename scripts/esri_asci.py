"""ESRI asci-file from Rasterio, Numpy and Pandas, including processing time."""

import rasterio
from pathlib import Path
import numpy as np
import copy
import pandas as pd
import datetime

data_path = Path(r"../data")
source_path = data_path.joinpath("de_tol")
dem_tif = source_path.joinpath("dem_kockengen_20160905.tif")
dst_path = data_path.joinpath("dem_test")
dst_path.mkdir(parents=True, exist_ok=True)
asc_nodata = -99


start = datetime.datetime.now()
with rasterio.open(dem_tif) as src:
    profile = src.profile
    data = src.read(1)
    dem_res = copy.copy(src.res[0])


print(f"Read DEM in: {(datetime.datetime.now() - start).seconds} secs")
data[data == profile["nodata"]] = asc_nodata
profile["driver"] = "AAIGrid"
profile["nodata"] = asc_nodata

# %%
header = f"""ncols {profile['width']}
nrows {profile['height']}
xllcorner {src.bounds.left}
yllcorner {src.bounds.bottom}
cellsize {dem_res}
NODATA_value {asc_nodata:.2f}"""

# %% via rasterio
start = datetime.datetime.now()

rio_asc = dst_path.joinpath("using_rasterio.asc")
with rasterio.open(rio_asc, "w+", **profile) as dst:
    dst.write(data, 1)

print(f"Rasterio: {(datetime.datetime.now() - start).seconds} secs")

# %% via numpy
start = datetime.datetime.now()
np_asc = dst_path.joinpath("using_numpy.asc")
np.savetxt(np_asc,
           data,
           fmt='%.2f',
           delimiter=' ',
           newline='\n',
           header=header,
           comments='')

print(f"Numpy: {(datetime.datetime.now() - start).seconds} secs")

# %% via pandas
start = datetime.datetime.now()
pd_asc = dst_path.joinpath("using_pandas.asc")
pd_asc.write_text(f"{header}\n")
df = pd.DataFrame(data)
df.to_csv(pd_asc,
          sep=" ",
          header=False,
          index=False,
          mode="a",
          float_format='%.2f')

print(f"Pandas: {(datetime.datetime.now() - start).seconds} secs")
