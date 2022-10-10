"""
Authors: Aashley Sardjoe Mishre [1] and Oleh Dzyubachyk [2]
Affiliations: 1. Leiden university medical center, Radiology department, 2. Leiden university medical center, Division of Image Processing (LKEB)
Date: 21-06-2021
Last updated:14-01-2022
    
Title script: ROIModule_MutliParticipants_functions
Purpose: This script includes all subfunctions for obtaining semi-automated segmented ROIs of a single dataset of one participant. 
This script is used in the mutliple participant analyses

"""

from os import getcwd, path, listdir, unlink
import numpy as np
import flirimageextractor
from matplotlib import cm
import pandas as pd
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from common_functions import saveRescaledImg, QDoubleStack, QDrawableLabel

  
def readin_temp():    
    dialog = QFileDialog()
    dialog.FileMode(QFileDialog.ExistingFile)
    filepathjpg, _filter = dialog.getOpenFileName(None,"Select image file",getcwd(),"Image (*.png *.jpeg *.jpg *.tiff)")
    flir = flirimageextractor.FlirImageExtractor(palettes=[cm.jet, cm.bwr, cm.gist_ncar])
    if filepathjpg != "":
        flir.process_image(filepathjpg)
        temp_numpy = flir.get_thermal_np()
    else:
        temp_numpy = []
    
    return temp_numpy,filepathjpg

def uploadrefimg(self):
    img_nmpy,fpath = readin_temp()
    if img_nmpy != []:
        filename_withextension = path.basename(fpath)
        self.imagetemp_name = path.splitext(filename_withextension)[0] ### check, as now it is not doing anything
        self.imagetemp = img_nmpy
        self.draw_ROI_widget2.setImage(saveRescaledImg(self.imagetemp))
        self.draw_ROI_widget2.setEnabled(self.imagetemp.size > 0)
        self.button_drawROI_multi.setChecked(True)  
        self.filepathuser = path.dirname(fpath)
        
def clear_ROI_multi(self):
    ROI_module_multi(self)
    self.draw_ROI_widget2.clear()
    
def ROI_module_multi(self):
    self.draw_ROI_widget2.setEnabled(self.button_drawROI_multi.isChecked())
 
def transferROI_registeredimg(self):
    if len(self.draw_ROI_widget2.storeCol_coordinates) > 0:
        temp_path = self.folder 
        if not path.isdir(temp_path):
            mkdir(temp_path)
        
        if (path.isdir(temp_path) == 1):
            allcontent = listdir(temp_path)
            for f in range(len(allcontent)):
                unlink(path.join(temp_path,allcontent[f]))
  
        registered_datareadin = []
        self.registered_imgname = []
        if not self.filepathuser:
            initdir_user = getcwd()
        else:
            initdir_user = self.filepathuser
        dialog = QFileDialog()
        dialog.setOption(QFileDialog.ShowDirsOnly, True) 
        dialog.FileMode(QFileDialog.Directory)
        self.pathsubject = dialog.getExistingDirectory(None,"Select directory",initdir_user)
        
        if self.pathsubject:
            content = [c for c in listdir(self.pathsubject) if (path.splitext(c)[1] == '.npy')]#listdir(self.pathsubject)
            for content_name in content:    
                npy_array = np.load(path.join(self.pathsubject,content_name))
                registered_datareadin.append(npy_array)
                self.registered_imgname.append(content_name)
        
            
            self.data_registered = np.array(registered_datareadin)#registered_datareadin # 
            showregImagesmasked(self)
            self.tempvals,self.tempmean,self.tempmax,self.tempmin,self.ROI_pix = get_temperature_vals(self)
        self.button_export.setEnabled(True)
    else:
        drawROIwarningmssg()

