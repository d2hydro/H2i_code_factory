# H2Flo data format and strucure
Here we describe the structure of a H2Flo project and the structure of its files.

## metadata.json
A JSON file containing the metadata of a H2Flo project. The content of keys are explained below:
* **api_version**: reference to the version of the Python H2Flo API (by absence of versioning the code-date of the API)
* **topology_version**: reference to the version of grids.exe, writing the topology files (by absence of versioning the date the exe is compiled)
* **results_version**: reference to the version of flows.exe, writing the result files (by absence of versioning the date the exe is compiled)
* **name**: a user-supplied name for the model-case that can be used as a name for grouping the results in QGIS
* **crs**: EPSG-code of the coordinate reference system the model is in
* **topology**: object referencing to the files describing the model topology:
    * **2d_nodes_file**: file in the grids-folder with the node coordinates of the 2D model
    * **2d_links_file**: file in the grids-folder with the link coordinates of the 2D model
* **results**: array with model-results. Every element in that array is an object describing results:
    * **layer**: the layer-name of the output variable for reference in QGIS
    * **result_file**: file in the flows\ts folder with result-values
    * **topology_file**: reference to the topology file (2d_nodes_file or 2d_links_file) the result_file is to be referenced to
    * **time_specs_file**: reference to the file with time specifications

## Grids
The grids-folder contains the following files:
* link_coordinates.dia: A space-seperated-value ASCI file with the following columns:
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
