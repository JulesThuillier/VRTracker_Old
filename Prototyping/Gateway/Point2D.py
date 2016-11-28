#!/usr/bin/env python
from collections import deque
from utils.Observer import Observer, Observable
from math import sqrt
from datetime import datetime

# Buffer of a 2D point
class Point2D:

    bufferSize = 50
    buffer = deque(maxlen=bufferSize)

    camera = ""

    MAX_FRAME_LOST_BEFORE_DELETE = 15

    lastUpdateCounter = 0 # This counter is incremented every time his Camera receives a frame, either this point is not in the frame
    timeLastUpdated = 0

    def __init__(self, x, y, height, width, camera):
        self.MAX_DELAY_MS = 100000
        self.lastUpdateTime = datetime.now()
        self.pointLost = False
        self.point3Dassigned = None
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
        self.lastUpdateTime = datetime.now()
        point = {'x': int(x), 'y': int(y), 'height': int(height), 'width': int(width)};
        self.buffer.append(point)
        self.positionUpdateNotifier.notifyObservers()

    # Warning : does not pop
    def get(self):
        return self.buffer[-1]

    def getAll(self):
        return list(self.buffer)


    # Check distance between last 2D point in buffer and the point in parameter (not squared)
    def distance(self, x, y):
        '''
        Measures distance between last 2D point in buffer
        and the point in parameter (not squared)
        Helps determine which point is which when a new frame is
        received in Camera
        :param x:
        :param y:
        :return:
        '''
        lastxy = self.buffer[-1]
        distx = abs(lastxy['x'] - int(x))
        disty = abs(lastxy['y'] - int(y))
        return distx*distx + disty*disty

    def sizeDifference(self, height, width):
        '''
        Measures size difference between last 2D point in buffer
        and the point in parameter (not squared)
        Helps determine which point is which when a new frame is
        received in Camera
        :param height:
        :param width:
        :return:
        '''
        lastxy = self.buffer[-1]
        h = abs(lastxy['height'] - int(height))
        w = abs(lastxy['width'] - int(width))
        return h*h + w*w

    def count(self):
        '''
        Simply counting frame updates from the camera
        Incremented each time a frame is received without this point
        Count is back to zero when the point is back in the frame
        :return:
        '''
        self.lastUpdateCounter += 1

    def isLost(self):
        '''
        Check if 2D point is lost
        Either because the camera received too many frames
        without this point, Or too much time elapsed since it
        was last updated
        :return:
        '''
        timeSinceLastUpdate = datetime.now() - self.lastUpdateTime
       # print timeSinceLastUpdate.microseconds
        if (self.MAX_FRAME_LOST_BEFORE_DELETE < self.lastUpdateCounter):
            self.pointLost = True
           # print "LOST : FRAME"
        # Check if time elapsed since last update not too long, or discard the point
        elif (timeSinceLastUpdate.microseconds > self.MAX_DELAY_MS or timeSinceLastUpdate.seconds > 0):
            self.pointLost = True
           # print "LOST : TOO OLD"
        return self.pointLost

    def assign(self, point3D):
        '''
        Save assignement of this 2D Point to a 3D point
        This point cannot be assigned to another 3D Point
        :param point3D:
        :return:
        '''
        self.point3Dassigned = point3D

    def unassign(self):
        '''
        Remove assignement of the 2D point to a 3D Point
        This point if now free to be reassigned
        :return:
        '''
        self.point3Dassigned = None


    class PositionUpdateNotifier(Observable):
        '''
        Notify Observers (in 3D Point) when the position
        has been updated
        '''
        def __init__(self, outer):
            Observable.__init__(self)
            self.outer = outer
        def notifyObservers(self):
                self.setChanged()
                Observable.notifyObservers(self)
