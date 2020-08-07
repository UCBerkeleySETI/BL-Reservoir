import zmq
import time
import os
import wget
import time
import logging
import sys
import pickle
from .utils import get_algo_type

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

logging.info("Running")

context = zmq.Context()
request_recv_socket = context.socket(zmq.PULL)
request_recv_socket.bind("tcp://*:5555")
broadcast_socket = context.socket(zmq.PUB)
broadcast_socket.connect("tcp://10.0.3.141:5559")

# set up poller
poller = zmq.Poller()
poller.register(request_recv_socket, zmq.POLLIN)

logging.info("Socket connected")

while True:
    sockets = dict(poller.poll(2))
    if request_recv_socket in sockets and sockets[request_recv_socket] == zmq.POLLIN:
        serialized = request_recv_socket.recv()
        logging.debug(f"Received serialized request: {serialized}")
        request = pickle.loads(serialized)

        # set up response
        message = {"done": False}
        message["algo_type"] = get_algo_type(request["alg_package"])
        message["start_timestamp"] = time.time()*1000

        file_url = request["input_file_url"]
        # http://blpd13.ssl.berkeley.edu/dl/GBT_58402_67632_HIP65057_fine.h5
        temp_url = file_url
        temp_url = temp_url.replace(".","")
        temp_url = temp_url.replace(":","")
        temp_url = temp_url.replace("/","")
        temp_url = temp_url.replace("http","")
        temp_url = temp_url.replace("h5","")
        message["url"] = file_url
        message["filename"] = file_url.split("/")[-1]
        logging.info(f'Received request to process {file_url} with {request["alg_package"]}/{request["alg_name"]}')
        message["message"] = f'Received request to process {file_url} with {request["alg_package"]}/{request["alg_name"]}'
        logging.info(f"Sending message to frontend: {message}")
        broadcast_socket.send_multipart([b"MESSAGE", pickle.dumps(message)])

        start = time.time()
        filename = wget.download(file_url)
        obs_name = os.path.splitext(filename)[0]

        logging.info(f"Downloaded observation {obs_name}")
        message["message"] = f"Downloaded observation {obs_name}"
        broadcast_socket.send_multipart([b"MESSAGE", pickle.dumps(message)])

        alg_env = f'/code/bl_reservoir/{request["alg_package"]}/{request["alg_package"]}_env/bin/python3'
        fail = os.system(f'cd bl_reservoir/{request["alg_package"]} && {alg_env} {request["alg_name"]} {os.path.join(os.getcwd(), filename)} /buckets/bl-scale/{obs_name}')
        if fail:
            message["message"] = f"Algorithm Failed, removing {obs_name}"
            broadcast_socket.send_multipart([b"MESSAGE", pickle.dumps(message)])
            os.remove(filename)
            logging.info(f"Algorithm Failed, removed {obs_name} from disk")
            continue

        os.remove(filename)
        end = time.time()

        logging.info(f'{request["alg_package"]}/{request["alg_name"]} finished on {obs_name}')
        message["target"] = obs_name
        message["message"] = f'{request["alg_package"]}/{request["alg_name"]} finished in {end-start} seconds. Results uploaded to gs://bl-scale/{obs_name}'
        message["processing_time"] = end-start
        message["object_uri"] = f"gs://bl-scale/{obs_name}"
        broadcast_socket.send_multipart([b"MESSAGE", pickle.dumps(message)])
        message["done"] = True
        broadcast_socket.send_multipart([b"MESSAGE", pickle.dumps(message)])
