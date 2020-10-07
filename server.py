import zmq
import time
import os
import wget
import logging
import sys
import pickle
import subprocess
from .utils import get_algo_type, alg_working_directories, get_algo_command_template

# set up logging
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logging.info("Running")

# grab pod metadata
pod_id = os.environ("POD_ID")
pod_ip = os.environ("POD_IP")
scheduler_ip = os.environ("SCHEDULER_IP", "")

# set up networking, request_recv_socket pulls in requests,
# and broadcast_socket sends out status updates via a ZMQ proxy
context = zmq.Context()
request_recv_socket = context.socket(zmq.PULL)
request_recv_socket.bind("tcp://*:5555")
broadcast_socket = context.socket(zmq.PUB)
broadcast_socket.connect("tcp://10.0.3.141:5559")

if scheduler_ip:
    update_send_socket = context.socket(zmq.PUSH)
    update_send_socket.bind(f"tcp://{scheduler_ip}:5510")

# set up poller, for polling messages from request_recv_socket
poller = zmq.Poller()
poller.register(request_recv_socket, zmq.POLLIN)

logging.info("Socket connected")

logging.info(f"{pod_id} running at {pod_ip}:5555")
connect_request = dict()
connect_request["pod_id"] = pod_id
connect_request["pod_ip"] = pod_ip

if scheduler_ip:
    connect_request["message"] = f"{pod_id} running at {pod_ip}:5555"
    update_send_socket.send_pyobj(connect_request)

# prepare default message
message = dict()
message["pod_id"] = pod_id
message["pod_ip"] = pod_ip

while True:
    # poller polls for 2 miliseconds and processes the request if one is received
    sockets = dict(poller.poll(2))
    if request_recv_socket in sockets and sockets[request_recv_socket] == zmq.POLLIN:
        # request is received as a pickled dictionary object;
        # however, we may get malicious traffic sending us random data,
        # so we catch UnpicklingError's and print the received message for debugging
        serialized = request_recv_socket.recv()
        try:
            request = pickle.loads(serialized)
            logging.info(f"Received request: {request}")
        except pickle.UnpicklingError:
            logging.info(f"Malformed serialized request: {serialized}")
            continue

        # set up response
        message["done"] = False
        message["algo_type"] = get_algo_type(request["alg_package"])
        message["start_timestamp"] = time.time()*1000

        # string manipulation to make things easier on the front end
        file_url = request["input_file_url"]
        # http://blpd13.ssl.berkeley.edu/dl/GBT_58402_67632_HIP65057_fine.h5
        temp_url = file_url
        temp_url = temp_url.replace(".", "")
        temp_url = temp_url.replace(":", "")
        temp_url = temp_url.replace("/", "")
        temp_url = temp_url.replace("http", "")
        temp_url = temp_url.replace("h5", "")
        message["url"] = temp_url
        message["filename"] = file_url.split("/")[-1]
        logging.info(f'Received request to process {file_url} with {request["alg_package"]}/{request["alg_name"]}')
        message["message"] = f'Received request to process {file_url} with {request["alg_package"]}/{request["alg_name"]}'

        # we send the message as a pickled dictionary object using send_multipart
        # to attache the "MESSAGE" topic to the message, this lets the SUB sockets connected to the proxy
        # to choose the types of messages they want to receive
        logging.info(f"Sending message to frontend: {message}")
        broadcast_socket.send_multipart([b"MESSAGE", pickle.dumps(message)])

        # download the file and record the start time
        start = time.time()
        filename = wget.download(file_url)
        obs_name = os.path.splitext(filename)[0]

        logging.info(f"Downloaded file {filename}")
        message["message"] = f"Downloaded file {filename}"
        broadcast_socket.send_multipart([b"MESSAGE", pickle.dumps(message)])

        #
        alg_workdir = alg_working_directories.get(request["alg_package"], None)
        if "command" not in request:
            # we use subprocess.call to call the requested algorithm, the cwd keyword argument lets us select the working directory
            # we want to run the algorithm in, this makes things easier for algorithms like turboSETI, which have to be called in
            # its own project directory
            logging.debug('Calling: ')
            logging.debug(get_algo_command_template(request["alg_package"], request["alg_name"])
                          (f'/code/{filename}', '/results_buffer').split())
            fail = subprocess.call(
                get_algo_command_template(request["alg_package"], request["alg_name"])
                                         (f'/code/{filename}', '/results_buffer').split(), cwd=alg_workdir)

            # string manipulation to make the output directory look better
            # outputs will be moved to bl-scale/<obs_name>/energy_detection/energy_detection_fine for fine-res energy detection
            if request["alg_name"].endswith(".py"):
                alg_name = request["alg_name"].split(".")[0]
            else:
                alg_name = request["alg_name"]
            dirs = (f'/buckets/bl-scale/{obs_name}',
                    f'/buckets/bl-scale/{obs_name}/{request["alg_package"]}',
                    f'/buckets/bl-scale/{obs_name}/{request["alg_package"]}/{alg_name}')
            for dir in dirs:
                try:
                    os.mkdir(dir)
                except FileExistsError:
                    continue

            # move outputs from results buffer to the storage buckets
            # the files have to be output to a local directory first to bypass issues with FUSE
            # which errors when we try to write to a file multiple times in a short time
            # using a local directory as a buffer lets us write via FUSE once per file
            subprocess.call(f'mv /results_buffer/* /buckets/bl-scale/{obs_name}/{request["alg_package"]}/{alg_name}', shell=True)
        else:
            fail = subprocess.call(f'{request["command"]}')

        # if run fails, detete downloaded data and wait for next request
        if fail:
            message["message"] = f"Algorithm Failed, removing {obs_name}"
            broadcast_socket.send_multipart([b"MESSAGE", pickle.dumps(message)])
            os.remove(filename)
            logging.info(f"Algorithm Failed, removed {obs_name} from disk")
            continue

        # delete input file and record finish time
        os.remove(filename)
        end = time.time()

        # send finished message
        logging.info(f'{request["alg_package"]}/{request["alg_name"]} finished on {obs_name}')
        message["target"] = obs_name
        message["message"] = (f'{request["alg_package"]}/{request["alg_name"]} finished in {end-start} seconds.'
                              f'Results uploaded to gs://bl-scale/{obs_name}/{request["alg_package"]}/{request["alg_name"]}')
        message["processing_time"] = end-start
        message["object_uri"] = f'gs://bl-scale/{obs_name}/{request["alg_package"]}/{alg_name}'
        broadcast_socket.send_multipart([b"MESSAGE", pickle.dumps(message)])
        message["done"] = True
        broadcast_socket.send_multipart([b"MESSAGE", pickle.dumps(message)])
