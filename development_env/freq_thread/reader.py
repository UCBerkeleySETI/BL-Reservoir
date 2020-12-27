from blimpy import Waterfall
import numpy
from multiprocessing import Pool
from functools import partial
import multiprocessing
import os
import tqdm
import h5py

def f(x,directory,freq):
    start = 1926
    step =2.835503418452676e-06 *256
    obs =Waterfall(directory[x], load_data=False)
    if obs.header['fch1'] < 1930:
        data = numpy.expand_dims(Waterfall(directory[x], f_start=freq-step,
                    f_stop=freq, max_load=20).data, axis=0)
        if data.shape==(1,16,1,256):
            return [obs.header['tstart'], data, directory[x]]
    return []

def multi_read(files, length=100, freq=1575):
    data = []
    pool = multiprocessing.Pool(os.cpu_count())
   
    for _ in tqdm.tqdm(pool.map(partial(f, directory=files, freq=freq), range(length)), total=100):
        data.append(_)
    pool.close()
    pool.join()
    # data = pool.map(partial(f, directory=files, freq=freq), range(length))
    return data

def single_file(start, files,width,):
    hf = h5py.File(files, "r")
    data = hf['data'][:,:,(start)*width:(start+1)*width]            
    hf.close()
    return data

def multi_read_single_file(files):
    print("Number of CPU Cores:")
    pool = multiprocessing.Pool(os.cpu_count())
    data = []
    print("Data Header Info")
    obs = Waterfall(files, load_data=False)
    obs.info()
    shape = obs.selection_shape
    freq_bins = shape[2]
    width = freq_bins//256
    length = 32
    width = freq_bins//length
    data = pool.map(partial(single_file, files=files, width=width), range(length-1))
    pool.close()
    pool.join()
    return data
    
