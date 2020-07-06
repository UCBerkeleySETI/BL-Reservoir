import zmq
import time
import os

print("Running")

context = zmq.Context()
socket = context.socket(zmq.PULL)
socket.bind("tcp://*:5555")
broadcast = context.socket(zmq.PUB)
broadcast.connect("tcp://10.0.3.141:5559")

print("Socket connected")

while True:
    #  Wait for next request from client
    message = socket.recv_string()
    print("Received request: %s" % message)

    #  Do some 'work'
    time.sleep(1)

    #  Send reply back to client
    broadcast.send_string("Echo: " + message)
