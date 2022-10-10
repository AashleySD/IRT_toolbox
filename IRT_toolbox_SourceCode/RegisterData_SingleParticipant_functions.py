"""
Authors: Aashley Sardjoe Mishre [1] and Oleh Dzyubachyk [2]
Affiliations: 1. Leiden university medical center, Radiology department, 2. Leiden university medical center, Division of Image Processing (LKEB)
Date: 03-08-2021
Last updated:14-01-2022
    
Title script: RegisterData_SingleParticipant_functions
Purpose: This script includes all subfunctions for registering a single dataset of one participant.

"""

from os import path, listdir
import numpy as np
from image_overlap import overlap_images
from time import sleep
from matplotlib import pyplot
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication
from common_functions import saveRescaledImg, IRT_registration

def Registration_progressbar(self):
    data_in_aligned = self.data_aligned
    dataref_aligned = self.data_ref
    refimg = data_in_aligned[:,:,0]
    getshape = data_in_aligned.shape
    output_allimg_registered = np.zeros((getshape[0],getshape[1],getshape[2]), dtype=np.float64)
    output_allimg_registered[:,:,0] = refimg
    
    self.statusBar().showMessage('Registration is in progress. Please do not close your window!')
    self.progress.setMaximum(getshape[2]-1)
    self.progress.setValue(0)
    self.progress.setVisible(True)
    QApplication.processEvents()
    
    saveRescaledImg(refimg,path.join(self.folder,'img0registered.png'))      


    for image_counter in range(1,getshape[2]):
        deformed_img = IRT_registration(np.ascontiguousarray(data_in_aligned[:,:,image_counter], dtype=np.float64),np.ascontiguousarray(dataref_aligned[:,:,image_counter], dtype=np.float64))
        def_img_array = np.asarray(deformed_img)
        def_img = def_img_array[0,:,:]
        output_allimg_registered[:,:,image_counter] = def_img
        imvis = overlap_images(refimg,def_img)
        fn = path.join(self.folder,'img' + str(image_counter) + 'registered.png')
        imvis.save(fn)
        
        self.listWidget2.item(image_counter).setIcon(QIcon(fn))
        self.listWidget2.item(image_counter).setText(path.splitext(self.filenames[image_counter])[0])     
        self.progress.setValue(image_counter)
        QApplication.processEvents()
    
    sleep(1)         
    self.statusBar().showMessage('Finished registering')
    self.progress.setVisible(False)
    
    return output_allimg_registered

def Run_registration_withProgressbar(self):#,data_in_aligned,dataref
    
    output_registered = Registration_progressbar(self)#,data_in_aligned,dataref
   
    return output_registered

def show_registered_images(self):

    self.frame_button_registration.setVisible(True)
    self.frame_edit.setVisible(False)
    self.data_registered = Run_registration_withProgressbar(self)
    self.stack2.setLabel("Single subject: Image registration")    
    self.frame_register.setVisible(False) 
    self.frame_button_registration.setVisible(False)
    self.frame_ROI.setVisible(True) 
        