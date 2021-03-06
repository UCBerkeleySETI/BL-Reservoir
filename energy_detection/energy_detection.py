import zmq
import time
import os
import wget
import time
import pickle
import logging
import sys
from .. import upload

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

print("Running")

context = zmq.Context()
socket = context.socket(zmq.PULL)
socket.bind("tcp://*:5555")
broadcast = context.socket(zmq.PUB)
broadcast.connect("tcp://10.0.3.141:5559")

print("Socket connected")

while True:
    message_dict = {"done": False}
    message_dict["algo_type"] = "Energy-Detection"
    message_dict["start_timestamp"] = time.time()*1000

    request = socket.recv()
    logging.info(f"Serial request: {request}")
    request_dict = pickle.loads(request)
    data_url = request_dict["input_file_url"]
    # http://blpd13.ssl.berkeley.edu/dl/GBT_58402_67632_HIP65057_fine.h5
    temp_url = data_url
    temp_url = temp_url.split("/")[-1]
    temp_url = temp_url.replace(".","")
    temp_url = temp_url.replace("h5","")
    message_dict["url"] = temp_url
    logging.info(f"Received request to process {data_url}")
    message_dict["message"] = f"Received request to process {data_url}"
    broadcast.send_pyobj(message_dict)

    start = time.time()
    filename = wget.download(data_url)
    obs_name = os.path.splitext(filename)[0]

    logging.info(f"Downloaded observation {obs_name}")
    message_dict["message"] = f"Downloaded observation {obs_name}"
    broadcast.send_pyobj(message_dict)
    fail = os.system(f"cd bl_reservoir/energy_detection && python3 energy_detection_fine_dry_run.py {os.path.join(os.getcwd(), filename)} /buckets/bl-scale/{obs_name}")
    if fail:
        message_dict["message"] = f"Algorithm Failed, removing {obs_name}"
        broadcast.send_pyobj(message_dict)
        os.remove(filename)
        logging.info(f"Algorithm Failed, removed {obs_name}")
        continue

    os.remove(filename)
    end = time.time()

    logging.info("Energy Detection Finished")
    message_dict["done"] = True
    message_dict["target"] = obs_name
    message_dict["message"] = f"Energy Detection and Result Upload finished in {end-start} seconds. Results uploaded to gs://bl-scale/{obs_name}"
    message_dict["processing_time"] = end-start
    message_dict["object_uri"] = f"gs://bl-scale/{obs_name}"
    broadcast.send_pyobj(message_dict)
