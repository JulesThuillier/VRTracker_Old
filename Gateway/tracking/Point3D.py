import Point2D
from collections import deque
from math import sqrt

# Buffer of a 2D point
class Point3D():

    points2D = []

    bufferSize = 50
    buffer = deque(maxlen=bufferSize)

    def __init__(self, length=50):
        bufferSize = length

    def update(self):
        print ("TODO")

    def add(self, x, y, z):
        buffer.append([x,y])


    # Warning : does not pop
    def get(self):
        return buffer[-1]

    def getAll(self):
        return list(buffer)


    # Check distance between last 3D point in buffer and the point in parameter (not squared)
    def distance(self, x, y, z):
        lastxy = buffer[-1]
        distx = abs(lastxy[0] - x)
        disty = abs(lastxy[1] - y)
        distz = abs(lastxy[2] - z)
        return distx*distx + disty*disty + distz*distz
