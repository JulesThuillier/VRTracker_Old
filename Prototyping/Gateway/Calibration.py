#!/usr/bin/env python
from utils.Observer import Observer
from Camera import Camera
import numpy as np
from parse import *
import time

class Calibration:
    """
    This calibration is aimed at receiving calibration datas from
    the websocket server, and control the calibration sequence.
    It holds the 3D World Coordinates sent over websocket.
    Calls cameras calibration function to save 2D calibration points
    and calculate a new projection matrix on calibration exit
    """

    points2D = []
    cameras = {}

    def __init__(self, server, client, cameras, tag):
        print "Init Calibration"
        self.cameras = cameras
        self.server = server
        self.client = client
        self.tag = tag
        self.tag.setCalibrationMode()

    def push(self, message):
        if message == "enter":
            print "Start calibration"
            for key in self.cameras:
                    if isinstance(self.cameras[key], Camera):
                        self.cameras[key].enterCalibrationMode()
                        self.server.send_message(self.client, "Camerea detected : " + self.cameras[key].macadress)
            self.server.send_message(self.client, "Calibration Started")

        elif message == "exit":
            print "End calibration, calculates..."
            self.server.send_message(self.client, "Calibration Finished, calculating matrix...")
            for key in self.cameras:
                    if isinstance(self.cameras[key], Camera):
                        if len(self.cameras[key].listOf2D3DPairCalibration)<4:
                            self.server.send_message(self.client, "Camera " + self.cameras[key].macadress + " has only " + str(len(self.cameras[key].listOf2D3DPairCalibration)) + " calibration point, 4 are required. This camera won't be calibrated")
                        else:
                            camPosition = self.cameras[key].exitCalibrationMode()
                            self.server.send_message(self.client, str(camPosition))

            self.tag.setIRoff()
            self.tag.setRGBoff()

        elif message == "on":
            self.tag.setIRon()
            self.tag.setRGB(1023,0,0)
            self.server.send_message(self.client, "Tag turned ON")

        elif message == "off":
            self.tag.setIRoff()
            self.tag.setCalibrationMode()
            self.server.send_message(self.client, "Tag turned OFF")

        else:
            extracted_data = parse("calib:{}-{}-{}", message)
            if extracted_data != None and len(extracted_data.fixed) == 3:

                for key in self.cameras:
                    if isinstance(self.cameras[key], Camera):
                        self.cameras[key].prepToRecordCalibrationPoint2D()
                # Toggle IR Led of the Tag for 1 second to record the points
                self.tag.setRGB(1023,0,0)
                self.tag.setIRonMax()
                time.sleep(1)
                self.tag.setIRoff()
                self.tag.setCalibrationMode()

                self.server.send_message(self.client, "New calibration point received")
                xyz = [int(extracted_data.fixed[0]), int(extracted_data.fixed[1]), int(extracted_data.fixed[2])]

                for key in self.cameras:
                    if isinstance(self.cameras[key], Camera):
                        xyposition = self.cameras[key].saveCalibrationPoint2D(xyz)
                        self.server.send_message(self.client, "Camera " + str(key) + " 2D position : " + str(xyposition))
