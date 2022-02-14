"""Functions for (Geo)Pandas apply-method"""
from shapely.geometry import LineString, box


def link_direction(node_from, node_to, nodes_df):
    """Get the v-direction from node_to and node_from."""
    point_from = nodes_df.loc[node_from]["geometry"]
    point_to = nodes_df.loc[node_to]["geometry"]
    dif_x = abs(point_from.x - point_to.x)
    dif_y = abs(point_from.y - point_to.y)
    if dif_x < dif_y:
        direction = 1
    else:
        direction = 0
    return direction


def link_from_nodes(node_from, node_to, nodes_df):
    """Get the link from node_to and node_from.""" 
    return LineString([nodes_df.loc[node_from]["geometry"],
                       nodes_df.loc[node_to]["geometry"]])

def xy_to_box(x, y, size):
    """Function to draw polygons around nodes."""
    return box(minx=x-size*0.5,
               miny=y-size*0.5,
               maxx=x+size*0.5,
               maxy=y+size*0.5)


def v_coord(node_from, node_to, nodes_df):
    node_start = nodes_df.loc[node_from]
    node_end = nodes_df.loc[node_to]
    if node_start["dxy"] > node_end["dxy"]:
        node = node_end
    else:
        node = node_start
    link = link_from_nodes(node_from, node_to, nodes_df)
    box =  xy_to_box(node["x"], node["y"], node["dxy"])
    faces = [LineString([box.coords[i], box.coords[i+1]]) for i in range(len(box.coords) - 1)]
    face = next(face for face in faces if face.intersects(link))
    return face.centroid


def correct_link(row, v_df):
    """Get the link from node_to and node_from.""" 
    geom = v_df.loc[row.name]["geometry"]
    bounds = row["geometry"].boundary
    return LineString([bounds[0], geom, bounds[-1]])