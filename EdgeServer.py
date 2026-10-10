import numpy as np
import socket
import pickle
import cv2
import timeit

def sendData(request_type, msg):
    data = []
    data.append(request_type)
    data.append(msg)
    data = pickle.dumps(data)
    start = timeit.default_timer()
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('localhost', 2222))
    s.sendall(data)
    data = s.recv(100)
    data = data.decode()
    end = timeit.default_timer()
    total_delay = end - start
    print(total_delay)
    return data

img = cv2.imread("1.jpg")
img = cv2.resize(img, (400, 400))
data = sendData("cloud", img)
print(data)

data = sendData("edge", "welcome to java world")
print(data)

