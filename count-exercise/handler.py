#
# Copyright Amazon AWS DeepLens, 2017
#

# greengrassInfiniteInfer.py
# Runs GPU model inference on a video stream infinitely, and
# publishes a message to topic 'infinite/infer' periodically.
# The script is launched within a Greengrass core.
# If function aborts, it will restart after 15 seconds.
# Since the function is long-lived, it will run forever
# when deployed to a Greengrass core. The handler will NOT
# be invoked in our example since we are executing an infinite loop.
import traceback
import os
import greengrasssdk
from threading import Timer
import time
import awscam
import cv2
import math
import numpy
from threading import Thread
from recognition import NaiveRecognition
import uuid
from datetime import datetime
from tzlocal import get_localzone

# Creating a greengrass core sdk client
client = greengrasssdk.client('iot-data')

# The information exchanged between IoT and clould has
# a topic and a message body.
# This is the topic that this code uses to send messages to cloud
my_name = os.environ['AWS_IOT_THING_NAME']
iotTopic = '$aws/things/{}/infer'.format(my_name)
client.publish(
    topic=iotTopic, 
    payload = '{{"type":"{type}","payload":{{"id":"{id}","time":"{time}","msg":"Camera {name} id up.","datetime":"{datetime}"}}}}'.format(
        id = str(uuid.uuid4()),
        type = 'system',
        time = time.time(),
        name = my_name,
        datetime = datetime.now(get_localzone()).isoformat()
    )
)

ret, frame = awscam.getLastFrame()
ret,jpeg = cv2.imencode('.jpg', frame)
Write_To_FIFO = True
class FIFO_Thread(Thread):
    def __init__(self):
        ''' Constructor. '''
        Thread.__init__(self)

    def run(self):
        fifo_path = "/tmp/results.mjpeg"
        if not os.path.exists(fifo_path):
            os.mkfifo(fifo_path)
        f = open(fifo_path,'w')
        print("Opened Pipe")
        while Write_To_FIFO:
            try:
                f.write(jpeg.tobytes())
            except IOError as e:
                continue

counter = 0

def add_one(xmin, ymin, xmax, ymax):
    global counter
    counter += 1

def send_notification(xmin, ymin, xmax, ymax):
    global client, iotTopic, my_name
    client.publish(
        topic=iotTopic, 
        payload = '{{"type":"{event_type}","payload":{{"id":"{id}","camera":"{camera}","time":"{time}","exercise":"{exercise}","datetime":"{datetime}"}}}}'.format(
            id = str(uuid.uuid4()),
            camera = my_name,
            time = time.time(),
            event_type = 'exercise',
            exercise = 'barbell_up',
            datetime = datetime.now(get_localzone()).isoformat()
        )
    )
    
def merged_handlers(xmin, ymin, xmax, ymax):
    send_notification(xmin, ymin, xmax, ymax)
    add_one(xmin, ymin, xmax, ymax)

recognize = NaiveRecognition(action = merged_handlers, size = 3)

def greengrass_infinite_infer_run():
    try:
        modelPath = "/opt/awscam/artifacts/mxnet_deploy_ssd_resnet50_300_FP16_FUSED.xml"
        modelType = "ssd"
        input_width = 224
        input_height = 224
        max_threshold = 0.6
        outMap = { 1: 'barbell' }
        results_thread = FIFO_Thread()
        results_thread.start()
        # Send a starting message to IoT console
        print("Object detection starts now")

        # Load model to GPU (use {"GPU": 0} for CPU)
        mcfg = {"GPU": 1}
        model = awscam.Model(modelPath, mcfg)
        print("Model loaded")
        ret, frame = awscam.getLastFrame()
        if ret == False:
            raise Exception("Failed to get frame from the stream")
        yscale = float(frame.shape[0]/input_height)
        xscale = float(frame.shape[1]/input_width)

        doInfer = True
        while doInfer:
            start_time = time.time() # start time of the loop
            # Get a frame from the video stream
            ret, frame = awscam.getLastFrame()
            # Raise an exception if failing to get a frame
            if ret == False:
                raise Exception("Failed to get frame from the stream")

            # Resize frame to fit model input requirement
            # cropped = frame[800:1800,:]
            frameResize = cv2.resize(frame, (input_width, input_height))

            # Run model inference on the resized frame
            inferOutput = model.doInference(frameResize)

            # Output inference result to the fifo file so it can be viewed with mplayer
            parsed_results = model.parseResult(modelType, inferOutput)['ssd']
            first = True
            label = '{'
            for obj in parsed_results:
                if (first and obj['prob'] > max_threshold): # and is_expected_size(obj['xmin'], obj['xmax'], obj['ymin'], obj['ymax']):
                    first = False
                    #msg = "{time}   {position}\n".format(time = time.time(), position = (obj['xmin'] + obj['xmax']) / 2)
                    #with open('/tmp/position.txt','a') as log:
                    #    log.write(msg)
                    recognize.add(obj['xmin'], obj['ymin'], obj['xmax'], obj['ymax'])
                    xmin = int( xscale * obj['xmin'] ) + int((obj['xmin'] - input_width/2) + input_width/2)
                    ymin = int( yscale * obj['ymin'] )
                    xmax = int( xscale * obj['xmax'] ) + int((obj['xmax'] - input_width/2) + input_width/2)
                    ymax = int( yscale * obj['ymax'] )
                    cv2.rectangle(frame, (xmin, ymin), (xmax, ymax), (255, 165, 20), 4)
                    label += '"{}": {:.2f},'.format(obj['label'], obj['prob'] )
                    label_show = "{}:    {:.2f}%".format(obj['label'], obj['prob']*100 )
                    cv2.putText(frame, label_show, (xmin, ymin - 30),cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 165, 20), 6)
            label += '"null": 0.0'
            label += '}' 

            cv2.putText(frame, "Count: {}".format(counter), (5, 50), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 165, 20), 6)
            global jpeg
            ret,jpeg = cv2.imencode('.jpg', frame)
            print("FPS: ", 1.0 / (time.time() - start_time))
            
    except Exception as e:
        print(traceback.format_exc())
        print(e)

    # Asynchronously schedule this function to be run again in 15 seconds
    Timer(15, greengrass_infinite_infer_run).start()

# Execute the function above
greengrass_infinite_infer_run()


# This is a dummy handler and will not be invoked
# Instead the code above will be executed in an infinite loop for our example
def handler(event, context):
    return