def showregImagesmasked(self):
    self.page_switch.setCurrentIndex(8)
    self.frame_quantify_ROI_widget_multi.clear()

    if path.isdir(self.folder):
        allcontent = listdir(self.folder)
        for f in range(len(allcontent)):
            unlink(path.join(self.folder,allcontent[f]))
                
    for i in range(len(self.registered_imgname)):
        IDcheck = "ID0" in self.registered_imgname[i]
        if IDcheck:
            image_ref = self.data_registered[i]
                 
            
    fnames = []       
    Mask = self.draw_ROI_widget2.getROImask(image_ref.shape)  
    No_images = np.shape(self.data_registered)[0]

    self.tempvals = []
    self.tempmean = np.zeros(No_images)
    self.tempmax = np.zeros(No_images)
    self.tempmin = np.zeros(No_images)
    
    for h in range(No_images):
        image_reg_temp = self.data_registered[h]
        idx = np.where(image_reg_temp == 0)
        image_reg_temp[idx] = np.min(image_reg_temp[np.nonzero(image_reg_temp)])
        fn = path.join(self.folder,str(h) + "masked_reg.png")
        imROI = saveRescaledImg(image_reg_temp,fn,Mask)
        
        data = Mask * self.data_registered[h]
        
        data_list = []
        [x for rows in range(data.shape[0]) for cols in range(data.shape[1]) if ((data[rows,cols] > 0) and data_list.append(data[rows,cols]))]

        vals = np.array(data_list) 
        self.tempvals.append(vals)
        self.tempmean[h] = np.mean(vals)
        self.tempmax[h] = np.amax(vals)
        self.tempmin[h] = np.amin(vals)
        self.ROI_pix = len(vals)

    images = []
 
    for img_list in range(len(self.registered_imgname)):
        
        fn = path.join(self.folder, str(img_list) + "masked_reg.png")  
        
        draw_ROI = QDrawableLabel(lWidth=self.imWidth,lHeight=self.imHeight)
        images.append(draw_ROI)
        draw_ROI.setImage(QImage(fn))
        draw_ROI.setfilename(path.splitext(self.registered_imgname[img_list])[0])
        draw_ROI.setMeanT(self.tempmean[img_list])
        draw_ROI.setMaxT(self.tempmax[img_list])
        
        fname = path.join(self.folder,'masked_ROI_' + str(img_list) + '.png')
        draw_ROI.saveToFile(fname)
        
        item = QListWidgetItem(QIcon(fname),'')
        item.setToolTip('')
        self.frame_quantify_ROI_widget_multi.addItem(item)
        
    self.frame_quantify_ROI_widget_multi.setVisible(True)    
    self.frame_quantify_ROI_widget_multi.update()

        
def get_temperature_vals(self):
    nn = len(self.registered_imgname)
    tempvals_arr = []
    tempmean_arr = np.zeros(nn)
    tempmax_arr = np.zeros(nn)
    tempmin_arr = np.zeros(nn)
    ROI_pix_arr = np.zeros(nn)
    Mask = self.draw_ROI_widget2.getROImask(self.data_registered[0].shape)
    for i in range(nn):       
        data = Mask * self.data_registered[i]
                
        data_list = []
        [x for rows in range(data.shape[0]) for cols in range(data.shape[1]) if ((data[rows,cols] > 0) and data_list.append(data[rows,cols]))]

                    
        vals = np.array(data_list)            
        tempvals_arr.append(vals)
        tempmean_arr[i] = np.mean(vals)
        tempmax_arr[i] = np.amax(vals)
        tempmin_arr[i] = np.amin(vals)
        ROI_pix_arr[i] = len(vals)
               
    return tempvals_arr,tempmean_arr,tempmax_arr,tempmin_arr,ROI_pix_arr

def drawROIwarningmssg():
    warningROI = QMessageBox()
    warningROI.setIcon(QMessageBox.Warning)
    warningROI.setText("Please draw an ROI first!     ")
    warningROI.setWindowTitle("Draw ROI")
    warningROI.setStandardButtons(QMessageBox.Ok)
    warningROI.exec_()
 
