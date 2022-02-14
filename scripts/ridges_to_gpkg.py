import geopandas as gpd
from pathlib import Path
from shapely.geometry import LineString, Point

crs = "epsg:28992"

def ridge_to_line(ridge):
    ridge_list = ridge.split("\n")
    ridge_list = [tuple(map(float, i.split(" ")[1:])) for i in ridge_list]
    return LineString(ridge_list)
    

ridges_file = Path(r"d:\projecten\D2102.SUBGRID_H2i\03.models\de_tol_small\ridges.  1")

ridges_txt = ridges_file.read_text()
ridges_txt = ridges_txt.split(sep="\n", maxsplit=1)[1] # get rid of first line
ridges_list = ridges_txt.split("\n-1")
ridges_list = ridges_list[:-1]
geoms = [ridge_to_line(ridge) for ridge in ridges_list]

pt_geoms = [[Point(j) for j in i.coords] for i in geoms]
pt_geoms = [item for sublist in pt_geoms for item in sublist]

ridges_gdf = gpd.GeoDataFrame(data={"geometry":geoms}, crs=crs)
ridges_vertices_gdf = gpd.GeoDataFrame(data={"geometry":pt_geoms}, crs=crs)


ridges_gdf.to_file("ridges.gpkg",
                   layer="ridges",
                   driver="GPKG")

ridges_vertices_gdf.to_file("ridges.gpkg",
                            layer="vertices",
                            driver="GPKG")
