import socket 
from threading import Thread 
from socketserver import ThreadingMixIn
import socket
import pickle
import cv2
import datetime

running = True

def saveImage(img):
    ct = datetime.datetime.now()
    ct = str(ct)
    ct = ct.replace(" ","_")
    ct = ct.replace(".","_")
    ct = ct.replace(":","_")
    name = ct+".jpg"
    print(name)
    cv2.imwrite("TrafficImages/"+name, img)
    

def startCloudServer():
    class Cloud(Thread): 
 
        def __init__(self,ip,port): 
            Thread.__init__(self) 
            self.ip = ip 
            self.port = port
            print('Request received from Client IP : '+ip+' with port no : '+str(port)+"\n")        
         
        def run(self):
            global encrypted_data
            data = conn.recv(1000000)
            data = pickle.loads(data)
            request_type = data[0]
            if request_type == "cloud":#cloud receive request as traffic image
                img = data[1]
                saveImage(img)
                conn.send("Cloud Image Received".encode())
                print("Cloud Traffic Image Received")
            elif request_type == "edge": #cloud received request of edge data
                msg = data[1]
                print(msg)
                conn.send("Edge Traffic Data Received".encode())#sending results back to edge server                   
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
    server.bind(('localhost', 2222))
    print("Cloud Server Started\n\n")
    while running:
        server.listen(4)
        (conn, (ip,port)) = server.accept()
        newthread = Cloud(ip,port) 
        newthread.start() 
    
def startServer():
    Thread(target=startCloudServer).start()

startServer()

