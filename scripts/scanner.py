# -*- coding: utf-8 -*-
"""
Created on Mon Mar 11 11:34:50 2019

@author: ILEANA
"""

import numpy as np
import cv2

class ImageScanner:
    def __init__(self, filename):
        self.image = cv2.imread(filename)
        self.createBorder()
        self.orig = self.image.copy()
        
        self.gray = self.processGrayImage()
        
        self.contours = cv2.findContours(self.gray, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)[1]
        self.maxContour = self.getMaxContourRectangle()
        
#        cv2.drawContours(gray, [self.maxContour], -1, (255,255,255), 2)
        
        warpedImage = self.getTransformedImage(self.orig, self.maxContour/self.ratio)
        scannedImage = cv2.cvtColor(warpedImage, cv2.COLOR_BGR2GRAY)
        scannedImage2 = cv2.threshold(scannedImage,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)[1]
        cv2.imwrite('scannedimage_warped.jpg', warpedImage)
        cv2.imwrite('scannedimage2.jpg', scannedImage2)
        cv2.imwrite('scannedimage.jpg', scannedImage)
        
    def orderPoints(self,a):
        a = a.reshape(4,2)
        xySum = a.sum(axis=1)
        xyDiff = np.diff(a, axis=1)
        
        topL = a[np.argmin(xySum)]
        bottomR = a[np.argmax(xySum)]
        topR = a[np.argmin(xyDiff)]
        bottomL = a[np.argmax(xyDiff)]
    
        return np.array([topL, topR, bottomR, bottomL])
    
    def getTransformedImage(self, img, points):
        points = self.orderPoints(points)
        (topL, topR, bottomR, bottomL) = points.copy() 
        
        newWidth = max(self.distBetweenP(topL,topR), self.distBetweenP(bottomL,bottomR))
        newHeight = max(self.distBetweenP(bottomR,topR), self.distBetweenP(bottomL,topL))
        
        topView = np.array([
                [0,0],
                [newWidth-1,0],
                [newWidth-1, newHeight-1],
                [0, newHeight-1]
                ], dtype="float32")
        
        points = points.astype('float32')
        transformedMatrix = cv2.getPerspectiveTransform(points, topView)
        scannedImage = cv2.warpPerspective(img, transformedMatrix, (newWidth, newHeight))
        
        return scannedImage
        
    def createBorder(self):
        borderType = cv2.BORDER_CONSTANT
        TDLU=[30]*4 
    
        self.image = cv2.copyMakeBorder(self.image, TDLU[0] , TDLU[1] , TDLU[2] , TDLU[3] , borderType, None, 255)
        
    def processGrayImage(self):
        gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        gray = cv2.threshold(gray,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)[1]
        
        height, width, depth = self.image.shape
        self.ratio = 500/width
        newH, newW  = height*self.ratio, width*self.ratio
        gray = cv2.resize(gray, (int(newW), int(newH)))
        gray = cv2.GaussianBlur(gray, (5, 5), 0)
        gray = cv2.Canny(gray,100,200)
        
        return gray;
        
    def getMaxContourRectangle(self):
        cAreas = [self.getContourArea(c) for c in self.contours]
    
        maxContour = self.contours[cAreas.index(max(cAreas))]
        
        minX = maxContour[maxContour[:, :, 0].argmin()][0][0]
        maxX = maxContour[maxContour[:, :, 0].argmax()][0][0]
        minY = maxContour[maxContour[:, :, 1].argmin()][0][1]
        maxY = maxContour[maxContour[:, :, 1].argmax()][0][1]
        
        topLeft = np.array([np.array([minX, minY])])
        topRight = np.array([np.array([minX, maxY])])
        bottomLeft = np.array([np.array([maxX, minY])])
        bottomRight = np.array([np.array([maxX, maxY])])
        
        maxContour = np.array([topLeft, topRight, bottomRight, bottomLeft])
        
        return maxContour
    
    def getContourArea(self, contour):
        minX = contour[contour[:, :, 0].argmin()][0][0]
        maxX = contour[contour[:, :, 0].argmax()][0][0]
        minY = contour[contour[:, :, 1].argmin()][0][1]
        maxY = contour[contour[:, :, 1].argmax()][0][1]
        
        return (maxX - minX)*(maxY - minY)
    
    def distBetweenP(self, a,b):
        return int(np.sqrt((b[0]-a[0])**2 + (b[1] - a[1])**2))