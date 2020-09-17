import tensorflow as tf
import numpy as np
import time
from collections import defaultdict
from tensorflow.keras import datasets, layers, models
import matplotlib.pyplot as plt
from keras.preprocessing import image
from keras.applications import resnet50
from keras.applications.resnet50 import ResNet50
from tensorflow.keras.applications.resnet50 import preprocess_input, decode_predictions
import skimage
from skimage import transform
from PIL import Image
from matplotlib import cm
import cv2
from sklearn.utils import shuffle
from sklearn.model_selection import train_test_split
import pandas as pd
from matplotlib import pyplot as plt
from sklearn.datasets.samples_generator import make_blobs
from sklearn.cluster import KMeans
from sklearn.cluster import DBSCAN
from matplotlib import pyplot as plt
import random
from tqdm import tqdm
import time 



start = time.time()
print("Loading Windows Samples")
np_images = np.load('filter/filtered.npy')
np_images = np.take(np_images,np.random.permutation(np_images.shape[0]),axis=0,out=np_images)
print(np_images.shape)
temp_stop = time.time()-start
print("Downloading Resnet 50 model")
conv_only_model = ResNet50(include_top=False,
                 weights='imagenet',
                 input_shape=(32, 256, 3),
                 pooling="max")
# conv_only_model.summary()
start = time.time()
def resize_and_rgb(img, shape=(224, 224)):
  np_images_resized = skimage.transform.resize(image=img, output_shape = shape)
  np_images_resized -= np.min(np_images_resized)
  np_images_resized = np_images_resized / np.max(np_images_resized)
  im = cv2.cvtColor(np.float32(np_images_resized),cv2.COLOR_GRAY2RGB)
  return im
print("Resize and preprocess data.")
converted_img = np.zeros((5000, 32, 256, 3))
for k in tqdm(range(converted_img.shape[0])):
  converted_img[k,:,:,:] = resize_and_rgb(np_images[k,:,:], (32, 256))
# # Scale the input image to the range used in the trained network
x = resnet50.preprocess_input(converted_img)
# # Run the image through the deep neural network to make a prediction
print("Pushing Data through the network")
predictions = conv_only_model.predict(x)
def DBSCAN_clustering_fit(inputdata):
  dbscan = DBSCAN(eps=0.5, min_samples=3, metric='euclidean', metric_params=None, algorithm='auto', leaf_size=30, p=None, n_jobs=-1)
  prediction = dbscan.fit_predict(inputdata)
  print(np.max(prediction))
  clusters = np.max(prediction)
  print(prediction)
  generated = np.zeros((clusters))
  for i in range(0,inputdata.shape[0]):
    for k in range(0,clusters):
      if prediction[i]==k:
        generated[k]+=1
  print(generated)
  names = np.zeros((clusters))
  for t in range(0,clusters):
    names[t]=t
  plt.bar(names, generated)
  plt.savefig('density_cluster.png')
  return prediction, dbscan
print("Density clustering...")
