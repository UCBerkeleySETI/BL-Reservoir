import zmq
import time
import os
import wget
from .. import upload

print("Running")

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5555")

print("Socket connected")

while True:
    data_url = socket.recv_string()
    print(f"Received request to process {data_url}")
    start = time.time()
    filename = wget.download(data_url)
    obs_name = os.path.splitext(filename)[0]
    os.system(f"python3 /code/alien-hunting-algs/energy_detection/preprocess_fine.py {os.path.join(os.getcwd(), filename)}")
    upload.upload_dir("bl-scale", os.path.join(obs_name))
    os.remove(filename)
    os.system(f"rm -rf {obs_name}")
    end = time.time()
    socket.send_string(
    f"Energy Detection and Result Upload finished in {end-start} seconds. Results uploaded to bl-scale/{obs_name}")
