# -*- coding: utf-8 -*-
"""
Created on Mon Dec 20 09:39:08 2021

@author: danie
"""

from fortio import FortranFile
import geopandas as gpd
import pandas as pd

level_file = r"../data/de_tol_small/case1/flows/ts/waterlevels2d.dat"
grid_file = r"../data/de_tol_small/case1/grids/grid.gpkg"
ts_file = r"../data/de_tol_small/case1/flows/ts/timesteps.asc"

mesh_df = gpd.read_file(grid_file, layer="node_mesh")
ts_df = pd.read_csv(ts_file, delim_whitespace=True, names=["seconds","seconds_cumulative"])

t0= pd.Timestamp.fromisoformat("2001-01-01T00:00:00")
waterlevel_df = gpd.GeoDataFrame(columns=["datetime", "waterlevel", "geometry"], crs=mesh_df.crs)

with FortranFile(level_file,
                 mode='r',
                 header_dtype='uint32',
                 auto_endian=True,
                 check_file=True) as src:
    for ts in range(src.nrec):
        print(f"parsing ts {ts}")
        values = src.read_record("f8")
        geoms = mesh_df["geometry"]
        df = gpd.GeoDataFrame(data={"waterlevel":values,
                                    "geometry":geoms})
        ts = t0 + pd.Timedelta(seconds=ts_df.loc[ts]["seconds_cumulative"])
        df["datetime"] = ts.isoformat()
        waterlevel_df = waterlevel_df.append(df)

#%%
schema={"properties":{"datetime":"datetime", "waterlevel":"float"},
        "geometry": "Polygon"}
waterlevel_df.to_file("result.gpkg", driver="GPKG", layer="waterlevel", schema=schema)