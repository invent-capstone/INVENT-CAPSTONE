#Libraries
import RPi.GPIO as GPIO
import time
import sys
from socket import *
import socketserver
import os
import argparse
import cv2
import numpy as np
from threading import Thread
import importlib.util
from time import ctime
from time import sleep 
GPIO.setmode(GPIO.BCM) #GPIO Mode (BOARD / BCM)
turnLights = False
GPIO_TRIGGER = 17 #ultra sonic pin
GPIO_ECHO = 27 # ultrasonic pin
GPIO.setwarnings(False) #enable warning from GPIO
AN2 = 24 # set pwm2 pin on MDDS10 to GPIO 25
AN1 = 25 # set pwm1 pin on MDDS10 to GPIO 24
DIG2 = 18 # set dir2 pin on MDDS10 to GPIO 23
DIG1 = 23 # set dir1 pin on MDDS10 to GPIO 18
GPIO.setup(AN2, GPIO.OUT) # set pin as output
GPIO.setup(AN1, GPIO.OUT) # set pin as output
GPIO.setup(DIG2, GPIO.OUT) # set pin as output
GPIO.setup(DIG1, GPIO.OUT) # set pin as output
GPIO.setup(GPIO_TRIGGER, GPIO.OUT) #set pin as output
GPIO.setup(GPIO_ECHO, GPIO.IN) #set pin as input
p1 = GPIO.PWM(AN1, 100) # set pwm for M1
p2 = GPIO.PWM(AN2, 100) # set pwm for M2
sleep(1) # delay for 1 seconds
photocellPin = 4 #photocell pin
greenPin   = 5 #rgb light pin (green)
redPin = 6 #rgb light pin (red)
bluePin  = 22 #rgb light pin (blue)

HOST=""
PORT = 26968
BUFFSIZE = 1024
ADDR = (HOST,PORT)


#Setting up the local wifi connection
tcpSerSock = socket(AF_INET,SOCK_STREAM) #ipv4, full duplex
socketserver.TCPServer.allow_reuse_address=True #use socket even if already in use
socket.allow_reuse_address=True #use socket even if already in use
tcpSerSock.setsockopt(SOL_SOCKET,SO_REUSEADDR,1) #use socket even if already in use
tcpSerSock.bind(ADDR)
tcpSerSock.listen(5) #buffer queue
tcpSerSock.settimeout(0.00001)
    


class VideoStream:
    #Camera object that controls video streaming from the Picamera
    def __init__(self,resolution=(320,240),framerate=0):
        # Initialize the PiCamera and the camera image stream
        self.stream = cv2.VideoCapture(0)
        ret = self.stream.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
        ret = self.stream.set(3,resolution[0])
        ret = self.stream.set(4,resolution[1])
            
        # Read first frame from the stream
        (self.grabbed, self.frame) = self.stream.read()

        # Variable to control when the camera is stopped
        self.stopped = False

    def start(self):
    # Start the thread that reads frames from the video stream
        Thread(target=self.update,args=()).start()
        return self

    def update(self):
        # Keep looping indefinitely until the thread is stopped
        while True:
            # If the camera is stopped, stop the thread
            if self.stopped:
                # Close camera resources
                self.stream.release()
                return

            # Otherwise, grab the next frame from the stream
            (self.grabbed, self.frame) = self.stream.read()

    def read(self):
        # Return the most recent frame
        return self.frame

    def stop(self):
        # Indicate that the camera and thread should be stopped
        self.stopped = True


# Define and parse input arguments 
parser = argparse.ArgumentParser()
parser.add_argument('--modeldir', help='Folder the .tflite file is located in',required=True)
parser.add_argument('--graph', help='Name of the .tflite file, if different than detect.tflite', default='detect.tflite')
parser.add_argument('--labels', help='Name of the labelmap file, if different than labelmap.txt', default='labelmap.txt')
parser.add_argument('--threshold', help='Minimum confidence threshold for displaying detected objects', default=0.75)
parser.add_argument('--resolution', help='Desired webcam resolution in WxH. If the webcam does not support the resolution entered, errors may occur.', default='1280x720')
parser.add_argument('--edgetpu', help='Use Coral Edge TPU Accelerator to speed up detection', action='store_true')

args = parser.parse_args()

MODEL_NAME = args.modeldir #retreiving models 
GRAPH_NAME = args.graph #retreiving graphs
LABELMAP_NAME = args.labels #retreiving labels
min_conf_threshold = float(args.threshold)  #setting up the threshhold for classification
resW, resH = args.resolution.split('x')
imW, imH = int(resW), int(resH)
use_TPU = args.edgetpu

pkg = importlib.util.find_spec('tflite_runtime')
if pkg:
    from tflite_runtime.interpreter import Interpreter
    if use_TPU:
        from tflite_runtime.interpreter import load_delegate
else: #incase another models are used
    from tensorflow.lite.python.interpreter import Interpreter
    if use_TPU:
        from tensorflow.lite.python.interpreter import load_delegate

