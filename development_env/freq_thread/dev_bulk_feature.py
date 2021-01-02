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
import pickle



directory = str(sys.argv[1])
begin = int(str(sys.argv[2]))
end = int(str(sys.argv[3]))
print("""
    ____                     _____ ________________
   / __ \___  ___  ____     / ___// ____/_  __/  _/
  / / / / _ \/ _ \/ __ \    \__ \/ __/   / /  / /  
 / /_/ /  __/  __/ /_/ /   ___/ / /___  / / _/ /   
/_____/\___/\___/ .___/   /____/_____/ /_/ /___/   
               /_/                                 
    ______           __                
   / ____/__  ____ _/ /___  ___________
  / /_  / _ \/ __ `/ __/ / / / ___/ _  |
 / __/ /  __/ /_/ / /_/ /_/ / /  /  __/
/_/    \___/\__,_/\__/\__,_/_/   \___/ 
                                       
""")
print("Peter Ma - 12/27/2020")
print("""
BULK COMPUTATION: feature extraction of multiple observations by feeding radio spectrograms into a Neural Network to compute the feautures for classification further down the pipeline. 
""")
print("___________________________________________________________________________________")

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

start = 1926
step =2.835503418452676e-06 *256

time_stamps = []
count=0
file_directory=[]
for directory in files:
    obs =Waterfall(directory, load_data=False)
    if obs.header['fch1'] < 1930:
        flag= True
        obs = Waterfall(directory, f_start=1575-step, 
                    f_stop=1575, max_load=20, load_data=False)
        if obs.selection_shape==(16,1,256):
            print('check')
            print(count)
            time_stamps.append(obs.header['tstart'])
            file_directory.append(directory)

count =0
new_model = load_model('test_model.h5')
for i in range(end-begin):
    filename = str(file_directory[i+begin])
    print("___________________________________________________________________________________")
    print("""
        ____                 _____ ________________
    / __ \___  ___  ____ / ___// ____/_  __/  _/
    / / / / _ \/ _ \/ __ \\__ \/ __/   / /  / /  
    / /_/ /  __/  __/ /_/ /__/ / /___  / / _/ /   
    /_____/\___/\___/ .___/____/_____/ /_/ /___/   
                /_/                             
    """)
    print("----- Single Core IO Version -----")
    print("Peter Ma - 12/27/2020")
    print("""
    Feeding Radio spectrograms into Neural Network to compute the feautures for classification further down the pipeline.  
    """)
    print("___________________________________________________________________________________")
    start= time.time()
    print("Reading Data")
    obs = Waterfall(filename, load_data=False)
    target_name = obs.header['source_name']
    print("Target Name: "+str(target_name))

    data = Waterfall(filename, max_load = 20).data
    samples = data.shape[2]//256

    print("Reshape Data and Preprocess")
    data = np.reshape(data, (samples,data.shape[0],data.shape[1], 256))

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
    
    features = new_model.predict(result)
    print(features.shape)

    print("Saving Features")
    np.save(str(target_name)+ "_"+str(obs.header['tstart'])+'_feature_'+'.npy', features)
    print("DONE- time elapsed [sec]:")
    print(time.time()-start)




    




