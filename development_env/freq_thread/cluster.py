import tensorflow as tf
import keras
from keras.models import Sequential 
from keras.layers import Dense, Dropout
from keras.layers.core import Activation, Flatten
import matplotlib.pyplot as plt
from keras.optimizers import SGD,RMSprop
from keras.models import load_model
from keras.losses import binary_crossentropy
from keras.utils import np_utils
import os, os.path
import numpy as np
import tempfile
from keras.layers import Reshape
from keras import losses
from keras.layers.advanced_activations import LeakyReLU 
from keras.activations import sigmoid
from keras.layers import Input, LSTM, MaxPooling1D, Conv1D
from keras.models import Model
from keras import backend as K
from keras.layers.convolutional import Convolution1D
from keras.layers import  Conv2D, MaxPool3D, MaxPooling2D, TimeDistributed, Embedding, Convolution2D , Lambda
from keras.layers import BatchNormalization
from keras.callbacks import TensorBoard
from keras.callbacks import EarlyStopping, ModelCheckpoint
from blimpy import Waterfall
from keras.layers import Reshape, Conv2DTranspose, BatchNormalization, ZeroPadding2D
from keras.layers import Softmax
from  keras.backend import expand_dims
from keras.layers import Input, Dense, Conv2D, MaxPooling2D, UpSampling2D
from random import seed
from random import random
from sklearn.cluster import KMeans
from collections import defaultdict
from multiprocessing import Pool
from functools import partial
from reader import f, multi_read, multi_read_numpy
import multiprocessing
from astropy.time import Time
from keras.models import load_model
import sys 
from pandas import DataFrame
import time 
import pickle
import tqdm
from joblib import dump, load
from finger_print import filter_candidates

directory = str(sys.argv[1])
files = []
start = time.time()

for filename in os.listdir(directory):
    if 'npy' in filename:
        files.append(os.path.join(directory, filename))

def checkMJD(elem):
    time = elem.split('_')
    print(time)
    string_time = time[2] 
    if string_time == 'OFF':
        string_time = time[3] 
    float_time = float(string_time)
    return float_time

files.sort(key=checkMJD)
print(len(files))

file_length = len(files)
stack_list = multi_read_numpy(file_length, files )

data = np.asarray(stack_list)
# data = np.zeros((file_length,stack_list[0].shape[0],stack_list[0].shape[1]))
# for i in range(file_length):
#     data[i,:,:] = stack_list[i]

print(data.shape)
def k_means_clustering_fit(inputdata, clusters):
    kmeans = KMeans(n_clusters=clusters, init='k-means++', max_iter=3000, n_init=100, random_state=2)
    kmeans.fit(inputdata)
    generated = np.zeros((clusters))
    prediction =  kmeans.predict(inputdata)
    for i in range(0,inputdata.shape[0]):
        for k in range(0,clusters):
            if prediction[i]==k:
                generated[k]+=1
    print(generated)
    return prediction, kmeans

def kmean_function(freq, data, model):
    print(freq)
    prediction =  model.predict(data[:,freq,:])
    return prediction

hold =[]
if 200 > len(files):
    clusters = int(len(files)//1.5)
else:
    clusters = 200

print("Predicted classes are ....")
random_index = int(random()*data.shape[1])
hold, kmeans = k_means_clustering_fit(data[:,random_index,:], clusters)

est = time.time()
pred = kmean_function(0,data,kmeans)
print(len(pred))
print(time.time()-est)



finger_print = []
length = data.shape[1]
finger_print_collapse = np.zeros((length,len(files)))
for i in range(length):
    finger_print_collapse[i,:]= kmean_function(i, data,kmeans)

times_files = []
for i in range(len(files)):
    times_files.append(checkMJD(files[i]))


df = filter_candidates(finger_print_collapse,files,times_files)



print(finger_print_collapse.shape)
np.save('fingerprint_'+str(checkMJD(files[0]))+"_"+str(checkMJD(files[len(files)-1]))+'.npy', data=finger_print_collapse)


print("END TIME")
print(time.time()-start)