# If using Edge TPU, assign filename for Edge TPU model
if use_TPU:
    # If user has specified the name of the .tflite file, use that name, otherwise use default 'edgetpu.tflite'
    if (GRAPH_NAME == 'detect.tflite'):
        GRAPH_NAME = 'edgetpu.tflite'       

# Get path to current working directory
CWD_PATH = os.getcwd()

# Path to .tflite file, which contains the model that is used for object detection
PATH_TO_CKPT = os.path.join(CWD_PATH,MODEL_NAME,GRAPH_NAME)

# Path to label map file
PATH_TO_LABELS = os.path.join(CWD_PATH,MODEL_NAME,LABELMAP_NAME)

# Load the label map
with open(PATH_TO_LABELS, 'r') as f:
    labels = [line.strip() for line in f.readlines()]

if use_TPU:
    interpreter = Interpreter(model_path=PATH_TO_CKPT, experimental_delegates=[load_delegate('libedgetpu.so.1.0')])
    print(PATH_TO_CKPT)
else:
    interpreter = Interpreter(model_path=PATH_TO_CKPT)

interpreter.allocate_tensors()

# Get model details
input_details = interpreter.get_input_details() #retreives required height and width for the image
output_details = interpreter.get_output_details()
height = input_details[0]['shape'][1]
width = input_details[0]['shape'][2]
floating_model = (input_details[0]['dtype'] == np.float32)

input_mean = 127.5 #values for pixel normalization
input_std = 127.5 #values for pixel normalization

if labels[0] == '???':
    del(labels[0])
# Initialize frame rate calculation
# Initialize video stream
videostream = VideoStream(resolution=(imW,imH),framerate=0).start()

'''
Retrieves the frame from camera
and processes it to check its content
'''
def processImage(movementLeft):
    startLoop=True
    while(startLoop):
        exec=time.time()
        frame = videostream.read()
        videostream.stop()
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_resized = cv2.resize(frame_rgb, (width, height))
        input_data = np.expand_dims(frame_resized, axis=0)

        # Normalize pixel values if using a floating model (i.e. if model is non-quantized)
        if floating_model:
            input_data = (np.float32(input_data) - input_mean) / input_std

        # Perform the actual detection by running the model with the image as input
        interpreter.set_tensor(input_details[0]['index'],input_data)
        interpreter.invoke()

        # Retrieve detection results
        boxes = interpreter.get_tensor(output_details[0]['index'])[0] # Bounding box coordinates of detected objects
        classes = interpreter.get_tensor(output_details[1]['index'])[0] # Class index of detected objects
        scores = interpreter.get_tensor(output_details[2]['index'])[0] # Confidence of detected objects
        #num = interpreter.get_tensor(output_details[3]['index'])[0]  # Total number of detected objects (inaccurate and not needed)

        # Loop over all detections and draw detection box if confidence is above minimum threshold
        for i in range(len(scores)):
            if ((scores[i] > min_conf_threshold) and (scores[i] <= 1.0)):
                ymin = int(max(1,(boxes[i][0] * imH)))
                xmin = int(max(1,(boxes[i][1] * imW)))
                ymax = int(min(imH,(boxes[i][2] * imH)))
                xmax = int(min(imW,(boxes[i][3] * imW)))
                object_name = labels[int(classes[i])] # Look up object name from "labels" array using class index
                label = '%s: %d%%' % (object_name, int(scores[i]*100)) # Example: 'person: 72%'
                labelSize, baseLine = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2) # Get font size
                label_ymin = max(ymin, labelSize[1] + 10) # Make sure not to draw label too close to top of window
                cv2.rectangle(frame, (xmin, label_ymin-labelSize[1]-10), (xmin+labelSize[0], label_ymin+baseLine-10), (255, 255, 255), cv2.FILLED) # Draw white box to put label text in
                cv2.putText(frame, label, (xmin, label_ymin-7), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2) # Draw label text
                if("traffic" in object_name): #deciding output
                    for y in range(640):
                        if frame[y][360][2]>=190 :
                            Stop()
                            object_name="Red "+object_name
                            break
                else:
                    startLoop=False #break loop
                if(("traffic" in object_name) and (not "Red" in object_name)):
                    startLoop=False
                    object_name="Green"+object_name
                    moveForward(20,movementLeft)
                if("parking" in object_name or "base" in object_name):
                    Stop()
                    moveRight(20,0.600)
                    moveForward(20,1)
                    startLoop=False
                if("traffic" in object_name or "parking" in object_name or "base" in object_name):
                    print(object_name)        
                print(time.time()-exec)
