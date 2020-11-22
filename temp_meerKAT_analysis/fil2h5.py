import numpy as np
from blimpy import Waterfall
import h5py
import sys 
filename = str(sys.argv[1])
obs = Waterfall(filename, max_load=25)
with h5py.File(filename+".h5", "w") as data_file:
    data_file.create_dataset("data", data=obs.data[:,:,:])
