# -*- coding: utf-8 -*-
"""convert grid to geopackage"""

import geopandas as gpd
from pathlib import Path
from shapely.geometry import Point, Polygon, shape, LineString
from readers import read_nodes, read_links
from functions import xy_to_box, link_from_nodes, v_coord, correct_link

#%%
# path to H2Flo grid-files
grids_path = Path(r"../data/de_tol_small/case1/grids")
nodes_dia = grids_path / "node_coordinates.dia"
links_dia = grids_path / "link_coordinates.dia"
node_dem = grids_path / "node_dem.dia"
gpkg_path = grids_path / "grid.gpkg"
epsg = "28992"  # later read this from h2flo settings

# drop gpkg if exists
if gpkg_path.exists():
    gpkg_path.unlink()

# %% read h-coords and write to geopackage
print("h-coords")
nodes_df = read_nodes(nodes_dia)
nodes_df.set_index("number", inplace=True)
nodes_df["geometry"] = nodes_df[["x", "y"]].apply(tuple, axis=1).apply(Point)
nodes_df.set_crs(f"epsg:{epsg}", inplace=True)
nodes_df.to_file(gpkg_path, layer="node_coordinates", driver="GPKG")


# %% convert to h-mesh and write to geopackage
print("h-mesh")
mesh_df = nodes_df.copy()
mesh_df.loc[~nodes_df["has_ridge"], "geometry"] = mesh_df.loc[~nodes_df["has_ridge"]].apply(
    (lambda x: xy_to_box(x["x"], x["y"], x["dxy"])),
    axis=1
    )


import rasterio
from rasterio.features import shapes
import numpy as np

ridge_numbers = mesh_df[mesh_df["has_ridge"]].index.to_list()
with rasterio.Env():
    with rasterio.open(node_dem) as src:
        data = src.read(1).astype(int) # first band
        mask = np.isin(data, ridge_numbers)
        result = {
        int(v): s
        for i, (s, v) 
        in enumerate(
            shapes(data, mask=mask, transform=src.transform))}

mesh_df.loc[nodes_df["has_ridge"], "geometry"] = mesh_df.loc[nodes_df["has_ridge"]].apply(
    (lambda x: shape(result[x.name])),
    axis=1
    )
mesh_df.to_file(gpkg_path, layer="node_mesh", driver="GPKG")

# %% read v-links
print("v-links")
links_df = read_links(links_dia, version="new")
links_df["geometry"] = [
    link_from_nodes(row["node_from"], row["node_to"], nodes_df) for _, row in links_df.iterrows()
    ]
links_df.set_crs(f"epsg:{epsg}", inplace=True)
links_df.to_file(gpkg_path, layer="link_coordinates", driver="GPKG")


"""
# %% get v-coords and write to geopackage
print("v-coords")
v_df = links_df.copy()
v_df["geometry"] = [
    v_coord(row["node_from"], row["node_to"], nodes_df) for _, row in v_df.iterrows()
    ]
v_df.to_file(gpkg_path, layer="v-coords", driver="GPKG")

# %% correct v-links and write to geopackage
print("correct v-links")
links_df["geometry"] = links_df.apply((lambda x: correct_link(x, v_df)), axis=1)
links_df.to_file(gpkg_path, layer="v-links", driver="GPKG")
"""