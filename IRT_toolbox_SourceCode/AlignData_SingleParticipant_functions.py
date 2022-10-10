"""
Authors: Aashley Sardjoe Mishre [1] and Oleh Dzyubachyk [2]
Affiliations: 1. Leiden university medical center, Radiology department, 2. Leiden university medical center, Division of Image Processing (LKEB)
Date: 03-08-2021
Last updated: 27-12-2021
    
Title script: AlignData_SingleParticipant_functions
Purpose: This script includes all subfunctions for aligning a single dataset of one participant.

"""

from os import path, mkdir
import numpy as np
from image_overlap import overlap_images
from time import sleep
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import QApplication

from RegisterData_SingleParticipant_functions import show_registered_images#, ROI_module_single
from ROIModule_SingleParticipant_functions import ROI_module_single
from common_functions import saveRescaledImg, QDoubleStack, align_images
    
def Alignment_IRT(self,background_thres):
    refimg = np.load(path.join(self.folder,'refimg.npy'))
    getshape = refimg.shape
    nn = len(self.data_readin)
    output_allimg_aligned = np.zeros((getshape[0],getshape[1],nn), dtype=np.float64)
    output_allimg_ref = np.zeros((getshape[0],getshape[1],nn), dtype=np.float64)

    output_allimg_aligned[:,:,0] = refimg
    output_allimg_ref[:,:,0] = refimg

    saveRescaledImg(refimg,path.join(self.folder,'img0aligned.png'),None,2)
    
    for image_counter in range(nn-1):    
        fixed, im_aligned, redflag = align_images(np.load(path.join(self.folder,'refimg.npy')),self.data_readin[image_counter+1],background_thres)
        if redflag == 0:
            output_allimg_aligned[:,:,image_counter+1] = im_aligned
            output_allimg_ref[:,:,image_counter+1] = fixed
            imvis = overlap_images(fixed,im_aligned)
            fn_imvis = path.join(self.folder, "img"+ str(image_counter+1) + "aligned.png")
            imvis.save(fn_imvis)
            self.progress.setValue(image_counter+1)
            QApplication.processEvents()
        else:
            mssg_window = QMessageBox()
            mssg_window.setIcon(QMessageBox.Critical)
            mssg_window.setText("     The selected room temperature of the image was too high or too low!\n Please adjust the room temperature        ")
            mssg_window.setWindowTitle("Image alignment error ")
            mssg_window.setStandardButtons(QMessageBox.Ok)
            mssg_window.exec_()
            break
        
    return output_allimg_aligned, output_allimg_ref, redflag
    
    
def Image_alignment_withprogressbar(self,background_thres):
    output_allimg_aligned, outputallimgref, redflag = Alignment_IRT(self,background_thres)    
    return output_allimg_aligned, outputallimgref, redflag


def ReAlignSingleImage(self):
    self.frame_button_registration.setVisible(False)
    self.spinboxTh.setValue(self.alignThresh[self.listWidget2.currentRow()])
    if self.listWidget2.currentRow() > 0:
        self.frame_edit.setVisible(True)
    else:
        self.frame_button_registration.setVisible(True)
    
def DifferentBackgroundThres_mssg():
    warningROI = QMessageBox()
    warningROI.setIcon(QMessageBox.Warning)
    warningROI.setText("Please change the background temperature!     ")
    warningROI.setWindowTitle("background temperature")
    warningROI.setStandardButtons(QMessageBox.Ok)
    warningROI.exec_()
    
def realign_single_image_newBackground(self):
    self.progress.setMaximum(1)
    self.progress.setValue(0)
    self.progress.setVisible(True)
    QApplication.processEvents()
    self.alignThresh[self.listWidget2.currentRow()] = self.spinboxTh.value()
    
    cr = self.listWidget2.currentRow()
    pos = path.join(self.folder,"img" + str(cr))
    fixed, im_aligned, redflag = align_images(np.load(path.join(self.folder,'refimg.npy')),self.data_readin[self.listWidget2.currentRow()],self.spinboxTh.value())
    if redflag == 0:
        imvis = overlap_images(fixed,im_aligned)
        fn_imvis = pos + 'newaligned.png'
        imvis.save(fn_imvis)
        fn_npy = pos + 'newaligned.npy'
        fn_newref_npy = pos + 'newrefaligned.npy'
        np.save(fn_npy,im_aligned)
        np.save(fn_newref_npy,fixed)
        
        self.data_aligned[:,:,cr] = im_aligned
        self.data_ref[:,:,cr] = fixed
            
        self.progress.setValue(1)
        QApplication.processEvents()
        
        self.listWidget2.currentItem().setIcon(QIcon(fn_imvis))
        self.listWidget2.currentItem().setText(path.splitext(self.filenames[self.listWidget2.currentRow()])[0])
     
    else:
        DifferentBackgroundThres_mssg()
      
    sleep(1)
    self.progress.setVisible(False)
    self.frame_edit.setVisible(False)
    self.frame_button_registration.setVisible(True)

    
