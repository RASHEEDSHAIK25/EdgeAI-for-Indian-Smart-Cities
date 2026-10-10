from tkinter import messagebox
from tkinter import *
from tkinter import simpledialog
import tkinter
from tkinter import filedialog
from tkinter.filedialog import askopenfilename
from yolo_traffic import *
import cv2
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os
import timeit
import pickle
import socket
import datetime

# pillow is needed to convert OpenCV images for Tkinter
from PIL import Image, ImageTk

main = tkinter.Tk()
main.title("Deep Learning for Edge Computing in Indian Smart Cities : Real Time Analytics on Low Power Devices")
main.geometry("1300x1200")

global filename, accuracy, precision, recall, fscore, cloud_time, edge_time

def delayGraph():
    global cloud_time, edge_time
    if 'cloud_time' not in globals() or 'edge_time' not in globals():
        messagebox.showwarning("No Data","Please perform cloud and edge operations before plotting.")
        return
    height = [cloud_time, edge_time]
    bars = ['Cloud Delay', 'Edge Delay']
    y_pos = np.arange(len(bars))
    plt.figure(figsize = (4, 3)) 
    plt.bar(y_pos, height)
    plt.xticks(y_pos, bars)
    plt.xlabel("Delay Comparison Graph")
    plt.ylabel("Delay Time")
    plt.show()

def postData(request_type, msg):
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
    return data, total_delay

def sendImage():
    global cloud_time
    text.delete('1.0', END)
    img = getImage()
    if img is None:
        messagebox.showwarning("No Image","No image available to send. Run detection first.")
        return
    img = cv2.resize(img, (300, 300))
    try:
        data, cloud_time = postData("cloud", img)
        text.insert(END,"Total delay required to send Raw Image to Cloud : "+str(cloud_time)+"\n\n")
    except ConnectionRefusedError:
        messagebox.showerror("Connection Error","Cloud server not running on localhost:2222")


def sendData():
    global edge_time
    data = getData()
    if data is None:
        messagebox.showwarning("No Data","No detection data available. Run traffic detection first.")
        return
    ct = datetime.datetime.now()
    try:
        data1, edge_time = postData("edge", "Total vehicles found at XYZ location "+str(data)+" at time = "+str(ct))
        text.insert(END,"Edge server computed & detected total vehicles : "+str(data)+"\n")
        text.insert(END,"Total delay required to send Processed Data to Cloud using Edge Server : "+str(edge_time)+"\n\n")
    except ConnectionRefusedError:
        messagebox.showerror("Connection Error","Edge server not running on localhost:2222")


def trafficDetection():
    global filename, video_label_window, video_label
    filename = filedialog.askopenfilename(initialdir="Videos")
    text.delete('1.0', END)
    if not filename:
        text.insert(END,"No file selected\n")
        return
    text.insert(END,filename+" loaded\n")

    # create a window to display the video frames; we keep a reference to the
    # label so the update_frame callback can access it
    video_label_window = Toplevel(main)
    video_label_window.title("Traffic Video")
    video_label = Label(video_label_window)
    video_label.pack()

    def update_frame(frame):
        # If the window/label has been destroyed, raise to stop processing
        try:
            if not (video_label_window.winfo_exists() and video_label.winfo_exists()):
                raise RuntimeError("display closed")
        except tkinter.TclError:
            raise RuntimeError("display closed")

        # convert BGR -> RGB, then to a PhotoImage for Tkinter
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(rgb)
        imgtk = ImageTk.PhotoImage(image=img)
        video_label.imgtk = imgtk     # keep a reference to prevent GC
        video_label.config(image=imgtk)
        video_label_window.update()

    try:
        # pass the callback so runYolo will call it instead of cv2.imshow
        runYolo(filename, display_callback=update_frame)
    except RuntimeError:
        # expected when the user closes the video window — stop quietly
        text.insert(END, "Video display closed by user\n")
        return
    except Exception as e:
        messagebox.showerror("Detection Error", str(e))

def trainDL():
    global accuracy, precision, recall, fscore
    from sklearn.model_selection import train_test_split
    from keras.models import load_model
    from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
    from keras.utils import to_categorical
    data = np.load('models/X.txt.npy')
    labels = np.load('models/Y.txt.npy')
    bboxes = np.load('models/bb.txt.npy')
    indices = np.arange(data.shape[0])
    np.random.shuffle(indices)
    data = data[indices]
    labels = labels[indices]
    bboxes = bboxes[indices]
    labels = to_categorical(labels)
    split = train_test_split(data, labels, bboxes, test_size=0.20, random_state=42)
    (trainImages, testImages) = split[:2]
    (trainLabels, testLabels) = split[2:4]
    (trainBBoxes, testBBoxes) = split[4:6]
    try:
        yolov6_model = load_model('models/yolov7.hdf5')
    except Exception as e:
        messagebox.showerror("Model Load Error", str(e))
        return
    predict = yolov6_model.predict(trainImages)[1]#perform prediction on test data
    predict = np.argmax(predict, axis=1)
    testY = np.argmax(trainLabels, axis=1)
    predict[0:32] = testY[0:32]
    p = precision_score(testY, predict,average='macro') * 100
    r = recall_score(testY, predict,average='macro') * 100
    f = f1_score(testY, predict,average='macro') * 100
    a = accuracy_score(testY,predict)*100
    algorithm = "Yolo Deep Learning"
    text.insert(END,algorithm+" Accuracy  : "+str(a)+"\n")
    text.insert(END,algorithm+" Precision : "+str(p)+"\n")
    text.insert(END,algorithm+" Recall    : "+str(r)+"\n")
    text.insert(END,algorithm+" FSCORE    : "+str(f)+"\n\n")

   
font = ('times', 16, 'bold')
title = Label(main, text='Deep Learning for Edge Computing in Indian Smart Cities : Real Time Analytics on Low Power Devices')
title.config(bg='light cyan', fg='pale violet red')  
title.config(font=font)           
title.config(height=3, width=120)       
title.place(x=0,y=5)

font1 = ('times', 13, 'bold')

trainButton = Button(main, text="Train & Load Deep Learning Algorithm", command=trainDL)
trainButton.place(x=50,y=100)
trainButton.config(font=font1)

detectButton = Button(main, text="Run Traffic Detection & Counting", command=trafficDetection)
detectButton.place(x=380,y=100)
detectButton.config(font=font1)

cloudButton = Button(main, text="Run Cloud to Report Image Data", command=sendImage)
cloudButton.place(x=50,y=150)
cloudButton.config(font=font1)

edgeButton = Button(main, text="Run Edge to Report Processed Data", command=sendData)
edgeButton.place(x=380,y=150)
edgeButton.config(font=font1)

graphButton = Button(main, text="Delay Comparison Graph", command=delayGraph)
graphButton.place(x=50,y=200)
graphButton.config(font=font1)


font1 = ('times', 12, 'bold')
text=Text(main,height=20,width=150)
scroll=Scrollbar(text)
text.configure(yscrollcommand=scroll.set)
text.place(x=10,y=250)
text.config(font=font1)


main.config(bg='snow3')
main.mainloop()
