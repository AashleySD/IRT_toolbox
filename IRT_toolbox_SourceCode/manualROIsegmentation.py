"""
Authors: Aashley Sardjoe Mishre [1] and Oleh Dzyubachyk [2]
Affiliations: 1. Leiden university medical center, Radiology department, 2. Leiden university medical center, Division of Image Processing (LKEB)
Date: 15-06-2021
Last updated:27-12-2021
    
Title script: manualROIsegmentation
Purpose: This script includes all functions for manual ROI drawing
   
"""

from os import path, getcwd, listdir, unlink, getcwd
import numpy as np
import flirimageextractor
from matplotlib import cm
import pandas as pd
from datetime import datetime


from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from common_functions import saveRescaledImg, QDoubleStack, QDrawableLabel


def readin_temp():    
    dialog = QFileDialog()
    dialog.FileMode(QFileDialog.ExistingFile)
    filepathjpg, _filter = dialog.getOpenFileName(None,"Select image file",getcwd(),"Image (*.png *.jpeg *.jpg *.tiff)")
    if filepathjpg != "":
        flir = flirimageextractor.FlirImageExtractor(palettes=[cm.jet, cm.bwr, cm.gist_ncar])
        flir.process_image(filepathjpg)
        converted_temperature_image = flir.get_thermal_np()
    else:
        converted_temperature_image = []

    return converted_temperature_image,filepathjpg

def uploadrefimg(self):

    TemperatureMap,image_path = readin_temp()
    if TemperatureMap != []:
        filename_withextension = path.basename(image_path)
       
        self.imagetemp_name = path.splitext(filename_withextension)[0]
        self.imagetemp = TemperatureMap
        self.draw_ROI_lbl_manual.setText(self.imagetemp_name)
        
        self.button_clearROI_manual.setEnabled(self.imagetemp.size > 0)
        self.button_drawROI_manual.setEnabled(self.imagetemp.size > 0)
        self.button_regfolder.setEnabled(self.imagetemp.size > 0)
        self.draw_ROI_widget_manual.setClickable(self.imagetemp.size > 0)
        
        self.draw_ROI_widget_manual.clear()
        self.draw_ROI_widget_manual.setImage(saveRescaledImg(self.imagetemp))
            
def ROI_module_clear(self):
    self.draw_ROI_widget_manual.clear()
   
def drawROIwarningmssg():

    warningROI = QMessageBox()
    warningROI.setIcon(QMessageBox.Warning)
    warningROI.setText("Please draw an ROI first!     ")
    warningROI.setWindowTitle("Draw ROI")
    warningROI.setStandardButtons(QMessageBox.Ok)
    warningROI.exec_()
    
def temperaturevalue_singleimg(self):

    sC_coordinates = self.draw_ROI_widget_manual.storeCol_coordinates
    sR_coordinates = self.draw_ROI_widget_manual.storeRow_coordinates
    if len(sC_coordinates) > 0:
        
        dialog = QFileDialog()
        file, _filter = dialog.getSaveFileName(None,"Save as Excel table...",getcwd(),"Excel file (*.xlsx)")

        if file != '':
            df = pd.DataFrame((sC_coordinates,sR_coordinates))
            df.to_excel(excel_writer = file)
            
            filename_user = path.splitext(file)[0]
            Mask = self.draw_ROI_widget_manual.getROImask(self.imagetemp.shape)
            date_time = datetime.now().strftime('%Y-%m-%d_%H-%M')
            tempmean = []
            tempmax = []
            tempmin = []
            
            data = Mask * self.imagetemp
            data_list = []
            [x for rows in range(data.shape[0]) for cols in range(data.shape[1]) if ((data[rows,cols] > 0) and data_list.append(data[rows,cols]))]
   
            vals = np.array(data_list)            
            tempmean = np.mean(vals)
            tempmax = np.amax(vals)
            tempmin = np.amin(vals)
            ROI_pix = len(vals)
         
            #export data to excel  -summary data
            Keyslist,values = [],[]
            Keyslist.append("Parameters")
            values.append(["Mean Temperature", "Max Temperature","Min Temperature","Pixels in ROI"])
            Keyslist.append(self.imagetemp_name) 
            values.append([(tempmean), (tempmax), (tempmin), (ROI_pix)]) 
                    
            list_intv_outcomes = dict(zip(Keyslist, values))                    
            datasum = pd.DataFrame(list_intv_outcomes)
            fn_store_sum = filename_user + "_summary.xlsx" 
            writer_sum = pd.ExcelWriter(fn_store_sum, engine='xlsxwriter')
            datasum.to_excel(writer_sum, sheet_name='Temperature data', index=False)
            writer_sum.save()
            #export data to excel  -raw data
            Keyslist,values = [],[]
            Keyslist.append(self.imagetemp_name) 
            values.append(vals) 
                    
            list_intv_outcomes_raw = dict(zip(Keyslist, values))                    
            data = pd.DataFrame(list_intv_outcomes_raw)
            fn_store_raw = filename_user + "_raw.xlsx" 
            writer_raw = pd.ExcelWriter(fn_store_raw, engine='xlsxwriter')
            data.to_excel(writer_raw, sheet_name='Raw temperature data', index=False)
            writer_raw.save()   
            showsavecompletedmssg(self,Mask)
            
            self.button_drawROI_manual.setEnabled(False)
            self.button_drawROI_manual.setChecked(False)
            self.draw_ROI_widget_manual.setClickable(False)
    else:
        drawROIwarningmssg()

