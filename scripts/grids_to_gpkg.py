# -*- coding: utf-8 -*-
"""convert grid to geopackage"""

import geopandas as gpd
from pathlib import Path
from shapely.geometry import Point, shape, LineString, Polygon
from shapely.ops import split
from readers import read_nodes, read_links, read_ridges
from functions import xy_to_box, link_from_nodes
import time
import rasterio
from rasterio.features import shapes
import numpy as np
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning) 

#%%
# path to H2Flo grid-files
grids_path = Path(r"../data/de_tol_small/case1/grids")
nodes_dia = grids_path / "node_coordinates.dia"
links_dia = grids_path / "link_coordinates.dia"
node_dem = grids_path / "node_dem.dia"
ridges_file = grids_path.parent / "ridges.  1"
gpkg_path = grids_path / "grid.gpkg"
epsg = "28992"  # later read this from h2flo settings

# drop gpkg if exists
if gpkg_path.exists():
    try:
        gpkg_path.unlink()
    except PermissionError:
        print(f"cannot delete {gpkg_path}")

tic = time.perf_counter()
# %% read h-coords and write to geopackage
print("node_coordinates")
nodes_df = read_nodes(nodes_dia)
nodes_df.set_index("number", inplace=True)
nodes_df["geometry"] = nodes_df[["x", "y"]].apply(tuple, axis=1).apply(Point)
nodes_df.set_crs(f"epsg:{epsg}", inplace=True)
nodes_df.to_file(gpkg_path, layer="node_coordinates", driver="GPKG")

# %% convert to node-mesh and write to geopackage
print("node_mask")

#non-ridge can be drawn from the node_coordinates.dia directly
mask_df = nodes_df.copy()
mask_df.loc[~nodes_df["has_ridge"], "geometry"] = mask_df.loc[~nodes_df["has_ridge"]].apply(
    (lambda x: xy_to_box(x["x"], x["y"], x["dxy"])),
    axis=1
    )

#ridges are to be rasterized from the node_dem

ridge_numbers = mask_df[mask_df["has_ridge"]].index.to_list()
with rasterio.Env():
    with rasterio.open(node_dem) as src:
        data = src.read(1).astype(int) # first band
        mask = np.isin(data, ridge_numbers)
        result = {
        int(v): s
        for i, (s, v) 
        in enumerate(
            shapes(data, mask=mask, transform=src.transform))}

mask_df.loc[nodes_df["has_ridge"], "geometry"] = mask_df.loc[nodes_df["has_ridge"]].apply(
    (lambda x: shape(result[x.name])),
    axis=1
    )

mask_df.to_file(gpkg_path, layer="node_mask", driver="GPKG")

# %% read link_coordinates
print("link_coordinates")
links_df = read_links(links_dia, version="new")
links_df["geometry"] = [
    link_from_nodes(row["node_from"], row["node_to"], nodes_df) for _, row in links_df.iterrows()
    ]
links_df.set_crs(f"epsg:{epsg}", inplace=True)
links_df.to_file(gpkg_path, layer="link_coordinates", driver="GPKG")
links_df.set_index("number", inplace=True)


# %% create link_edges
print("link_edges")
ridges_df = read_ridges(ridges_file)
columns = links_df.columns.to_list() + ["number"]
links_edges = {}
node_mesh = {}
mask_df["area"] = mask_df["geometry"].area

for _,row in mask_df.sort_values("area", ascending=False).iterrows():
    node_mesh[row.name] = row.to_dict()
    links = links_df[(links_df["node_from"] == row.name) | (links_df["node_to"] == row.name)].index.to_list()
    links = [i for i in links if not i in links_edges.keys()]
    if row["has_ridge"]:
        dxy = row["dxy"]
        quad_x = (int((row["x"] - src.bounds.left) / dxy) + 0.5) *  dxy + src.bounds.left
        quad_y = (int((row["y"] - src.bounds.bottom) / dxy) + 0.5) *  dxy + src.bounds.bottom
        quad_mesh = xy_to_box(quad_x, quad_y, dxy)
        ridge = ridges_df[ridges_df.intersects(quad_mesh)].iloc[0]["geometry"]
        ridge = ridge.intersection(quad_mesh)
        ridge = LineString(ridge.boundary)
        geoms = split(quad_mesh, ridge).geoms
        node_dist = [Point(row["x"], row["y"]).distance(i.centroid) for i in geoms]
        min_dist = min(node_dist)
        mesh = geoms[node_dist.index(min_dist)]
        #mesh = next(i for i in split(quad_mesh, ridge).geoms if Point(row["x"], row["y"]).within(i))
    else:
        dxy, quad_x, quad_y = row["dxy"], row["x"], row["y"]
        mesh = xy_to_box(quad_x, quad_y, row["dxy"])
    node_mesh[row.name]["geometry"] = mesh
    # if links:
    #     mesh_coords = [i for i in mesh.boundary.coords]
    #     edges = [LineString((i, mesh_coords[idx+1])) for idx, i in enumerate(mesh_coords[:-1])]
    #     for link in links:
    #         row_out = links_df.loc[link].to_dict()
    #         geometry = [
    #             i for i in edges if i.intersects(row_out["geometry"])
    #             ]
    #         if len(geometry) == 1:
    #             row_out["geometry"] = geometry[0]
    #         elif len(geometry) == 0:
    #             dist = [i.distance(row_out["geometry"]) for i in edges]
    #             min_dist = min(dist)
    #             row_out["geometry"] = edges[dist.index(min_dist)]
    #         else:
    #             dist = [i.distance(row_out["geometry"].centroid) for i in edges]
    #             min_dist = min(dist)
    #             row_out["geometry"] = edges[dist.index(min_dist)]
            
    #         links_edges[link] = row_out
        
# links_edges_df = gpd.GeoDataFrame.from_dict(links_edges, orient="index")
# links_edges_df.set_crs(f"epsg:{epsg}", inplace=True)
# links_edges_df.index.name="number"
# links_edges_df.to_file(gpkg_path, layer="link_edges", driver="GPKG")


#%%
print("node_mesh")

node_mesh_df = gpd.GeoDataFrame.from_dict(node_mesh, orient="index")
node_mesh_df.set_crs(f"epsg:{epsg}", inplace=True)
node_mesh_df.index.name="number"


vertices_series = node_mesh_df["geometry"].apply(lambda x: [list(i)[:2] for i in x.exterior.coords]).explode().reset_index(drop=True)
vertices_df = gpd.GeoDataFrame(columns=["x", "y", "geometry"])
vertices_df.set_crs(f"epsg:{epsg}", inplace=True)
vertices_df["x"] = vertices_series.apply(lambda x:x[0])
vertices_df["y"] = vertices_series.apply(lambda x:x[1])
vertices_df = vertices_df.drop_duplicates()
vertices_df["geometry"] = vertices_df.apply((lambda x:Point(x["x"], x["y"])), axis=1)

def update_mesh_geom(x):
    coords = vertices_df[vertices_df.intersects(x)]["geometry"].values
    dist = [x.exterior.project(i) for i in coords]
    return Polygon(LineString([i for _, i in sorted(zip(dist,coords))]))

node_mesh_df.loc[:,"geometry"] = node_mesh_df["geometry"].apply(update_mesh_geom)
node_mesh_df.to_file(gpkg_path, layer="node_mesh", driver="GPKG")
toc = time.perf_counter()

print(f"grid post-processed in {toc - tic:0.4f} seconds")