# H2Flo data format and strucure
Here we describe the structure of a H2Flo project and the structure of its files.

## metadata.json
A JSON file containing the metadata of a H2Flo project. The content of keys are explained below:
* **api_version**: reference to the version of the Python H2Flo API (by absence of versioning the code-date of the API)
* **topology_version**: reference to the version of grids.exe, writing the topology files (by absence of versioning the date the exe is compiled)
* **results_version**: reference to the version of flows.exe, writing the result files (by absence of versioning the date the exe is compiled)
* **name**: a user-supplied name for the model-case that can be used as a name for grouping the results in QGIS
* **crs**: EPSG-code of the coordinate reference system the model is in
* **timesteps**: object referencing to a:
    * **timesteps_file**: file with timesteps specified (see Flows/ts)
    * **start_datetime**: ISO8601 formatted datetime string: YYYY-MM-DDThh:mm:ss
* **topology**: object referencing to the files describing the model topology:
    * **2d_nodes_file**: file in the grids-folder with the node coordinates of the 2D model
    * **2d_links_file**: file in the grids-folder with the link coordinates of the 2D model
* **results**: array with model-results. Every element in that array is an object describing results:
    * **layer**: the layer-name of the output variable for reference in QGIS
    * **result_file**: file in the flows\ts folder with result-values
    * **topology_file**: reference to the topology file (2d_nodes_file or 2d_links_file) the result_file is to be referenced to
    * **timesteps_file**: reference to the file with time specifications

## Grids
The grids-folder contains the following files with a structure as explained:
**link_coordinates.dia**: A space-seperated-value ASCI file with the following columns:
 1. **id**: int, unique index for the link – ordinal (1-based)
 2. **direction**: int, direction of flow; 0 = horizontal, 1 = vertical
 3. **node_from**: int, id of the links first node
 4. **node_to**: int, id of the links last node
 5. **x_from**: x-coordinate of the links first node
 6. **y_from**: y-coordinate of the links first node
 7. **x_to**: x-coordinate of the links last node
 8. **y_to**: y-coordinate of the links last node
 9. **zmin**: float, minimum level at the velocity-face
 10. **zmax**: float, maximum level at the velocity-face

**node_coordinates.dia**: A space-seperated-value ASCI file with the following columns:
 1. **id**: int, unique index for the node – ordinal (1-based)
 2. **x**: float, x-coordinate of the node
 3. **y**: float, y-coordinate of the node
 4. **ridge**: int, indicates if it is a node adjacent to a ridge; 0 = no-ridge, 1 = ridge
 5. **dxy**: float, size in x and y direction of the node-cell (quadtree cell size in meters
 6. **zmin**: float, minimum level in the node-cell
 7. **zmax**: float, maximum level at the node-cell

**node_dem.dia** An ESRI ASCII file (https://desktop.arcgis.com/en/arcmap/10.3/manage-data/raster-and-images/esri-ascii-raster-format.htm) on the resolution of, and alligned with the DEM-raster.
Every cell contains the topology node-number the DEM-cell is mapped to.

## Flows/ts
The flows/ts-folder contains the results of a H2Flo run:
**timesteps.asc**: A space-seperated-value ASCI file with the following columns:
 1. **id**: int, identification of the timestep (ordinal, 0-based)
 2. **Cumulative-time**: float, cumulative time (seconds) since start simulation

Multiple Fortran Unformatted Binary Files that can be read by fortio https://pypi.org/project/fortio/. Every record contains all values for all nodes or links in the topology. A list of result-files:
* **discharges2d.dat**: discharge (m3/s) over links
* **velocities2d.dat**: velocities (m/s) over links
* **thinwaterdepths2d.dat** thin water depth (m) at nodes
* **volumes2d.dat** volumes (m3) at nodes
* **waterlevels2d.dat** water levels (m + datum) at nodes