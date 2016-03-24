#!/usr/bin/env python
from Camera import Camera
from utils.Observer import Observer
from Point2D import Point2D
import compute
import numpy as np


# Represent a 3D Position with observers on 2D point updates
class Point3D:

    MAX_DISTANCE_ERROR = 20

    def __init__(self, user):
        print "Init Point 3D"
        self.lastXYZ = []
        self.points2D = []
        self.user = user
        self.pointLost = True
        self.newPoint2DObserver = Point3D.NewPoint2DObserver(self)
        self.point2DDeletedObserver = Point3D.Point2DDeletedObserver(self)
        self.point2DUpdateObserver = Point3D.Point2DUpdateObserver(self)
        self.buffer3DPositions = np.array([], dtype=np.float32).reshape(0,3)

    def update(self):
        print ("TODO")

    def add(self,point2D):
        '''
        Add 2D Point to this 3D Point calculation
        :param point2D:
        :return:
        '''
        self.points2D.append(point2D)
        point2D.assign(self)
        print "ADDING POINT FROM : " + point2D.camera.macadress
        # Check if there is at least two points, otherwise 3D Point is Lost
        if(len(self.points2D)>1):
            self.pointLost = False
            if(self.user.tag != None):
                self.user.tag.debugUserTracked()
        else:
            self.pointLost = True
            if(self.user.tag != None):
                self.user.tag.debugUserLost()


    def delete(self,point2D):
        '''
        Removes 2D Point from this 3D Point calculation
        :param point2D:
        :return:
        '''
        # Remove the Point2D if parameter is a Point2D
        if isinstance(point2D, Point2D):
            point2D.unassign()
            self.points2D.remove(point2D)
        # If the parameter is a Camera, we remove all instances of Point2D from that Camera
        elif isinstance(point2D, Camera):
            for point in self.points2D:
                if point.camera == point2D: # Here point2D is a Camera
                    print "REMOVING POINT FROM : " + point2D.macadress
                    point.unassign()
                    self.points2D.remove(point)
        # Check if there is at least two points, otherwise 3D Point is Lost
        if(len(self.points2D)>1):
            self.pointLost = False
            if(self.user.tag != None):
                self.user.tag.debugUserTracked()
        else:
            self.pointLost = True
            if(self.user.tag != None):
                self.user.tag.debugUserLost()

    # Warning : does not pop
    def get(self):
        return buffer[-1]

    def getAll(self):
        return list(buffer)

    def smooth(self, positionList):
        if np.ma.size(positionList, 0) > 1:
            return np.average(positionList, axis=0, weights=range(0,np.ma.size(positionList, 0),1))
        else:
            return positionList[0,:]


    # Check distance between last 3D point in buffer and the point in parameter (not squared)
    def distance(self, x, y, z):
        if len(self.lastXYZ) == 3:
            distx = abs(self.lastXYZ[0] - x)
            disty = abs(self.lastXYZ[1] - y)
            distz = abs(self.lastXYZ[2] - z)
            return distx*distx + disty*disty + distz*distz


    class Point2DUpdateObserver(Observer):
        def __init__(self, outer):
            self.outer = outer
        def update(self, observable, arg):
            if len(self.outer.points2D) >1:
                print "COUNT : " + str(len(self.outer.points2D))
             # elif len(self.outer.points2D) > 2:
                list3DPositions = np.array([], dtype=np.float32).reshape(0,3)

                # Calculate all 3D positions from all combinations of 2D pairs
                # and average those positions.
               # print "====================== 2D UPDATE OBSERVER ======================"
                for i in range(0, len(self.outer.points2D)-1):
                    for j in range(i+1, len(self.outer.points2D)):
                        value = compute.calculate3DPosition(self.outer.points2D[i], self.outer.points2D[j])
                        value = value.reshape(1,3)
                        list3DPositions = np.append(list3DPositions, value, axis=0)
                list3DPositions =  np.average(list3DPositions, axis=0)
               #u print "LIST : " + str( list3DPositions)
                # List of 10 last positions
                while np.ma.size(self.outer.buffer3DPositions, 0) >= 10:
                    self.outer.buffer3DPositions = np.delete(self.outer.buffer3DPositions, 0, 0)

                self.outer.buffer3DPositions = np.append(self.outer.buffer3DPositions, [list3DPositions], axis=0)
                #print self.outer.buffer3DPositions

                smoothedPosition = self.outer.smooth(self.outer.buffer3DPositions)
               # print "SMOOTHED : " + str(smoothedPosition)
                self.outer.user.sendPositionUpdate(smoothedPosition)
                self.outer.lastXYZ = smoothedPosition
            else:
                print "3D point LOST"
                self.outer.pointLost = True
                self.outer.user.tag.debugUserLost()


    class NewPoint2DObserver(Observer):
        def __init__(self, outer):
            self.outer = outer

        def update(self, observable, arg):
            if isinstance(observable.outer, Camera):
                temp2D = observable.outer.points2D[-1]

                # User is lost and receive new 2D Point
                if self.outer.pointLost:

                    # 1: Check if new 2D Point comes from same camera as another 2D Point used here (if yes, discard)
                    for point in self.outer.points2D:
                        if point.camera.macadress == temp2D.camera.macadress:
                            print "2D Point from same camera : Replace - " + point.camera.macadress
                            self.outer.delete(point)
                            # Add the New 2D Point to this 3D Point
                            self.outer.add(temp2D)
                            # Add Observer for position update on last 2D Point added from Camera
                            observable.outer.points2D[-1].positionUpdateNotifier.addObserver(self.outer.point2DUpdateObserver)
                            return

                    # Add the point to the user if user doesn't have 2 2D Points
                    if len(self.outer.points2D) < 2:
                        print "Adding new 2D Point to 3D Point"
                        # Add the New 2D Point to this 3D Point
                        self.outer.add(temp2D)
                        # Add Observer for position update on last 2D Point added from Camera
                        observable.outer.points2D[-1].positionUpdateNotifier.addObserver(self.outer.point2DUpdateObserver)
                        return


                # User is not lost and receive new 2D Point
                else:
                    # 1: Check if new 2D Point comes from same camera as another 2D Point used here (if yes, discard)
                    for point in self.outer.points2D:
                        if point.camera == temp2D.camera:
                            print "2D Point discard : same camera - " + point.camera.macadress
                            return

                    # 2: Calculate 3D Point position with new 2D point and check position difference (yes difference too high, discard)
                    for point in self.outer.points2D:
                        if point.isLost() ==  False and point.camera.macadress != temp2D.camera.macadress:
                            temp3D = compute.calculate3DPosition(point, temp2D)
                            distance = self.outer.distance(temp3D[0,0], temp3D[1,0], temp3D[2,0])
                          #  print "DISTANCE : " + str(distance)
                            if(distance > self.outer.MAX_DISTANCE_ERROR*self.outer.MAX_DISTANCE_ERROR):
                                print "2D Point discard : too far"
                                #Todo Get this back working
                                return

                    # If we get there, user is not lost, and new point is OK
                    # Add the New 2D Point to this 3D Point
                    print "Adding new 2D Point to 3D Point"
                    self.outer.add(temp2D)
                    # Add Observer for position update on last 2D Point added from Camera
                    observable.outer.points2D[-1].positionUpdateNotifier.addObserver(self.outer.point2DUpdateObserver)

    class Point2DDeletedObserver(Observer):
        def __init__(self, outer):
            self.outer = outer
        def update(self, observable, arg):
            print("2D Point deleted Observer in Point 3D from Camera : ")
            self.outer.delete(observable.outer)
            # Remove Observer for position update on 2D Point from Camera
           # observable.outer.points2D[-1].positionUpdateNotifier.deleteObserver(self.outer.point2DUpdateObserver)

    def __del__(self):
        for point in self.points2D:
            point.positionUpdateNotifier.deleteObserver(self.point2DUpdateObserver)
            point.camera.new2DPointNotifier.deleteObserver(self.newPoint2DObserver)
            point.camera.point2DdeletedNotifier.deleteObserver(self.point2DDeletedObserver)