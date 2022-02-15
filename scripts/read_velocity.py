# -*- coding: utf-8 -*-
"""
Created on Mon Dec 20 09:39:08 2021

@author: danie
"""

from fortio import FortranFile
import geopandas as gpd
import pandas as pd

level_file = r"../data/de_tol_small/case1/flows/ts/velocityupwind2d.dat"


with FortranFile(level_file,
                 mode='r',
                 header_dtype='uint32',
                 auto_endian=True,
                 check_file=True) as src:
    print(src.nrec)
    src.read_record()
    src.read_record()
    first_row = src.read_record("f8")
    second_row = src.read_record("f8")