#Command for the car to start driving
def straightLine():
    print("Obstacle Avoidance")
    global turnLights
    counter = 0
    while(True):
        try: #Retrieve command from phone if available
            tcpCliSock,addr = tcpSerSock.accept()
            data = tcpCliSock.recv(BUFFSIZE) 
        except:
            data=False
        print(data)
        if data:
            if("stop" in str(data)):
                Stop()
                break
            if("lights" in str(data)):
                if turnLights:
                    turnLights=False
                    yellowOff()
                
            else:
                turnLights=True
                if lightLevel(photocellPin) > 10000:
                    yellowOn()
        if turnLights:
            if lightLevel(photocellPin) > 10000:
                yellowOn()
            else:
                yellowOff()
        dis = int(distance())
        if(dis>20):
            moveForward(20,0.70)
        else:
            while (distance()<=20):
                moveRight(20,0.300)
                counter=counter+0.400
            moveForward(20,2)
            moveLeft(20,counter+0.05)
            moveForward(20,1.2)
            moveLeft(20,counter)
            moveForward(20,1.2+counter)
            moveRight(20,counter-0.150)
            counter=0
            Stop()
            break
    moveForward(20,0.6)

#Command for the car to stop driving
def Stop():
    print("Stopped")
    p1.start(0)
    p2.start(0)

#Command for the car to drive backward
def moveBackward (speed,time):
    print("Backward")
    GPIO.output(DIG1, GPIO.HIGH)
    GPIO.output(DIG2, GPIO.HIGH) 
    p1.start(speed) 
    p2.start(speed+2)
    sleep(time)
    p1.start(0)
    p2.start(0)

#Command for the car to move forward
def moveForward(speed,time):
    print("Forward") 
    GPIO.output(DIG1, GPIO.LOW)
    GPIO.output(DIG2, GPIO.LOW) 
    p1.start(speed) 
    p2.start(speed+2)
    processImage(time)
    sleep(time)
    p1.start(0)
    p2.start(0)
    
#Command for the car to move left
def moveLeft(speed,time):
    print("Left") 
    GPIO.output(DIG1, GPIO.LOW)
    GPIO.output(DIG2, GPIO.HIGH) 
    p1.start(speed) 
    p2.start(speed+2) 
    sleep(time)
    p1.start(0)
    p2.start(0)
    
#Command for the car to move right
def moveRight(speed,time):
    print("Right") 
    GPIO.output(DIG1, GPIO.HIGH)
    GPIO.output(DIG2, GPIO.LOW) 
    p1.start(speed) 
    p2.start(speed+2) 
    sleep(time)
    p1.start(0)
    p2.start(0)
    
#Measure distance returned by ultrasonic
def distance():
    # set Trigger to HIGH
    GPIO.output(GPIO_TRIGGER, True)
 
    # set Trigger after 0.01ms to LOW
    time.sleep(0.00001)
    GPIO.output(GPIO_TRIGGER, False)
 
    StartTime = time.time()
    StopTime = time.time()
 
    # save StartTime
    while GPIO.input(GPIO_ECHO) == 0:
        StartTime = time.time()
 
    # save time of arrival
    while GPIO.input(GPIO_ECHO) == 1:
        StopTime = time.time()
 
    # time difference between start and arrival
    TimeElapsed = StopTime - StartTime
    # multiply with the sonic speed (34300 cm/s)
    # and divide by 2, because there and back
    distance = (TimeElapsed * 34300) / 2
    return distance

#Function to measure light levels using photocell
def lightLevel (pin_to_circuit):
    count = 0
    #Output on the pin for 
    GPIO.setup(pin_to_circuit, GPIO.OUT)
    GPIO.output(pin_to_circuit, GPIO.LOW)
    sleep(0.001)
    #Change the pin back to input
    GPIO.setup(pin_to_circuit, GPIO.IN)
  
    #Count until the pin goes high
    while (GPIO.input(pin_to_circuit) == GPIO.LOW):
        count += 1
    return count

#Helper method for turning lights on
def blink(pin):
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.HIGH)
    
#Helper method for turning lights off
def turnOff(pin):
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.LOW)
    
#Function for turning the lights on
def yellowOn():
    blink(redPin)
    blink(greenPin)
    blink(bluePin)
    
#Function for turning the lights off
def yellowOff():
    turnOff(redPin)
    turnOff(greenPin)
    turnOff(bluePin)
 
#Setting up the car 
moveBackward(20,0.100)
yellowOff()

while True:
    try:
        tcpCliSock,addr = tcpSerSock.accept()
    except:
        data=""
    while True:
        if turnLights:
            if lightLevel(photocellPin) > 10000:
                yellowOn()
            else:
                yellowOff()
        try: #Retrieve command from phone if available
            data = tcpCliSock.recv(BUFFSIZE)
        except:
            data=False
        if not data:
            break
        if "straight" in str(data):
            straightLine()
        if "lights" in str(data):
            if turnLights:
                turnLights=False
                yellowOff()
            else:
                turnLights=True
                if lightLevel(photocellPin) > 10000:
                    yellowOn()
            print(turnLights)
        if "right" in str(data):
            moveRight(50,1)
        if "left" in str(data):
            moveLeft(50,1)
        if("stop" in str(data)):
            Stop()
            
#Close ports when terminated
tcpSerSock.close()



