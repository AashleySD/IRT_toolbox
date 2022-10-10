#!/usr/bin/env python3
"""
Authors: Aashley Sardjoe Mishre [1] and Oleh Dzyubachyk [2]
Affiliations: 1. Leiden university medical center, Radiology department, 2. Leiden university medical center, Division of Image Processing (LKEB)
Date: 15-06-2021
Last updated: 27-12-2021
    
Title script: ReadData_singleParticipant_functions
Purpose: This script includes all functions for reading and displaying IRT images from a single dataset of one participant.              
"""

from os import getcwd, path
import numpy as np
import flirimageextractor
from matplotlib import cm
from PyQt5.QtWidgets import * 
from PyQt5.QtGui import *
from PyQt5.QtCore import Qt
 
def readin_temp(self): 
    temp_numpy = []
    
    #the filepath of the first image is stored and used for the next image upload
    if not self.filepathuser:
        initdir_user = getcwd()
    else:
        initdir_user = self.filepathuser[0]
    
    dialog = QFileDialog()
    dialog.FileMode(QFileDialog.ExistingFile)
    filepathjpg, _filter = dialog.getOpenFileName(None,"Select image file",initdir_user,"Image (*.png *.jpeg *.jpg *.tiff)")

    if filepathjpg:
        flir = flirimageextractor.FlirImageExtractor(palettes=[cm.jet, cm.bwr, cm.gist_ncar])
        flir.process_image(filepathjpg)
        temp_numpy = flir.get_thermal_np()

    return temp_numpy, filepathjpg

    
def button_img_readin(self):
    positionImg = int(self.listWidget.currentRow()) 
 
    temp_numpy,filepath_jpg = readin_temp(self)
    if temp_numpy != []:
        self.listWidget.currentItem().setIcon(QIcon(filepath_jpg))
        filename = path.basename(filepath_jpg)
        if positionImg == 0:
            fn = "Reference image: " + filename
            np.save(path.join(self.folder,'refimg'),temp_numpy)
        else:
            fn = filename
        self.listWidget.currentItem().setText(path.splitext(fn)[0])
        self.filenames[positionImg] = fn    
        self.filepathuser[positionImg] = filepath_jpg
        self.data_readin[positionImg] = temp_numpy
    
        bempty = False  
        ii = 0
        while not bempty and (ii < len(self.filenames)):
            bempty = self.filenames[ii] == ''
            ii += 1
        
        self.button_alignimg.setEnabled(not bempty)
    
    
def show_img_upload(self):
    
    answer_user = self.upload_img_userinput.value()
    
    for img_list in range(answer_user,self.listWidget.count()):
        self.listWidget.takeItem(self.listWidget.count()-1)
        self.filenames.pop()
        self.filepathuser.pop()
        self.data_readin.pop()
        self.alignThresh.pop()
    
    for img_list in range(self.listWidget.count(), answer_user):
        item = QListWidgetItem(QIcon("Images/capture_res.png"),'')
        item.setToolTip('')
        self.listWidget.addItem(item)
        
        self.filenames.append('')
        self.filepathuser.append('')
        self.data_readin.append([])
        self.alignThresh.append(25)
        
        self.button_alignimg.setEnabled(False)   