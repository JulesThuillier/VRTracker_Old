import cv2
import numpy as np

"""
This file is the only one calling OpenCV function
to triangulate 3D position or calculate projection matrix
during calibration
"""

def calculate3DPosition(projMat1, projMat2, xy1, xy2):

    triangulationOutput = cv2.triangulatePoints(projMat1,projMat2, np.float32(xy1), np.float32(xy2))

    mypoint1 = np.array([triangulationOutput[0], triangulationOutput[1], triangulationOutput[2]])
    mypoint1 = mypoint1.reshape(-1, 3)
    mypoint1 = np.array([mypoint1])
    P_24x4 = np.resize(projMat1[0], (4,4))
    P_24x4[3,0] = 0
    P_24x4[3,1] = 0
    P_24x4[3,2] = 0
    P_24x4[3,3] = 1

    projected = cv2.perspectiveTransform(mypoint1, P_24x4)
    output2 = triangulationOutput[:-1]/triangulationOutput[-1]

    #TODO calculate point again with second proj mat, and calculate middle
    return output2

def calculateProjectionMatrix(camera, points3D):

	ret, rvec, tvec = cv2.solvePnP(points3D, camera.pointsCalibration, camera.camera_matrix, camera.distortion_coefficient)
	rotM_cam = cv2.Rodrigues(rvec)[0]

	# calculate camera position (= translation), from 0,0,0 point
	cameraPosition = -np.matrix(rotM_cam).T * np.matrix(tvec)
	print "Camera position : "
	print cameraPosition

	camMatrix = np.append(cv2.Rodrigues(rvec)[0], tvec, 1)
	projectionMatrix = np.dot(camera.camera_matrix, camMatrix)

	return projectionMatrix