def show_aligned_images(self,background_thres):
    
    answer_user = len(self.data_readin)
    self.progress.setMaximum(len(self.data_readin)-1)
    self.progress.setValue(0)
    self.progress.setVisible(True)
    
    if len(self.filenames) > 1:
        self.data_aligned, self.data_ref, redflag = Image_alignment_withprogressbar(self,background_thres)
        
        if redflag == 0:
            self.listWidget2.clear()
            for img_list in range(int(answer_user)):
                fn = path.join(self.folder,"img"+ str(img_list) + "aligned.png") 
                item = QListWidgetItem(QIcon(fn),path.splitext(self.filenames[img_list])[0])
                item.setToolTip('')
                self.listWidget2.addItem(item)

            self.frame_register.setVisible(True)
            #self.frame_edit.setVisible(True)
            self.frame_ROI.setVisible(False)   
            self.page_switch.setCurrentIndex(5)
    
    sleep(1)    
    self.progress.setVisible(False)
        
def createStack6(self):
 
    stack = QDoubleStack()
    stack.setLabel("Single subject :: Image alignment")
    
    sleft_frame_layout = stack.leftFrameLayout()
    sright_frame_layout = stack.rightFrameLayout()
    sleft_frame_layout.addSpacing(50) 
    
    self.frame_button_registration = QWidget()
    button_layout1 = QHBoxLayout()
    button_layout1.setContentsMargins(0,0,0,0)      
    self.button_realign = QPushButton("Re-Align Image")
    self.button_realign.setFixedSize(256,60)
    self.button_realign.setFont(self.helv12)
    self.button_realign.setStyleSheet("QPushButton { background-color : #333333; color : white}")
    self.button_realign.clicked.connect(lambda:ReAlignSingleImage(self))
    self.button_realign.setEnabled(False)
    #button_realign.setToolTip("blabla")
    button_layout1.addWidget(self.button_realign) 
    button_realigninfo = QPushButton("?")
    button_realigninfo.setFont(self.helv16)
    button_realigninfo.setStyleSheet("QPushButton { background-color : darkgrey; color: white }")
    button_realigninfo.setFixedSize(32,32)
    button_realigninfo.setToolTip("Select a post-baseline image and Re-align")
    button_realigninfo.setEnabled(False)
    button_layout1.addWidget(button_realigninfo) 
    button_layout1.addStretch() 
    self.frame_button_registration.setLayout(button_layout1)
    self.frame_button_registration.setVisible(True)
    sleft_frame_layout.addWidget(self.frame_button_registration) 

    self.frame_edit = QWidget()

    button_layout = QVBoxLayout()
    button_layout.setContentsMargins(0,0,0,0) 
    #button_layout.addSpacing(50)
    button_layout1 = QHBoxLayout()   
    button_layout1.setContentsMargins(0,0,0,0)  
    lbl = QLabel("Enter background threshold " + "\u00b0" + "C")
    lbl.setStyleSheet("QLabel { background-color : #171719; color : white}")
    lbl.setFont(self.helv12)
    button_layout.addWidget(lbl)  
    button_layout.addSpacing(5)    
    self.spinboxTh = QSpinBox()
    self.spinboxTh.setFixedSize(256,32)
    self.spinboxTh.setMinimum(1)
    self.spinboxTh.setMaximum(255)
    self.spinboxTh.setFont(self.helv12) 
    self.spinboxTh.setValue(25)
    self.spinboxTh.setStyleSheet("QSpinBox { background-color : white; color: black }")
    button_layout.addWidget(self.spinboxTh)
    button_layout.addSpacing(20)
    button_change_bTh = QPushButton("Align again")
    button_change_bTh.setFixedSize(256,60)
    button_change_bTh.setFont(self.helv12)
    button_change_bTh.setStyleSheet("QPushButton { background-color : #333333; color : white}")
    button_change_bTh.clicked.connect(lambda:realign_single_image_newBackground(self))
    button_layout1.addWidget(button_change_bTh) 
    button_infoAlign = QPushButton("?")
    button_infoAlign.setFont(self.helv16)
    button_infoAlign.setStyleSheet("QPushButton { background-color : darkgrey; color: white }")
    button_infoAlign.setFixedSize(32,32)
    button_infoAlign.setToolTip('<img src="%s"> ' % ("Images/alignmentinfo_2.png"))
    button_infoAlign.setEnabled(False)
    button_layout1.addWidget(button_infoAlign) 
    button_layout1.addStretch()       
    self.frame_edit.setVisible(False)
    self.frame_edit.setLayout(button_layout)
    button_layout.addLayout(button_layout1)
    sleft_frame_layout.addWidget(self.frame_edit)     
        
    sleft_frame_layout.addSpacing(20)

    self.frame_register = QWidget()
    button_layout = QHBoxLayout()
    button_layout.setContentsMargins(0,0,0,0)  
    button_registration = QPushButton("Next: Register Images")
    button_registration.setFixedSize(256,60)
    button_registration.setFont(self.helv12)
    button_registration.setStyleSheet("QPushButton { background-color : #621940; color : white}")
    button_registration.clicked.connect(lambda:show_registered_images(self))
    button_layout.addWidget(button_registration) 
    button_reginfo = QPushButton("?")
    button_reginfo.setFont(self.helv16)
    button_reginfo.setStyleSheet("QPushButton { background-color : darkgrey; color: white }")
    button_reginfo.setFixedSize(32,32)
    button_reginfo.setToolTip('<img src="%s"> ' % ("Images/registrationinfo.png"))
    button_reginfo.setEnabled(False)
    button_layout.addWidget(button_reginfo) 
    button_layout.addStretch()    
    self.frame_register.setLayout(button_layout) 
    sleft_frame_layout.addWidget(self.frame_register) 
    
    self.frame_ROI = QWidget()
    button_layout = QHBoxLayout()
    button_layout.setContentsMargins(0,0,0,0)  
    button_ROI = QPushButton("Next: Draw ROIs")
    button_ROI.setFixedSize(256,60)
    button_ROI.setFont(self.helv12)
    button_ROI.setStyleSheet("QPushButton { background-color : #333333; color : white}")
    button_ROI.clicked.connect(lambda:ROI_module_single(self))
    button_layout.addWidget(button_ROI) 
    button_ROIinfo = QPushButton("?")
    button_ROIinfo.setFont(self.helv16)
    button_ROIinfo.setStyleSheet("QPushButton { background-color : darkgrey; color: white }")
    button_ROIinfo.setFixedSize(32,32)
    button_ROIinfo.setToolTip('<img src="%s"> ' % ("Images/ROI_info.png"))
    button_ROIinfo.setEnabled(False)
    button_layout.addWidget(button_ROIinfo) 
    button_layout.addStretch()
    self.frame_ROI.setLayout(button_layout) 
    self.frame_ROI.setVisible(False)    
    sleft_frame_layout.addWidget(self.frame_ROI) 
    

    sleft_frame_layout.addStretch() 

    self.listWidget2 = QListWidget()
    self.listWidget2.setObjectName("listView")
    self.listWidget2.setViewMode(QListWidget.IconMode)
    self.listWidget2.setFont(self.helv12)
    self.listWidget2.setStyleSheet("QListWidget { background-color : #0c0c0b; border: none; color: #fc9c39 }")
    self.listWidget2.setIconSize(QSize(480,640))
    self.listWidget2.setSelectionMode(0)
    self.listWidget2.currentItemChanged.connect(lambda:itemChanged(self))
    sright_frame_layout.addWidget(self.listWidget2)  
    
    return stack
    
def itemChanged(self):
    if self.frame_register.isVisible():
        self.frame_button_registration.setVisible(True)
        self.frame_edit.setVisible(False)
    self.button_realign.setEnabled(self.listWidget2.currentRow() > 0)
