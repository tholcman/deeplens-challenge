import numpy
import math

def default_action(xmin, ymin, xmax, ymax):
    print(xmin, ymin, xmax, ymax)

class NaiveRecognition():
    def __init__(self, action = default_action, size = 5):
        self._action = action
        self._size = size
        self._buffer = []
        self._diff_buffer = []
        self._coeficient = 0.2
        self._top_idx = int(math.floor(self._size / 2))

    def add(self, xmin, ymin, xmax, ymax):
        # test position is float
        position = (ymin + ymax) / 2
        diff = xmax - xmin + ymax - ymin
        #print("{0:.3f},".format(position))
        #return
        if self._shouldIgnore(diff):
            return False 
        self._write(diff, position)
        if self._shouldFire():
            self._action(xmin, ymin, xmax, ymax)

    def _write(self, diff, position): 
        self._buffer.insert(0, position)
        if len(self._buffer) > 5 :
            self._buffer.pop() 
        self._diff_buffer.insert(0, diff)
        if len(self._diff_buffer) > 5 :
            self._diff_buffer.pop() 


    def _shouldIgnore(self, diff):
        if len(self._diff_buffer) < self._size:
            return False 
        mean_diff = numpy.mean(self._diff_buffer)
        min_diff = mean_diff * (1 - self._coeficient)
        max_diff = mean_diff * (1 + self._coeficient)
        return min_diff > diff or diff > max_diff

    def _shouldFire(self):
        if len(self._diff_buffer) < self._size:
            return False 
        min_pos = min(self._buffer)
        pos_diff = 0
        if min_pos != self._buffer[self._top_idx]:
            return False
        for pos in self._buffer:
            pos_diff += pos - min_pos
        if pos_diff < (0.5 * self._size):
            # print('not ', pos_diff)
            return False
        # print('enough ', pos_diff)
        return True