def saveDataToExcel(self):
    if len(self.draw_ROI_widget2.storeCol_coordinates) > 1:
        if not self.filepathuser:
            initdir_user = getcwd()
        else:
            initdir_user = self.filepathuser
        dialog = QFileDialog()
        file, _filter = dialog.getSaveFileName(None,"Save as Excel table...",initdir_user,"Excel file (*.xlsx)")
        
        if file != '':
            filename_user = path.splitext(file)[0]
            self.registered_datareadin = []
            self.registered_imgname = []
            content = listdir(self.pathsubject)
            for ii in range(len(content)):
                content_name = content[ii]
                extension = path.splitext(content_name)[1]
                if extension == ".npy":              
                    npy_array = np.load(path.join(self.pathsubject,content_name))
                    self.registered_datareadin.append(npy_array)
                    self.registered_imgname.append(path.splitext(content_name)[0])
            
            self.tempvals,self.tempmean,self.tempmax,self.tempmin,self.ROI_pix = get_temperature_vals(self)
            
            #export data to excel  -summary data
            Keyslist,values = [], []
            Keyslist.append("Parameters")
            values.append(["Mean Temperature", "Max Temperature","Min Temperature","Pixels in ROI"])
            for h in range (len(self.registered_imgname)):
                Keyslist.append(self.registered_imgname[h]) 
                values.append([(self.tempmean[h]), (self.tempmax[h]), (self.tempmin[h]), (self.ROI_pix)]) 
                    
            list_intv_outcomes = dict(zip(Keyslist, values))                    
            datasum = pd.DataFrame(list_intv_outcomes)
            fn_store_sum = str.replace(file,".xlsx","_summary.xlsx")
            writer_sum = pd.ExcelWriter(fn_store_sum, engine='xlsxwriter')
            datasum.to_excel(writer_sum, sheet_name='Temperature data', index=False)
            writer_sum.save()
            #export data to excel  -raw data
            Keyslist,values = [],[]
            for h in range (len(self.registered_imgname)):
                Keyslist.append(self.registered_imgname[h]) 
                values.append(self.tempvals[h]) 
                    
            list_intv_outcomes_raw=dict(zip(Keyslist, values))                    
            data = pd.DataFrame(list_intv_outcomes_raw)
            fn_store_raw = str.replace(file,".xlsx","_raw.xlsx")
            writer_raw = pd.ExcelWriter(fn_store_raw, engine='xlsxwriter')
            data.to_excel(writer_raw, sheet_name='Raw temperature data', index=False)
            writer_raw.save() 
            showsavecompletedmssg(self)
            
            if (path.isdir(self.folder)  == 1):
                allcontent = listdir(self.folder)
                for f in range(len(allcontent)):
                    unlink(path.join(self.folder,allcontent[f]))
    else:
        drawROIwarningmssg()

def showsavecompletedmssg(self):  
    self.statusBar().showMessage('Finished exporting!')
    
def ROI_semiauto_mainscreen(self):
    self.draw_ROI_widget2.clear()
    self.button_multipar_registration.setVisible(False)
    self.button_multipar_segmentation.setVisible(False)
    self.page_switch.setCurrentIndex(3)

    if not path.isdir(self.folder):
        mkdir(self.folder)
    
    if path.isdir(self.folder):
        allcontent = listdir(self.folder)
        for f in range(len(allcontent)):
            unlink(path.join(self.folder,allcontent[f]))
        
