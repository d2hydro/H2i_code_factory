# -*- coding: utf-8 -*-
"""
Created on Mon Dec 20 09:39:08 2021

@author: danie
"""

from fortio import FortranFile

file = r"../data/de_tol_small/case1/flows/ts/waterlevels2d.dat"

src =  FortranFile(file,
                   mode='r',
                   header_dtype='uint32',
                   auto_endian=True,
                   check_file=True)

print(src.nrec)

print(len(src.read_record("f8")))
