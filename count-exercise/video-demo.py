import numpy as np
from mxnet.contrib.ndarray import MultiBoxDetection
import cv2
import mxnet as mx
from timeit import default_timer as timer
from collections import namedtuple

import recognition
Batch = namedtuple('Batch', ['data'])

data_shape = (224, 224)
mean_pixels = mx.nd.array((123, 117, 104)).reshape((3,1,1))
ctx = mx.cpu() #mx.gpu(args.gpu_id)

# video In/Out
cap = cv2.VideoCapture('cut.mp4')
fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter('output.avi',fourcc, 30.0, data_shape, isColor = True)

# load Network
load_symbol, args, auxs = mx.model.load_checkpoint('model/deploy_ssd_resnet50_300', 0)
mod = mx.mod.Module(load_symbol, label_names=None, context=ctx)
mod.bind(for_training=False, data_shapes=[('data', (1, 3, data_shape[0], data_shape[1]))])
mod.set_params(args, auxs)

counter = 0

def addOne(data):
    global counter
    counter += 1

recognize = recognition.NaiveRecognition(action = addOne)

while(cap.isOpened()):
    ret, frame = cap.read()
    data = mx.nd.array(frame)
    if ret == False:
        print('Error while reading')
        break
    image = cv2.resize(frame, data_shape)

    # swap BGR to RGB
    data = image[:, :, (2, 1, 0)]
    # convert to float before subtracting mean
    data = data.astype(np.float32)
    # subtract mean
    data -= mean_pixels
    # organize as [batch-channel-height-width]
    data = np.transpose(data, (2, 0, 1))
    data = data[np.newaxis, :]
    # convert to ndarray
    data = mx.nd.array(data)

    mod.forward(Batch([mx.nd.array(data)]))
    prob = mod.get_outputs()[0].asnumpy()
    prob = np.squeeze(prob)
    
    for obj in prob[:1]:
        recognize.add(obj[2], obj[3], obj[4], obj[5])
        xmin = int( obj[2] * data_shape[0] )
        ymin = int( obj[3] * data_shape[0] )
        xmax = int( obj[4] * data_shape[0] )
        ymax = int( obj[5] * data_shape[0] )
        cv2.putText(image, '{}'.format(counter), (5, 25),cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 165, 20), 2)
        cv2.rectangle(image, (xmin, ymin), (xmax, ymax), (255, 165, 20), 4)
    cv2.imshow('frame', image)
    out.write(image)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    


cap.release()
cv2.destroyAllWindows()
