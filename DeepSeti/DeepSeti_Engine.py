import wget
import pandas as pd
import requests
from DeepSeti import DeepSeti
import os 


print("Running")

context = zmq.Context()
socket = context.socket(zmq.PULL)
socket.bind("tcp://*:5555")
broadcast = context.socket(zmq.PUB)
broadcast.connect("tcp://10.0.3.141:5559")

print("Socket connected")


DeepSeti = DeepSeti()

for i in range(100,200):
  try:
    print("Downloading "+ str(i))
    file_download = wget.download(short_list[i])
    print(file_download)
    print("finished downloading")
    DeepSeti.prediction(model_location='/content/encoder_injected_model_Cudda.h5', 
                    test_location='/content/'+file_download, 
                    anchor_location='/content/GBT_58402_66967_HIP66130_mid.h5', 
                    top_hits=100, target_name=file_download,
                    output_folder='/content/drive/My Drive/Deeplearning/SETI/output_folder/')
    os.remove('/content/'+file_download)
    print("Search Execution Complete")
  except:
    try:
      os.remove('/content/'+short_list[i].replace('http://blpd7.ssl.berkeley.edu/dl2/', ''))
    except:
      print("Execution stack cleanered")
    print("Dataset "+ short_list[i].replace('http://blpd7.ssl.berkeley.edu/dl2/', '')+" doesn't exist --------- skipped!")