def showsavecompletedmssg(self,Mask):

    self.statusBar().showMessage('Finished exporting!')
    showMaskonImage(self,Mask)
    
def showMaskonImage(self,mask):
    if path.isdir(self.folder):
        allcontent = listdir(self.folder)
        for f in range(len(allcontent)):
            unlink(path.join(self.folder,allcontent[f]))

    fntempsave = path.join(self.folder, "singleImageMask.png")
    saveRescaledImg(self.imagetemp,fntempsave,mask);

    data = mask * self.imagetemp
    data_list = []
    data_list = []
    [x for rows in range(data.shape[0]) for cols in range(data.shape[1]) if ((data[rows,cols] > 0) and data_list.append(data[rows,cols]))]
   
    vals = np.array(data_list)            
    tempmean = np.mean(vals)
    tempmax = np.amax(vals)
       
    self.draw_ROI_widget_manual.setImage(QImage(fntempsave))
    self.draw_ROI_widget_manual.setMeanT(tempmean)
    self.draw_ROI_widget_manual.setMaxT(tempmax)
    
def ROI_manual_main(self):
    
    self.button_multipar_registration.setVisible(False)
    self.button_multipar_segmentation.setVisible(False)
    self.draw_ROI_widget_manual.setImage(None)
    self.draw_ROI_widget_manual.clear()
    self.draw_ROI_lbl_manual.setText('')
    self.draw_ROI_widget_manual.setClickable(False)
    self.button_drawROI_manual.setChecked(True)
    self.button_regfolder.setEnabled(False)
    self.page_switch.setCurrentIndex(4)
    
def ROI_module_manual(self):
    self.draw_ROI_widget_manual.setClickable(self.button_drawROI_manual.isChecked())

def createStack5(self):

    stack = QDoubleStack()
    stack.setLabel("Single image :: Manual ROI delineation")
    
    sleft_frame_layout = stack.leftFrameLayout()
    sright_frame_layout = stack.rightFrameLayout()

    sleft_frame_layout.addSpacing(50)    
    
    button_layout = QHBoxLayout()
    button = QPushButton("1. Upload Image")
    button.setFixedSize(256,60)
    button.setFont(self.helv12)
    button.setStyleSheet("QPushButton { background-color : #621940; color : white}")
    button.clicked.connect(lambda:uploadrefimg(self))
    button_layout.addWidget(button) 
    button_uploadinfo = QPushButton("?")
    button_uploadinfo.setFont(self.helv16)
    button_uploadinfo.setStyleSheet("QPushButton { background-color : darkgrey; color: white }")
    button_uploadinfo.setFixedSize(32,32)
    button_uploadinfo.setToolTip('<img src="%s"> ' % ("Images/uploadinfo_manual.png"))
    button_uploadinfo.setEnabled(False)
    button_layout.addWidget(button_uploadinfo) 
    button_layout.addStretch()    
    sleft_frame_layout.addLayout(button_layout) 
    sleft_frame_layout.addSpacing(20) 
    
    
    button_layout = QHBoxLayout()
    self.button_drawROI_manual = QPushButton("2. Draw ROI")
    self.button_drawROI_manual.setFixedSize(124,60)
    self.button_drawROI_manual.setFont(self.helv12)
    self.button_drawROI_manual.setStyleSheet("QPushButton { background-color : #e9765b; color : white}")
    self.button_drawROI_manual.clicked.connect(lambda:ROI_module_manual(self))
    self.button_drawROI_manual.setEnabled(False)
    self.button_drawROI_manual.setCheckable(True)
    self.button_drawROI_manual.setChecked(True)
    button_layout.addWidget(self.button_drawROI_manual) 
    self.button_clearROI_manual = QPushButton("2. Clear ROI")
    self.button_clearROI_manual.setFixedSize(124,60)
    self.button_clearROI_manual.setFont(self.helv12)
    self.button_clearROI_manual.setStyleSheet("QPushButton { background-color : #e9765b; color : white}")
    self.button_clearROI_manual.clicked.connect(lambda:ROI_module_clear(self))
    self.button_clearROI_manual.setEnabled(False)
    button_layout.addWidget(self.button_clearROI_manual) 
    
    button_layout.addStretch()    
    sleft_frame_layout.addLayout(button_layout) 
    sleft_frame_layout.addSpacing(20) 
    
    self.button_regfolder = QPushButton("3. Export Raw Data")
    self.button_regfolder.setFixedSize(256,60)
    self.button_regfolder.setFont(self.helv12)
    self.button_regfolder.setStyleSheet("QPushButton { background-color : #fd8f52; color : white}")
    self.button_regfolder.clicked.connect(lambda:temperaturevalue_singleimg(self))
    self.button_regfolder.setEnabled(False)
    sleft_frame_layout.addWidget(self.button_regfolder) 

    sleft_frame_layout.addStretch() 

    self.draw_ROI_lbl_manual = QLabel("")
    self.draw_ROI_lbl_manual.setStyleSheet("QLabel { background-color : #0c0c0b; color : #fc9c39}")
    self.draw_ROI_lbl_manual.setFont(self.helv16)    
    sright_frame_layout.addSpacing(20)
    sright_frame_layout.addWidget(self.draw_ROI_lbl_manual)  
    
    self.draw_ROI_widget_manual = QDrawableLabel(lWidth=self.imWidth,lHeight=self.imHeight)
    sright_frame_layout.addSpacing(5)
    sright_frame_layout.addWidget(self.draw_ROI_widget_manual) 
    
    sright_frame_layout.addStretch()
  
    return stack