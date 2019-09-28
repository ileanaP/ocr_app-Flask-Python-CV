# -*- coding: utf-8 -*-
"""
Created on Sat Sep  7 19:43:50 2019

@author: ILENUCA
"""

import os
from app import app
from app.services.ImagePreprocessingService import ImagePreprocessingService
from app.services.ImageSegmentationService import ImageSegmentationService
#from app.services.ImageSegmentationService import ImageSegmentationService

class ImageService:
    def __init__(self, filename): #s-ar putea ca filename sa fie NONE
        self.filename = filename
        self.filePath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        self.operator = None
        
        self.targetFilename = self.filename.replace(".", "_preprocessing.")
        self.targetFilePath = os.path.join(app.config['RESULTS_FOLDER'], self.targetFilename)
        
    def apply(self, operation):
        returnvalue = '0'
        
        if operation == 'preprocessing':
            
            self.operator = ImagePreprocessingService(self.filePath)
            self.operator.apply(self.targetFilePath)
            
            if self.operator.processed:
                returnvalue = self.targetFilename
                
        elif operation == 'segmentation':
            
            self.operator = ImageSegmentationService(self.filename, self.targetFilePath) # sa ma folosesc de filePath            
            self.operator.apply()
            
            if self.operator.processed:
                
                returnvalue = 'ok'
                
        else:
            returnvalue = 'operation not yet defined'
            
        return returnvalue
            