"""
Authors: Aashley Sardjoe Mishre [1] and Oleh Dzyubachyk [2]
Affiliations: 1. Leiden university medical center, Radiology department, 2. Leiden university medical center, Division of Image Processing (LKEB)
Date: 15-06-2021
Last updated:14-01-2022

Title script: ROIModule_SingleParticipant_functions
Purpose: This script includes all subfunctions for semi-automated ROI segmentation of a single dataset of one participant. 
This script is used in the single participant analysis

"""

from os import path, listdir, unlink, getcwd, mkdir
import numpy as np
import math
import pandas as pd
from RegisterData_MultipleParticipants_functions import multi_registration_mainscreen
from manualROIsegmentation import ROI_manual_main
from Single_Participant_module import * #Single_participant
from image_overlap import *
from datetime import datetime

from PyQt5.QtWidgets import * 
from PyQt5.QtGui import * 
from PyQt5.QtCore import Qt, QSize
from common_functions import saveRescaledImg, QDoubleStack, QDrawableLabel



def clear_ROI_single(self):

    ROI_module_single(self)
    
    self.draw_ROI_widget_single.update()
    self.draw_ROI_widget_single.storeRow_coordinates = []
    self.draw_ROI_widget_single.storeCol_coordinates = []

def ROI_module_single(self):

    self.page_switch.setCurrentIndex(6)
    refimg = self.data_registered[:,:,0]
    self.draw_ROI_widget_single.setImage(saveRescaledImg(refimg))
    self.frame_quantify_ROI_widget.clear()
    self.draw_ROI_lbl_sinlge.setText(path.splitext(self.filenames[0])[0])
    
def show_ROI_registered_dataset(self):

    self.page_switch.setCurrentIndex(7)

    if path.isdir(self.folder):
        allcontent = listdir(self.folder)
        for f in range(len(allcontent)):
            unlink(path.join(self.folder,allcontent[f]))

    if len(self.draw_ROI_widget_single.storeCol_coordinates) > 1:
        image_ref = self.data_registered[:,:,0]
     
        Mask = self.draw_ROI_widget_single.getROImask(image_ref.shape)   
        No_images = np.shape(self.data_registered)[2]
        self.tempvals = []
        self.tempmean = np.zeros(No_images)
        self.tempmax = np.zeros(No_images)
        self.tempmin = np.zeros(No_images)
        
        
        for h in range(No_images):
            image_reg_temp = self.data_registered[:,:,h]
            idx = np.where(image_reg_temp == 0)
            image_reg_temp[idx] = np.min(image_reg_temp[np.nonzero(image_reg_temp)])
            fn = path.join(self.folder,str(h) + "masked_reg.png")
            imROI = saveRescaledImg(image_reg_temp,fn,Mask)
            
            data = Mask * self.data_registered[:,:,h] 
            data_list = []
            [x for rows in range(data.shape[0]) for cols in range(data.shape[1]) if ((data[rows,cols] > 0) and data_list.append(data[rows,cols]))]

            vals = np.array(data_list) 
            self.tempvals.append(vals)
            self.tempmean[h] = np.mean(vals)
            self.tempmax[h] = np.amax(vals)
            self.tempmin[h] = np.amin(vals)
            self.ROI_pix = len(vals)
        
        answer_user = No_images
            

        images = []
     
        for img_list in range(int(No_images)):
            
            fn = path.join(self.folder, str(img_list) + "masked_reg.png")  
            
            draw_ROI = QDrawableLabel(lWidth=self.imWidth,lHeight=self.imHeight)
            images.append(draw_ROI)
            draw_ROI.setImage(QImage(fn))
            draw_ROI.setfilename(path.splitext(self.filenames[img_list])[0])

            draw_ROI.setMeanT(self.tempmean[img_list])
            draw_ROI.setMaxT(self.tempmax[img_list])
            
            fname = path.join(self.folder,'masked_ROI_' + str(img_list) + '.png')
            draw_ROI.saveToFile(fname)
            
            item = QListWidgetItem(QIcon(fname),'')
            item.setToolTip('')
            self.frame_quantify_ROI_widget.addItem(item)
            
        self.frame_quantify_ROI_widget.setVisible(True)    
        self.frame_quantify_ROI_widget.update()

 #####################################################################################    
 
