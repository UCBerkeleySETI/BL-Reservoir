import zmq
import time

print("Running")

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5555")

print("Socket connected")

while True:
    #  Wait for next request from client
    message = socket.recv_string()
    print("Received request: %s" % message)

    #  Do some 'work'
    time.sleep(1)

    #  Send reply back to client
    socket.send_string("Echo: " + message)
