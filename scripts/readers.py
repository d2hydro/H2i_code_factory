"""File readers for H2Flo gridgen dia-files."""
import pandas as pd
import geopandas as gpd
from shapely.geometry import LineString

def _ridge_to_line(ridge):
    ridge_list = ridge.split("\n")
    ridge_list = [tuple(map(float, i.split(" ")[1:])) for i in ridge_list]
    return LineString(ridge_list)


def read_ridges(file):
    ridges_txt = file.read_text()
    ridges_txt = ridges_txt.split(sep="\n", maxsplit=1)[1] # get rid of first line
    ridges_list = ridges_txt.split("\n-1")
    ridges_list = ridges_list[:-1]
    geoms = [_ridge_to_line(ridge) for ridge in ridges_list]

    return gpd.GeoDataFrame(data={"geometry":geoms})

def read_nodes(file):
    return gpd.GeoDataFrame(pd.read_csv(file,
                                        delim_whitespace=True,
                                        names=["number",
                                               "x",
                                               "y",
                                               "has_ridge",
                                               "dxy",
                                               "zmin",
                                               "zmax"],
                                        dtype={"number": int,
                                               "x": float,
                                               "y": float,
                                               "has_ridge": bool,
                                               "dxy": float,
                                               "zmin": float,
                                               "zmax": float}))


def read_links(file, version="old"):
    if version == "old":
        specs = {"number": int,
                 "node_from": int,
                 "node_to": int,
                 "x1": float,
                 "y1": float,
                 "x2": float,
                 "y2": float,
                 "zmin": float,
                 "zmax": float}
    if version == "new":
        specs = {"number": int,
                 "direction": int,
                 "node_from": int,
                 "node_to": int,
                 "x1": float,
                 "y1": float,
                 "x2": float,
                 "y2": float,
                 "zmin": float,
                 "zmax": float}

    return gpd.GeoDataFrame(pd.read_csv(file,
                                        delim_whitespace=True,
                                        names=list(specs.keys()),
                                        dtype=specs))
