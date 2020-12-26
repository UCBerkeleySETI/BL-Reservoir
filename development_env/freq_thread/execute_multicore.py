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
from reader import f
import multiprocessing
from reader import multi_read
from astropy.time import Time
from keras.models import load_model
import sys 
from pandas import DataFrame
import time 

freq = int(str(sys.argv[1]))
directory = str(sys.argv[2])

files = []
start = time.time()
# directory ="../../../../../mnt_blpd7/datax/dl/"
for filename in os.listdir(directory):
    if 'fine' in filename:
        files.append(os.path.join(directory, filename))

for filename in os.listdir(directory):
    if 'fine' in filename:
        files.append(os.path.join(directory, filename))

def checkMJD(elem):
    time = elem.split('_')
    string_time = time[2] + '.'+time[3] 
    float_time = float(string_time)
    return float_time


files.sort(key=checkMJD)

print(len(files))

if sys.argv[3] == None:
    depth = len(files)
else:
    depth = int(str(sys.argv[3]))

multicore_data = multi_read(files, length=depth, freq=freq)

stack_list =[]
time_stamps= []
file_directory = []
for i in range(len(multicore_data)):
    if multicore_data[i] != []:
        stack_list.append(multicore_data[i][1])
        time_stamps.append(multicore_data[i][0])
        file_directory.append(multicore_data[i][2])

for i in range(len(time_stamps)-1):
    if time_stamps[i] ==  time_stamps[i+1]:
        time_stamps[i+1] = time_stamps[i+1] + 0.0000000001

result = np.concatenate(stack_list)
result = result [:,:,0,:]
result= np.expand_dims(result, axis=3)

min_val = result.min()
data_1 = result-min_val+1
data_1 = np.log(data_1)
max_val = data_1.max()
data_1 = data_1/max_val

result = data_1
print(result.shape)
print(len(time_stamps))


new_model = load_model('test_model.h5')
features = new_model.predict(result)
print(features.shape)

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


hold =[]
clusters = 100
print("Predicted classes are ....")
hold, kmeans = k_means_clustering_fit(features, clusters)

def detector(hold, i):
    if hold[i-1]!=hold[i] and hold[i+1]!=hold[i] :
        return True
    return False 

candidates = []
for i in range(1, len(time_stamps)-1):
    if detector(hold, i):
        print(time_stamps[i])
        candidates.append(time_stamps[i], i, files[i],freq )
print("Candidates: ")
print(candidates)

df = DataFrame (candidates,columns=['Time [MJD]','Index','File_Directory', 'Freq'])
df.to_pickle("candidates_" + str(freq)+".pkl")


k_means_labels =  kmeans.predict(features)
k_means_cluster_members = defaultdict(list)
for i in range(k_means_labels.shape[0]):
    k_means_cluster_members[k_means_labels[i]].append(i)

negatives = []
for i in range(1,len(hold)-1):
    if hold[i-1]==hold[i] and hold[i+1]==hold[i]:
        negatives.append([i-1,i,i+1])    

print("False Signals:")
print(len(negatives))
print("END TIME")
print(time.time()-start)
print("START OF MJD")
print(time_stamps[0])
print("END OF MJD")
print(time_stamps[len(time_stamps)-1])
print("DELTA MJD")
print(time_stamps[len(time_stamps)-1]-time_stamps[0])