def createStack4(self):

    stack = QDoubleStack()
    stack.setLabel("Multiple participants :: Semi-automated ROI extraction")
    
    sleft_frame_layout = stack.leftFrameLayout()
    sright_frame_layout = stack.rightFrameLayout()

    sleft_frame_layout.addSpacing(50)    
    
    button_layout = QHBoxLayout()
    button_refimg = QPushButton("1. Upload Reference Image")
    button_refimg.setFixedSize(256,60)
    button_refimg.setFont(self.helv12)
    button_refimg.setStyleSheet("QPushButton { background-color : #621940; color : white}")
    button_refimg.clicked.connect(lambda:uploadrefimg(self))
    button_layout.addWidget(button_refimg) 
    button_uploadinfo = QPushButton("?")
    button_uploadinfo.setFont(self.helv16)
    button_uploadinfo.setStyleSheet("QPushButton { background-color : darkgrey; color: white }")
    button_uploadinfo.setFixedSize(32,32)
    button_uploadinfo.setToolTip('<img src="%s"> ' % ("Images/uploadinfo_semiauto.png"))
    button_uploadinfo.setEnabled(False)
    button_layout.addWidget(button_uploadinfo) 
    button_layout.addStretch()    
    sleft_frame_layout.addLayout(button_layout) 
    sleft_frame_layout.addSpacing(50) 
        
    button_layout = QHBoxLayout()
    self.button_drawROI_multi = QPushButton("2. Draw ROI")
    self.button_drawROI_multi.setFixedSize(124,60)
    self.button_drawROI_multi.setFont(self.helv12)
    self.button_drawROI_multi.setStyleSheet("QPushButton { background-color : #c7594b; color : white}")
    self.button_drawROI_multi.clicked.connect(lambda:ROI_module_multi(self))
    self.button_drawROI_multi.setCheckable(True)
    self.button_drawROI_multi.setChecked(True)
    button_layout.addWidget(self.button_drawROI_multi) 
    button_clearROI = QPushButton("2. Clear ROI")
    button_clearROI.setFixedSize(124,60)
    button_clearROI.setFont(self.helv12)
    button_clearROI.setStyleSheet("QPushButton { background-color : #c7594b; color : white}")
    button_clearROI.clicked.connect(lambda:clear_ROI_multi(self))
    button_layout.addWidget(button_clearROI) 
    button_layout.addStretch()    
    sleft_frame_layout.addLayout(button_layout) 
    sleft_frame_layout.addSpacing(50) 
    
    
    button_layout = QHBoxLayout()
    button_regfolder = QPushButton("3. Upload Registered Data")
    button_regfolder.setFixedSize(256,60)
    button_regfolder.setFont(self.helv12)
    button_regfolder.setStyleSheet("QPushButton { background-color : #e9765b; color : white}")
    button_regfolder.clicked.connect(lambda:transferROI_registeredimg(self))
    button_layout.addWidget(button_regfolder) 
    button_uploadinfo = QPushButton("?")
    button_uploadinfo.setFont(self.helv16)
    button_uploadinfo.setStyleSheet("QPushButton { background-color : darkgrey; color: white }")
    button_uploadinfo.setFixedSize(32,32)
    button_uploadinfo.setToolTip("Apply ROI to registered images")
    button_uploadinfo.setEnabled(False)
    button_layout.addWidget(button_uploadinfo)
    button_layout.addStretch()  
    sleft_frame_layout.addLayout(button_layout)         
    sleft_frame_layout.addSpacing(50) 
    
    self.button_export = QPushButton("4. Export Raw Data")
    self.button_export.setFixedSize(256,60)
    self.button_export.setFont(self.helv12)
    self.button_export.setStyleSheet("QPushButton { background-color : #fd8f52; color : white}")
    self.button_export.clicked.connect(lambda:saveDataToExcel(self))
    self.button_export.setEnabled(False)
    sleft_frame_layout.addWidget(self.button_export) 
    sleft_frame_layout.addSpacing(20) 

    sleft_frame_layout.addStretch() 
    
    self.draw_ROI_widget2 = QDrawableLabel(lWidth=self.imWidth,lHeight=self.imHeight)
    self.draw_ROI_widget2.setEnabled(False)
    sright_frame_layout.addSpacing(5)
    sright_frame_layout.addWidget(self.draw_ROI_widget2) 
    sright_frame_layout.addStretch()
          
    return stack


def createStack9(self):

    stack = QDoubleStack()
    stack.setLabel("Multiple participants :: Semi-automated ROI extraction")
    
    sleft_frame_layout = stack.leftFrameLayout()
    sright_frame_layout = stack.rightFrameLayout()

    sleft_frame_layout.addSpacing(50)    
    
    button_layout = QHBoxLayout()
    button_export = QPushButton("Export Data")
    button_export.setFixedSize(256,60)
    button_export.setFont(self.helv12)
    button_export.setStyleSheet("QPushButton { background-color : #621940; color : white}")
    button_export.clicked.connect(lambda:saveDataToExcel(self))
    button_layout.addWidget(button_export) 
    button_layout.addStretch()    
    sleft_frame_layout.addLayout(button_layout) 
    sleft_frame_layout.addSpacing(20) 
        
    self.button_export = QPushButton("Draw Another ROI")
    self.button_export.setFixedSize(256,60)
    self.button_export.setFont(self.helv12)
    self.button_export.setStyleSheet("QPushButton { background-color : #fd8f52; color : white}")
    self.button_export.clicked.connect(lambda:ROI_semiauto_mainscreen(self))
    self.button_export.setEnabled(False)
    sleft_frame_layout.addWidget(self.button_export) 
    sleft_frame_layout.addSpacing(20) 

    sleft_frame_layout.addStretch() 
    
    self.frame_quantify_ROI_widget_multi = QListWidget()
    self.frame_quantify_ROI_widget_multi.setViewMode(QListWidget.IconMode)
    self.frame_quantify_ROI_widget_multi.setFont(self.helv12)
    self.frame_quantify_ROI_widget_multi.setStyleSheet("QListWidget { background-color : #0c0c0b; border: none; color: #fc9c39 }")
    self.frame_quantify_ROI_widget_multi.setIconSize(QSize(self.imHeight,self.imWidth))
    self.frame_quantify_ROI_widget_multi.setSelectionMode(0)
    self.frame_quantify_ROI_widget_multi.setVisible(False)
    sright_frame_layout.addWidget(self.frame_quantify_ROI_widget_multi)  
        
    return stack