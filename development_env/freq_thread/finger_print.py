import os, os.path
import numpy as np
import tempfile
from blimpy import Waterfall
from random import seed
from random import random
from sklearn.cluster import KMeans
from collections import defaultdict
from multiprocessing import Pool
from functools import partial
from reader import f, multi_read, multi_read_numpy
import multiprocessing
from astropy.time import Time
import sys 
from pandas import DataFrame
import time 
import pickle
import tqdm
from joblib import dump, load

filename = str(sys.argv[1])

def pattern_gen(obs):
  pattern = np.zeros(( obs.shape[0]*2, obs.shape[1]))
  for i in range(pattern.shape[0]):
    for j in range(pattern.shape[1]):
      if i ==j:
        pattern[i,j]=-1
      elif j==i-1:
        pattern[i,j]=1
  
      else:
        pattern[i,j]=0
  return pattern

def check(data):
  filter_data = np.zeros((data.shape[0], data.shape[1]))
  for i in range(0,data.shape[0]):
    for j in range(0,data.shape[1],2):
      if data[i,j]!=0 and data[i,j+1]!=0:
        print("("+str(i)+","+str(j+1)+")")
        filter_data[i,j+1]=1
  return filter_data

finger_print = np.load(filename)
pattern = pattern_gen(finger_print)

result = finger_print @ pattern
filter_data = check(result)
print(filter_data)
np.save("filtered_data.npy", filter_data )