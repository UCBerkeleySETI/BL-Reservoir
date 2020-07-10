import zmq
import time
import os
import wget
from .. import upload

print("Running")

context = zmq.Context()
socket = context.socket(zmq.PULL)
socket.bind("tcp://*:5555")
broadcast = context.socket(zmq.PUB)
broadcast.connect("tcp://10.0.3.141:5559")

print("Socket connected")

while True:
    message_dict = {"done": False}
    request_dict = socket.recv_pyobj()
    data_url = request_dict["message"]
    print(f"Received request to process {data_url}")
    message_dict["message"] = f"Received request to process {data_url}"
    broadcast.send_pyobj(message_dict)

    start = time.time()
    filename = wget.download(data_url)
    obs_name = os.path.splitext(filename)[0]
    print(f"Downloaded observation {obs_name}")
    message_dict["message"] = f"Downloaded observation {obs_name}"
    broadcast.send_pyobj(message_dict)
    fail = os.system(f"cd alien_hunting_algs/energy_detection && python3 preprocess_fine.py {os.path.join(os.getcwd(), filename)}")
    if fail:
        message_dict["message"] = f"Algorithm Failed, removing {obs_name}"
        broadcast.send_pyobj(message_dict)
        os.remove(filename)
        os.system(f"rm -rf {obs_name}")
        print(f"Algorithm Failed, removed {obs_name}")
        continue

    upload.upload_dir("bl-scale", os.path.join(os.getcwd(), obs_name))
    os.remove(filename)
    os.system(f"rm -rf {obs_name}")
    end = time.time()

    message_dict["done"] = True
    message_dict["algo_type"] = 'Energy-Detection'
    message_dict["target"] = obs_name
    message_dict["message"] = f"Energy Detection and Result Upload finished in {end-start} seconds. Results uploaded to gs://bl-scale/{obs_name}"
    message_dict["processing_time"] = end-start
    message_dict["object_uri"] = f"gs://bl-scale/{obs_name}"
    broadcast.send_pyobj(message_dict)
