from utils.Observer import Observer
from Camera import Camera

class Calibration:

    points2D = []

    def __init__(self):
        print "Init Point 3D"
        self.newPoint2DObserver = Calibration.NewPoint2DObserver(self)
        self.point2DDeletedObserver = Calibration.Point2DDeletedObserver(self)
        self.point2DUpdateObserver = Calibration.Point2DUpdateObserver(self)

    def push(self, message):
        print message


    class Point2DUpdateObserver(Observer):
        def __init__(self, outer):
            self.outer = outer
        def update(self, observable, arg):
            print("Position update Observer in Point 3D")
            #TODO


    class NewPoint2DObserver(Observer):
        def __init__(self, outer):
            self.outer = outer
        def update(self, observable, arg):
            print("New 2D Point Observer in Point 3D")
            if isinstance(observable.outer, Camera):
                #TODO check if this point could be owned by this user, if yes add it to the list
                self.outer.add(arg)

                # Add Observer for position update on last 2D Point added from Camera
                observable.outer.points2D[-1].positionUpdateNotifier.addObserver(self.outer.point2DUpdateObserver)

    class Point2DDeletedObserver(Observer):
        def __init__(self, outer):
            self.outer = outer
        def update(self, observable, arg):
            print("2D Point deleted Observer in Point 3D")
            if isinstance(arg, Camera):
                print ("points2D length : " + str(len(self.outer.points2D)))
                self.outer.delete(arg)
                print ("points2D length after remove : " + str(len(self.outer.points2D)))
                # Remove Observer for position update on 2D Point from Camera
                observable.outer.points2D[-1].positionUpdateNotifier.deleteObserver(self.outer.point2DUpdateObserver)