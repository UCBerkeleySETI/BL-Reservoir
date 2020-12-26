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
import h5py
import time 

filename = str(sys.argv[1])
print("___________________________________________________________")
start= time.time()
print("Reading Data")
with h5py.File(filename, "r") as f:
    # Get the data
    data = f['data']
samples = data.shape[2]//256

print("Reshape Data and Preprocess")
data = np.reshape(data, (samples,data.shape[0],data.shape[1], 256))

obs = Waterfall(filename, load_data=False)
target_name = obs.header['rawdatafile']
target_name = target_name.replace('.raw','')

print(data.shape)
result = data [:,:,0,:]
result= np.expand_dims(result, axis=3)
print(result.shape)
min_val = result.min()
data_1 = result-min_val+1
data_1 = np.log(data_1)
max_val = data_1.max()
data_1 = data_1/max_val
result = data_1

print("Feeding Neural Network")
new_model = load_model('test_model.h5')
features = new_model.predict(result)
print(features.shape)

print("Saving Features")
np.save(str(target_name)+'_feature_'+'.npy', features)
print("DONE- time elapsed:")
print(time.time()-start)