def SaveDataExcel(self):
    
    dialog = QFileDialog()
    filename_user, _filter = dialog.getSaveFileName(None,"Save as Excel table...",getcwd(),"Excel file (*.xlsx)")
 
    #export data to excel  -summary data
    if filename_user:
    
        Keyslist,values = [],[]
        Keyslist.append("Parameters")
        values.append(["Mean Temperature", "Max Temperature","Min Temperature","Pixels in ROI"])
        for h in range (len(self.filenames)):
            Keyslist.append(path.splitext(self.filenames[h])[0]) 
            values.append([(self.tempmean[h]), (self.tempmax[h]), (self.tempmin[h]), (self.ROI_pix)]) 
                
        list_intv_outcomes = dict(zip(Keyslist, values))                    
        datasum = pd.DataFrame(list_intv_outcomes)
        fn_store_sum = str.replace(filename_user,".xlsx","_summary.xlsx")
        writer_sum = pd.ExcelWriter(fn_store_sum, engine='xlsxwriter')
        datasum.to_excel(writer_sum, sheet_name='Temperature data')
        writer_sum.save()
        #export data to excel  -raw data
        
        Keyslist,values = [],[]
        for h in range(len(self.filenames)):
                  Keyslist.append(path.splitext(self.filenames[h])[0]) 
                  values.append(self.tempvals[h]) 
                
        list_intv_outcomes_raw = dict(zip(Keyslist, values))                    
        data = pd.DataFrame(list_intv_outcomes_raw)
        fn_store_raw = str.replace(filename_user,".xlsx","_raw.xlsx")
        writer_raw = pd.ExcelWriter(fn_store_raw, engine='xlsxwriter')
        data.to_excel(writer_raw, sheet_name='Raw temperature data')
        writer_raw.save()  
        showsavecompletedmssg(self)
     
  
def SaveRegData(self):

    dialog = QFileDialog()
    dialog.setOption(QFileDialog.ShowDirsOnly, True) 
    dialog.FileMode(QFileDialog.Directory)
    filename_user_py = dialog.getExistingDirectory(None,"Select directory")
    
    if filename_user_py:
       
        date_time = datetime.now().strftime('%Y-%m-%d_%H-%M')
        directory = "RegisteredData_"  + date_time
        pathstore = path.join(filename_user_py, directory)  
        if not path.exists(pathstore):
            mkdir(pathstore)
            
        refimg = self.data_registered[:,:,0]#[0]#
        fname = "ID0_" + path.splitext(self.filenames[0])[0]
        fname = "ID0_reference_img_" + path.splitext(self.filenames[0])[0].replace('Reference image: ','')
        np.save(path.join(pathstore,fname),refimg)
        
        for kk in range(1,len(self.filenames)):
            fname = path.splitext(self.filenames[kk])[0]

            fname = 'ID' + str(kk) + '_' + path.splitext(self.filenames[kk])[0] + "_registered"
            np.save(path.join(pathstore,fname),self.data_registered[:,:,kk])

            imvis = overlap_images(refimg,self.data_registered[:,:,kk])
            pathstore_overlap = path.join(pathstore, fname +".png")  
            imvis.save(pathstore_overlap,'png')
            
        showsavecompletedmssg(self)
    
def showsavecompletedmssg(self):

    self.statusBar().showMessage('Finished exporting!')

