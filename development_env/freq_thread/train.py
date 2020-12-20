import tensorflow as tf
import keras
from keras.models import Sequential 

from keras.layers.core import Activation, Flatten
import matplotlib.pyplot as plt
from keras.optimizers import SGD,RMSprop,adam
from keras.models import load_model
from sklearn.utils import shuffle
from keras.losses import binary_crossentropy
from sklearn.model_selection import train_test_split
from keras.utils import np_utils
import os, os.path
import numpy as np
import tempfile
from keras.layers import Reshape
from keras import losses
from keras.layers.advanced_activations import LeakyReLU 
from keras.activations import sigmoid
from scipy.io import wavfile

from keras.models import Model
from keras import backend as K
from keras.layers.convolutional import Convolution1D
from keras.layers import  Conv2D, MaxPool3D, MaxPooling2D, TimeDistributed, Embedding, Convolution2D , Lambda
from keras.layers import BatchNormalization
from keras.callbacks import TensorBoard
from keras.callbacks import EarlyStopping, ModelCheckpoint
from sklearn.metrics import confusion_matrix
from blimpy import Waterfall
from keras.layers import Reshape, Conv2DTranspose, BatchNormalization, ZeroPadding2D
from astropy import units as u
from keras.layers import Softmax
from  keras.backend import expand_dims
from keras.layers import Input, Dense, Conv2D, MaxPooling2D, UpSampling2D
from random import seed
from random import random
from astropy import units as u
import matplotlib.pyplot as plt

import numpy as np
from scipy import stats, interpolate
from blimpy import Waterfall
from bisect import bisect_left
from tqdm import tqdm
from copy import deepcopy



print("""
######################################################################################

START TRAINING
MODEL: AUTOENCODER 

Author: Peter Ma

######################################################################################
""")




obs1 = Waterfall('/content/GBT_58452_70595_HIP117059_fine.h5', f_start=1100, 
                f_stop=1200, max_load=100).data
print(obs1.shape)
data_1 = np.zeros((139810,16,256))
for i in range(data_1.shape[0]):
  if i%10000==0:
    print(i)
  data_1[i,:,:]=obs1[:,0,i*256:(i+1)*256]

data_1 = data_1[..., np.newaxis]
data_1 =data_1/data_1.max()
print(data_1.shape)


##################################-----------Building Model------------------#######################
input_shape = data_1[0].shape
layer_filters = [32,64,128]
kernel_size = (3,3)
latent_dim = 64
time = int(data_1.shape[1])
filters = layer_filters[1]*2

inputs = Input(shape=input_shape, name='encoder_input')
x = inputs
for filters in layer_filters:
    x = Conv2D(filters=filters,
               kernel_size=kernel_size,
               strides=1,
               padding='same', kernel_initializer='glorot_normal')(x)
    x = MaxPooling2D(2)(x)
    x = BatchNormalization()(x)
    x = LeakyReLU(alpha=0.2)(x)
x = Conv2D(filters=128,
            kernel_size=kernel_size,
            strides=1,
            padding='same', kernel_initializer='glorot_normal')(x)
# x = MaxPooling2D(8)(x)
x = BatchNormalization()(x)
x = LeakyReLU(alpha=0.2)(x)
shape = K.int_shape(x)
encoder = Model(inputs, x, name='encoder')
encoder.summary()
print(shape)


latent_inputs = Input(shape=(shape[1],shape[2], shape[3]), name='fully_connected_inputs')
x = Flatten()(latent_inputs)
x = Dense(64)(x)
x = Softmax()(x)
fully_connected = Model(latent_inputs, x, name='fullyconnected')
fully_connected.summary()


layer_filters = [32, 64, 128]
latent_inputs = Input(shape=(latent_dim,), name='decoder_input')
x = Dense(64)(latent_inputs)
x = LeakyReLU(alpha=0.2)(x)
x = Dense(shape[1] * shape[2]*shape[3])(x)
x = LeakyReLU(alpha=0.2)(x)
x = Reshape((shape[1], shape[2],shape[3]))(x)
x = LeakyReLU(alpha=0.2)(x)
shape_1 = K.int_shape(x)
x = Reshape((shape_1[1],  shape_1[2], shape_1[3]))(x)
for filters in layer_filters[::-1]:
    x = UpSampling2D((2, 2))(x) 
    x = Conv2D(filters, (3, 3), activation='relu', padding='same')(x)   
    x = BatchNormalization()(x)
    x = LeakyReLU(alpha=0.2)(x)

x = Conv2D(1, (3, 3), activation='sigmoid', padding='same')(x) 
# Instantiate Decoder Model
decoder = Model(latent_inputs, x, name='decoder')
decoder.summary()


print(data_1.shape)



##################################-----------Training Model------------------#######################
AutoEncoder = Model(inputs, decoder(fully_connected(encoder(inputs))), name='Generator')
AutoEncoder.summary()
sgd_encoder = SGD(lr=0.01, clipnorm=1, clipvalue=0.5)
AutoEncoder.compile(optimizer=sgd_encoder, loss='binary_crossentropy',  metrics=['acc'])
mc = ModelCheckpoint('model.h5', monitor='val_loss', mode='min', save_best_only=True)

AutoEncoder.fit(data_1[0:100000,:,:,:], data_1[0:100000,:,:,:],epochs=50, batch_size=1000, shuffle=True, 
                validation_data=(data_1[100000:,:,:,:], data_1[100000:,:,:,:]), callbacks=[mc])



def freeze_layers(model):
    for i in model.layers:
        i.trainable = False
        if isinstance(i, Model):
            freeze_layers(i)
    return model

encoder_injected = Model(inputs, fully_connected(encoder(inputs)), name='Generator')
encoder_injected.summary()
from keras.models import load_model

model_freezed = freeze_layers(encoder_injected)
model_freezed.save('/content/encoder_new-injected_model.h5')
AutoEncoder.save("/content/AutoEncoder_model.h5")
# encoder_final.save("/content/encoder_final_model.h5")
new_model = load_model('/content/encoder_new-injected_model.h5')

results = new_model.predict(data_1)
print(results.shape)