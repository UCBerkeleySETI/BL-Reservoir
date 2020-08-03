import zmq
import time
import os
import logger

print("Running")

context = zmq.Context()
socket = context.socket(zmq.PULL)
socket.bind("tcp://*:5555")
broadcast = context.socket(zmq.PUB)
broadcast.connect("tcp://10.0.3.141:5559")

print("Socket connected")

while True:
    #  Wait for next request from client
    message = socket.recv()
    print("Received request: %s" % str(message))

    #  Send reply back to client
    broadcast.send(message)