def createStack7(self):
 
    stack = QDoubleStack()
    stack.setLabel("Single subject :: Draw reference ROI (click directly on the image)")
   
    sleft_frame_layout = stack.leftFrameLayout()
    sright_frame_layout = stack.rightFrameLayout()
    
    sleft_frame_layout.addSpacing(50)    
    
    self.frame_draw_ROI = QWidget()    
    button_layout = QVBoxLayout()
    button = QPushButton("Clear ROI")
    button.setFixedSize(256,60)
    button.setFont(self.helv12)
    button.setStyleSheet("QPushButton { background-color : #621940; color : white}")
    button.clicked.connect(lambda:clear_ROI_single(self))
    button_layout.addWidget(button) 
    button_layout.addSpacing(20) 
    
    button = QPushButton("Finished!")
    button.setFixedSize(256,60)
    button.setFont(self.helv12)
    button.setStyleSheet("QPushButton { background-color : #e9765b; color : white}")
    button.clicked.connect(lambda:show_ROI_registered_dataset(self))
    button_layout.addWidget(button) 
    
    self.frame_draw_ROI.setLayout(button_layout)
    sleft_frame_layout.addWidget(self.frame_draw_ROI)
    sleft_frame_layout.addStretch() 
    
    self.draw_ROI_lbl_sinlge = QLabel('')
    self.draw_ROI_lbl_sinlge.setStyleSheet("QLabel { background-color : #0c0c0b; color : #fc9c39}")
    self.draw_ROI_lbl_sinlge.setFont(self.helv16)    
    
    sright_frame_layout.addSpacing(20)
    sright_frame_layout.addWidget(self.draw_ROI_lbl_sinlge)  
    
    self.draw_ROI_widget_single = QDrawableLabel(lWidth=self.imWidth,lHeight=self.imHeight)
    sright_frame_layout.addSpacing(5)
    sright_frame_layout.addWidget(self.draw_ROI_widget_single) 
    
    sright_frame_layout.addStretch()
  
    return stack
    
def createStack8(self):
 
    stack = QDoubleStack()
    stack.setLabel("Single subject :: Semi-automated ROI extraction")
   
    sleft_frame_layout = stack.leftFrameLayout()
    sright_frame_layout = stack.rightFrameLayout()  
    sleft_frame_layout.addSpacing(50)    
    
    button_layout = QVBoxLayout()
    button = QPushButton("Save Temperature Data")
    button.setFixedSize(256,60)
    button.setFont(self.helv12)
    button.setStyleSheet("QPushButton { background-color : #621940; color : white}")
    button.clicked.connect(lambda:SaveDataExcel(self))
    button_layout.addWidget(button) 
    button_layout.addSpacing(10) 
    button = QPushButton("Save Registered Images")
    button.setFixedSize(256,60)
    button.setFont(self.helv12)
    button.setStyleSheet("QPushButton { background-color : #621940; color : white}")
    button.clicked.connect(lambda:SaveRegData(self))
    button_layout.addWidget(button) 
    button_layout.addSpacing(50) 
    
    button = QPushButton("Draw Another ROI")
    button.setFixedSize(256,60)
    button.setFont(self.helv12)
    button.setStyleSheet("QPushButton { background-color : #e9765b; color : white}")
    button.clicked.connect(lambda:clear_ROI_single(self))
    button_layout.addWidget(button) 
    button_layout.addSpacing(10) 
    button = QPushButton("Home")
    button.setFixedSize(256,60)
    button.setFont(self.helv12)
    button.setStyleSheet("QPushButton { background-color : #fd8f52; color : white}")
    button.clicked.connect(lambda:self.home_return())
    button_layout.addWidget(button) 
    button_layout.addSpacing(10) 
    
    self.frame_quantify_ROI = QWidget()    
    self.frame_quantify_ROI.setLayout(button_layout)
    sleft_frame_layout.addWidget(self.frame_quantify_ROI)
    sleft_frame_layout.addStretch() 
    
    self.frame_quantify_ROI_widget = QListWidget()
    self.frame_quantify_ROI_widget.setViewMode(QListWidget.IconMode)
    self.frame_quantify_ROI_widget.setFont(self.helv12)
    self.frame_quantify_ROI_widget.setStyleSheet("QListWidget { background-color : #0c0c0b; border: none; color: #fc9c39 }")
    self.frame_quantify_ROI_widget.setIconSize(QSize(self.imHeight+50,self.imWidth))
    self.frame_quantify_ROI_widget.setSelectionMode(0)
    self.frame_quantify_ROI_widget.setVisible(False)
    sright_frame_layout.addWidget(self.frame_quantify_ROI_widget)  
  
    return stack
    