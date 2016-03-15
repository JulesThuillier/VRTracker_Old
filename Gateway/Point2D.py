#!/usr/bin/env python
from collections import deque
from utils.Observer import Observer, Observable
from math import sqrt

# Buffer of a 2D point
class Point2D:

    bufferSize = 50
    buffer = deque(maxlen=bufferSize)

    camera = ""

    MAX_FRAME_LOST_BEFORE_DELETE = 30

    lastUpdateCounter = 0 # This counter is incremented every time his Camera receives a frame, either this point is not in the frame
    timeLastUpdated = 0

    def __init__(self, x, y, height, width, camera):
        self.camera = camera
        self.bufferSize = 50
        self.buffer = deque(maxlen=self.bufferSize)
        self.lastUpdateCounter = 0
        self.positionUpdateNotifier= Point2D.PositionUpdateNotifier(self)
        point = {'x': int(x), 'y': int(y), 'height': int(height), 'width': int(width)};
        self.buffer.append(point)
        #TODO Notify point created ==> To associate it to 3D point

    def update(self, x, y, height, width):
        self.lastUpdateCounter = 0
        point = {'x': int(x), 'y': int(y), 'height': int(height), 'width': int(width)};
        self.buffer.append(point)
        #TODO Notify 2D Point updated ==> Update 3D position
        self.positionUpdateNotifier.notifyObservers()

    # Warning : does not pop
    def get(self):
        return self.buffer[-1]

    def getAll(self):
        return list(self.buffer)


    # Check distance between last 2D point in buffer and the point in parameter (not squared)
    def distance(self, x, y):
        lastxy = self.buffer[-1]
        distx = abs(lastxy['x'] - int(x))
        disty = abs(lastxy['y'] - int(y))
        return distx*distx + disty*disty

    # Check distance between last 2D point in buffer and the point in parameter (not squared)
    def sizeDifference(self, height, width):
        lastxy = self.buffer[-1]
        h = abs(lastxy['height'] - int(height))
        w = abs(lastxy['width'] - int(width))
        return h*h + w*w

    def count(self):
        self.lastUpdateCounter += 1

    def isLost(self):
        return self.MAX_FRAME_LOST_BEFORE_DELETE < self.lastUpdateCounter


    class PositionUpdateNotifier(Observable):
        def __init__(self, outer):
            Observable.__init__(self)
            self.outer = outer
        def notifyObservers(self):
                self.setChanged()
                Observable.notifyObservers(self)
