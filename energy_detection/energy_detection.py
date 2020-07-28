import zmq
import time
import os
import wget
import time
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
    message_dict["algo_type"] = "Energy-Detection"
    message_dict["start_timestamp"] = time.time()*1000

    request_dict = socket.recv_pyobj()
    data_url = request_dict["input_file_url"]
    # http://blpd13.ssl.berkeley.edu/dl/GBT_58402_67632_HIP65057_fine.h5
    temp_url = data_url
    temp_url = temp_url.replace(".","")
    temp_url = temp_url.replace(":","")
    temp_url = temp_url.replace("/","")
    temp_url = temp_url.replace("http","")
    temp_url = temp_url.replace("h5","")
    message_dict["url"] = temp_url
    print(f"Received request to process {data_url}")
    message_dict["message"] = f"Received request to process {data_url}"
    broadcast.send_pyobj(message_dict)

    start = time.time()
    filename = wget.download(data_url)
    obs_name = os.path.splitext(filename)[0]

    print(f"Downloaded observation {obs_name}")
    message_dict["message"] = f"Downloaded observation {obs_name}"
    broadcast.send_pyobj(message_dict)
    fail = os.system(f"cd bl_reservoir/energy_detection && python3 energy_detection_fine_dry_run.py {os.path.join(os.getcwd(), filename)}")
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
    message_dict["target"] = obs_name
    message_dict["message"] = f"Energy Detection and Result Upload finished in {end-start} seconds. Results uploaded to gs://bl-scale/{obs_name}"
    message_dict["processing_time"] = end-start
    message_dict["object_uri"] = f"gs://bl-scale/{obs_name}"
    broadcast.send_pyobj(message_dict)
