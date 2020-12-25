from blimpy import Waterfall
import numpy
from multiprocessing import Pool
from functools import partial
import multiprocessing
import os

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
    pool = multiprocessing.Pool(os.cpu_count())
    data = pool.map(partial(f, directory=files, freq=freq), range(length))
    return data