import numpy as np
from blimpy import Waterfall

import h5py
filename = "/data/meerKAT_data.fil"
  
obs = Waterfall(filename, max_load=5)

with h5py.File(filename+".hdf5", "w") as data_file:
    data_file.create_dataset("data", data=obs.data)