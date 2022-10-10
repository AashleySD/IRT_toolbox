"""
Authors: Aashley Sardjoe Mishre [1] and Oleh Dzyubachyk [2]
Affiliations: 1. Leiden university medical center, Radiology department, 2. Leiden university medical center, Division of Image Processing (LKEB)
Date: 15-06-2021
Last updated:27-10-2021
    
Title script: Single participant module 
Purpose: This function displays the user interface of the single participant module,
wherein the user can: upload images from a subject's dataset, run the image alignment code,
register the postbaseline images to the referenc image and semi-automically segment the ROIs 

"""

from ReadData_SingleParticipant_functions import show_img_upload, button_img_readin
from AlignData_SingleParticipant_functions import show_aligned_images
from os import path, mkdir, unlink, listdir
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import QSize
from common_functions import QDoubleStack


def Single_participant(self):
    
    #create temporary storage folder
    temp_path = self.folder 
    if (path.isdir(temp_path)  == 0):
        mkdir(temp_path)
    
    if (path.isdir(temp_path)  == 1):
        allcontent = listdir(temp_path)
        for f in range(len(allcontent)):
            unlink(path.join(temp_path,allcontent[f]))
    
    
    self.button_multipar_registration.setVisible(False)
    self.button_multipar_segmentation.setVisible(False)
    self.page_switch.setCurrentIndex(1)
    
    self.upload_img_userinput.setValue(2)
    for ii in range(self.listWidget.count()):
        self.listWidget.item(ii).setIcon(QIcon("Images/capture_res.png"))
    for ii in range(self.listWidget.count()):
        self.listWidget.item(ii).setText("")
        
def createStack2(self):

    stack = QDoubleStack()
    stack.setLabel("Single subject :: Upload images (.tiff, .png, .jpg)")
   
    sleft_frame_layout = stack.leftFrameLayout()
    sright_frame_layout = stack.rightFrameLayout()
    
    lbl = QLabel("Enter number images for upload")
    lbl.setStyleSheet("QLabel { background-color : #171719; color : white}")
    lbl.setFont(self.helv12)
        
    sleft_frame_layout.addSpacing(50)
    sleft_frame_layout.addWidget(lbl)  
    sleft_frame_layout.addSpacing(5)    
    
    spinbox_layout = QHBoxLayout()
    self.upload_img_userinput = QSpinBox()
    self.upload_img_userinput.setFixedSize(256,32)
    self.upload_img_userinput.setMinimum(2)
    self.upload_img_userinput.setMaximum(8)
    self.upload_img_userinput.setFont(self.helv12) 
    self.upload_img_userinput.setStyleSheet("QSpinBox { background-color : white; color: black }")
    self.upload_img_userinput.valueChanged.connect(lambda:show_img_upload(self))
    spinbox_layout.addWidget(self.upload_img_userinput) 
    button_upload_info = QPushButton("?")
    button_upload_info.setFont(self.helv16)    
    button_upload_info.setStyleSheet("QPushButton { background-color : darkgrey; color: white }")
    button_upload_info.setFixedSize(32,32)
    button_upload_info.setToolTip('<img src="%s"> ' % ("Images/uploadinfo.png"))
    button_upload_info.setEnabled(False)
    
    spinbox_layout.addWidget(button_upload_info) 
    spinbox_layout.addStretch()    
    sleft_frame_layout.addLayout(spinbox_layout) 
    sleft_frame_layout.addSpacing(20)
    
    button_layout = QHBoxLayout()
    self.button_alignimg = QPushButton("Next: Align Images")
    self.button_alignimg.setFixedSize(256,60)
    self.button_alignimg.setFont(self.helv12)
    self.button_alignimg.setStyleSheet("QPushButton { background-color : #621940; color : white}")
    self.button_alignimg.setEnabled(False)
    self.button_alignimg.clicked.connect(lambda:show_aligned_images(self,25))
    button_layout.addWidget(self.button_alignimg) 
    button_alignimg_info = QPushButton("?")
    button_alignimg_info.setFont(self.helv16)
    button_alignimg_info.setStyleSheet("QPushButton { background-color : darkgrey; color: white }")
    button_alignimg_info.setFixedSize(32,32)
    button_alignimg_info.setToolTip('<img src="%s"> ' % ("Images/alignmentinfo_1.png"))
    button_alignimg_info.setEnabled(False)
    button_layout.addWidget(button_alignimg_info) 
    button_layout.addStretch()    
    sleft_frame_layout.addLayout(button_layout) 
    sleft_frame_layout.addStretch() 
    
    self.listWidget = QListWidget()
    self.listWidget.setObjectName("listView")
    self.listWidget.setViewMode(QListWidget.IconMode)
    self.listWidget.setFont(self.helv12)
    self.listWidget.setStyleSheet("QListWidget { background-color : #0c0c0b; border: none; color: #fc9c39 }")
    self.listWidget.setIconSize(QSize(480,640))
    self.listWidget.setSelectionMode(0)
    self.listWidget.doubleClicked.connect(lambda:button_img_readin(self))
    sright_frame_layout.addWidget(self.listWidget)  
    
    show_img_upload(self)
    
        
    return stack    