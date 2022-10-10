"""
Authors: Aashley Sardjoe Mishre [1] and Oleh Dzyubachyk [2]
Affiliations: 1. Leiden university medical center, Radiology department, 2. Leiden university medical center, Division of Image Processing (LKEB)
Date: 15-06-2021
Last updated:14-01-2022
    
Title script: RegisterData_MultipleParticipant_functions
Purpose: This script includes all subfunctions for registering data of multiple participants. 
   
"""

from os import getcwd, path, mkdir, remove, listdir, unlink
import flirimageextractor
from matplotlib import cm
from image_overlap import overlap_images
import numpy as np
from datetime import datetime
from time import sleep 
from common_functions import align_images, saveRescaledImg

from PyQt5.QtWidgets import *
from PyQt5.QtCore import QSize
from PyQt5.QtGui import QIcon
from common_functions import QDoubleStack, IRT_registration

    
def getHeadFolder(): 
    dialog = QFileDialog()
    dialog.setOption(QFileDialog.ShowDirsOnly, True) 
    dialog.FileMode(QFileDialog.Directory)
    headfldr = dialog.getExistingDirectory(None,"Select headfolder including all subjectfolders",getcwd())
    
    return headfldr    

def showsheadfolder(self):
    self.listWidget_results.clear()
    self.headfolder = getHeadFolder()

    if self.headfolder != '':
        self.headfoldershow.setText("Headfolder: " + self.headfolder)
        self.button_start_reg.setEnabled((self.headfolder != '') and (getentry_text_all(self.list_entry_widgets) != ''))
        
    enterinterventionIDs(self)
    
def store_entrytext(self,entry_txt):
    self.list_entry_widgets.append(entry_txt)
    
def enterinterventionIDs(self):
    answer_user = self.upload_img_userinput_multi.value()
    if answer_user > 0:
        while self.form_layout.rowCount() > answer_user:
            self.form_layout.takeRow(self.form_layout.rowCount()-1)
            self.list_entry_widgets.pop()
                            
        for entry_list in range(self.form_layout.rowCount(), answer_user):
             lineEdit = QLineEdit()
             lineEdit.setFont(self.helv12)
             self.form_layout.addRow("#" + str(entry_list+1) + "  ", lineEdit)
             self.form_layout.labelForField(lineEdit).setFont(self.helv12)
             store_entrytext(self,lineEdit)

             
def getentry_text_all(listwidgets):
    list_entrs = []
    for line_edit in listwidgets:
        list_entrs.append(line_edit.text())
    return list_entrs
    
def alignment_yes(self):
    self.button_align_no.setChecked(not self.button_align_yes.isChecked())
    self.spinboxTh_multi.setEnabled(self.button_align_yes.isChecked())
    
def alignment_no(self):
    self.button_align_yes.setChecked(not self.button_align_no.isChecked())
    self.spinboxTh_multi.setEnabled(self.button_align_yes.isChecked())

def Register_multisubjects(self,data_in,data_ref_arg):
    refimg = data_in[0]

    no_interventions = len(data_in)
    output_allimg_registered = np.zeros((refimg.shape[0],refimg.shape[1],no_interventions), dtype=np.float64)
    output_allimg_registered[:,:,0] = refimg

    for c in range(1,no_interventions):
        deformed_img = IRT_registration(np.ascontiguousarray(data_in[c], dtype=np.float64),np.ascontiguousarray(data_ref_arg[c], dtype=np.float64))
        output_allimg_registered[:,:,c] = np.asarray(deformed_img)[0]#,:,:]
      
    return output_allimg_registered

def autoregistration(self):
    list_entries = getentry_text_all(self.list_entry_widgets)
    subfolder = [s for s in listdir(self.headfolder) if path.isdir(path.join(self.headfolder,s))]#= listdir(self.headfolder)
    directory = "RegisteredData_" + datetime.now().strftime('%Y-%m-%d_%H-%M')
    
    self.progress.setMaximum(len(subfolder) * len(self.list_entry_widgets[1:]))
    self.progress.setValue(0)
    self.progress.setVisible(True)
    QApplication.processEvents()
    
    for subjects in subfolder:
        self.statusBar().showMessage('Registering subfolder: ' + subjects)
        filename = []
        if path.isfile(path.join(self.folder,'refimg.npy')):
            remove(path.join(self.folder,'refimg.npy'))
        if path.isfile(path.join(self.folder,'imfix.npy')):
            remove(path.join(self.folder,'imfix.npy'))
        
        self.data_readin = []
        pathsubj = path.join(self.headfolder,subjects)#pathsubject   ## check, as not it is not doing anything
        content = listdir(pathsubj)
        bFirst = True
        for jj in range(len(list_entries)):
            interventionID_user = list_entries[jj]
            for content_name in content:
                match = content_name.find(interventionID_user)
                if match!=-1:   
                    extension = path.splitext(content_name)[1]                    
                    if extension.lower() in [".jpg",".jpeg",".png",".tiff",".tif"]:
                        flir = flirimageextractor.FlirImageExtractor(palettes=[cm.jet, cm.bwr, cm.gist_ncar])
                        flir.process_image(path.join(pathsubj,content_name))
                        temp_numpy = flir.get_thermal_np()
                        self.data_readin.append(temp_numpy)
                        filename.append(path.splitext(content_name)[0])
                        if bFirst:
                            np.save(path.join(self.folder,'refimg'),temp_numpy)
                            bFirst = False
                            
        
        refimg = self.data_readin[0] 
        saveRescaledImg(refimg,path.join(self.folder,"imfix.png"),None,2)
        self.listWidget_results.addItem(QListWidgetItem(QIcon(path.join(self.folder,"imfix.png")),'Reference image: '+filename[0]))
        self.listWidget_results.update()
        QApplication.processEvents()
        
        self.data_registered = []
        
        #store
        pathstore = path.join(pathsubj, directory)  
        if not path.exists(pathstore):
            mkdir(pathstore)
                
        data_aligned_ordered = [self.data_readin[0]];
        data_aligned_refimgs = [self.data_readin[0]];
        fname = "ID0_reference_img_" + filename[0]        
        np.save(path.join(pathstore, fname),np.load(path.join(self.folder,'refimg.npy')))
        
        if path.isfile(path.join(self.folder,'refimg.npy')):
            
            for j in range(1,len(self.data_readin)): 
                if self.button_align_yes.isChecked():
                    fixed, imaligned, flag = align_images(np.load(path.join(self.folder,'refimg.npy')),self.data_readin[j],self.spinboxTh_multi.value())
                else:
                    fixed = np.load(path.join(self.folder,'refimg.npy'))
                    imaligned = self.data_readin[j]
                    
                data_aligned_ordered.append(imaligned)
                data_aligned_refimgs.append(fixed)
                self.data_registered = Register_multisubjects(self,data_aligned_ordered,data_aligned_refimgs)
                
                fname = filename[j] + "_registered"
                np.save(path.join(pathstore, "ID" + str(j) + "_" + fname),self.data_registered[:,:,j])
                imvis = overlap_images(refimg,self.data_registered[:,:,j])
                pathstore_overlap = path.join(pathstore,fname +".png")  
                imvis.save(pathstore_overlap)
                
                self.listWidget_results.addItem(QListWidgetItem(QIcon(pathstore_overlap),fname))
                self.progress.setValue(self.progress.value()+1)
                QApplication.processEvents()
        else:
            self.statusBar().showMessage('Error on subfolder:' + pathsubj)
            self.progress.setValue(self.progress.value()+len(self.list_entry_widgets[1:]))
            QApplication.processEvents()
                
    sleep(1)
    self.progress.setVisible(False)

def showsavecompletedmssg(self):
    self.statusBar().showMessage('All images are registered!')

def Run_registration_withProgressbar(self):
    allEntries = getentry_text_all(self.list_entry_widgets)
    if (allEntries != '') and (self.headfolder != ''):
        self.listWidget_results.clear()
        autoregistration(self)
        showsavecompletedmssg(self)

def multi_registration_mainscreen(self):
    self.button_multipar_registration.setVisible(False)
    self.button_multipar_segmentation.setVisible(False)
    self.page_switch.setCurrentIndex(2)

    if not path.isdir(self.folder):
        mkdir(self.folder)
    
    if (path.isdir(self.folder)  == 1):
        allcontent = listdir(self.folder)
        for f in range(len(allcontent)):
            unlink(path.join(self.folder,allcontent[f]))

  
       
def createStack3(self):

    self.list_entry_widgets = []
 
    stack = QDoubleStack()
    stack.setLabel("Multiple participants :: Image registration")
    
    sleft_frame_layout = stack.leftFrameLayout()
    sright_frame_layout = stack.rightFrameLayout()
    sleft_frame_layout.addSpacing(50)
      
    
    button_layout = QHBoxLayout()
    button_sel_hf = QPushButton("Select Headfolder")
    button_sel_hf.setFixedSize(256,60)
    button_sel_hf.setFont(self.helv12)
    button_sel_hf.setStyleSheet("QPushButton { background-color : #621940; color : white}")
    button_sel_hf.clicked.connect(lambda:showsheadfolder(self))
    button_layout.addWidget(button_sel_hf) 
    button_HFinfo = QPushButton("?")
    button_HFinfo.setFont(self.helv16)
    button_HFinfo.setStyleSheet("QPushButton { background-color : darkgrey; color: white }")
    button_HFinfo.setFixedSize(32,32)
    button_HFinfo.setToolTip('<img src="%s"> ' % ("Images/headfolder_info.png"))
    button_HFinfo.setEnabled(False)
    button_layout.addWidget(button_HFinfo) 
    button_layout.addStretch()    
    sleft_frame_layout.addLayout(button_layout) 
    sleft_frame_layout.addSpacing(50)
    
    lbl = QLabel("Enter number of image identifiers")
    lbl.setStyleSheet("QLabel { background-color : #171719; color : white}")
    lbl.setFont(self.helv12)
    sleft_frame_layout.addWidget(lbl)  
    sleft_frame_layout.addSpacing(5)  
    
    spinbox_layout = QHBoxLayout()
    self.upload_img_userinput_multi = QSpinBox()
    self.upload_img_userinput_multi.setFixedSize(256,32)
    self.upload_img_userinput_multi.setMinimum(2)
    self.upload_img_userinput_multi.setMaximum(8)
    self.upload_img_userinput_multi.setFont(self.helv12) 
    self.upload_img_userinput_multi.setStyleSheet("QSpinBox { background-color : white; color: black }")    
    self.upload_img_userinput_multi.valueChanged.connect(lambda:enterinterventionIDs(self))
    spinbox_layout.addWidget(self.upload_img_userinput_multi) 
    button_upload_info = QPushButton("?")
    button_upload_info.setFont(self.helv16)    
    button_upload_info.setStyleSheet("QPushButton { background-color : darkgrey; color: white }")
    button_upload_info.setFixedSize(32,32)
    button_upload_info.setToolTip('<img src="%s"> ' % ("Images/imageIDinfo.png"))
    button_upload_info.setEnabled(False)

    
    spinbox_layout.addWidget(button_upload_info) 
    spinbox_layout.addStretch()    
    sleft_frame_layout.addLayout(spinbox_layout) 
    sleft_frame_layout.addSpacing(20)
    
    lbl = QLabel("Intervention ID:")
    lbl.setStyleSheet("QLabel { background-color : #171719; color : white}")
    lbl.setFont(self.helv12)
    sleft_frame_layout.addWidget(lbl)  
    sleft_frame_layout.addSpacing(5)  
    
        
    self.form_layout = QFormLayout()
    self.form_layout.setVerticalSpacing(10)
    form_widget = QWidget()
    form_widget.setStyleSheet("QWidget { color : white}");
    #form_widget.setFont(self.helv20)
    form_widget.setContentsMargins(0,0,0,0) 
    form_widget.setLayout(self.form_layout)

    sleft_frame_layout.addWidget(form_widget)
    sleft_frame_layout.addSpacing(20)
    
    lbl = QLabel("Perform image alignment?")
    lbl.setStyleSheet("QLabel { background-color : #171719; color : white}")
    lbl.setFont(self.helv12)
        
    sleft_frame_layout.addWidget(lbl)  
    sleft_frame_layout.addSpacing(5)
    
    button_layout = QHBoxLayout()
    self.button_align_yes = QPushButton("Yes")
    self.button_align_yes.setFixedSize(124,60)
    self.button_align_yes.setFont(self.helv12)
    self.button_align_yes.setStyleSheet("QPushButton { background-color : #e9765b; color : white}")
    self.button_align_yes.clicked.connect(lambda:alignment_yes(self))
    self.button_align_yes.setCheckable(True)
    self. button_align_yes.setChecked(True)
    button_layout.addWidget(self.button_align_yes) 
    self.button_align_no = QPushButton("No")
    self.button_align_no.setFixedSize(124,60)
    self.button_align_no.setFont(self.helv12)
    self.button_align_no.setStyleSheet("QPushButton { background-color : #e9765b; color : white}")
    self.button_align_no.setCheckable(True)
    self.button_align_no.setChecked(False)
    self.button_align_no.clicked.connect(lambda:alignment_no(self))
    button_layout.addWidget(self.button_align_no) 
    button_infoalign = QPushButton("?")
    button_infoalign.setFont(self.helv16)
    button_infoalign.setStyleSheet("QPushButton { background-color : darkgrey; color: white }")
    button_infoalign.setFixedSize(32,32)
    button_infoalign.setToolTip('<img src="%s"> ' % ("Images/alignmentinfo_2.png"))
    button_infoalign.setEnabled(False)
    button_layout.addWidget(button_infoalign) 
    button_layout.addStretch()    
    sleft_frame_layout.addLayout(button_layout)
    sleft_frame_layout.addSpacing(5)
    self.headfoldershow = QLabel("Headfolder: ")
    self.headfoldershow.setStyleSheet("QLabel { background-color : #0c0c0b; color : white}")
    self.headfoldershow.setFont(self.helv12)    
    
    lbl = QLabel("Enter background threshold: ")
    lbl.setStyleSheet("QLabel { background-color : #171719; color : white}")
    lbl.setFont(self.helv12)
    sleft_frame_layout.addWidget(lbl)
    self.spinboxTh_multi = QSpinBox()
    self.spinboxTh_multi.setFixedSize(256,32)
    self.spinboxTh_multi.setMinimum(1)
    self.spinboxTh_multi.setMaximum(255)
    self.spinboxTh_multi.setFont(self.helv12) 
    self.spinboxTh_multi.setValue(25)
    self.spinboxTh_multi.setStyleSheet("QSpinBox { background-color : white; color: black }")
    sleft_frame_layout.addWidget(self.spinboxTh_multi)
    sleft_frame_layout.addSpacing(50)
    
    button_layout = QHBoxLayout()
    self.button_start_reg = QPushButton("Run Registration")
    self.button_start_reg.setFixedSize(256,60)
    self.button_start_reg.setFont(self.helv12)
    self.button_start_reg.setStyleSheet("QPushButton { background-color : #fd8f52; color : white}")
    self.button_start_reg.clicked.connect(lambda:Run_registration_withProgressbar(self))
    self.button_start_reg.setEnabled(False)
    button_layout.addWidget(self.button_start_reg) 
    button_inforeg = QPushButton("?")
    button_inforeg.setFont(self.helv16)
    button_inforeg.setStyleSheet("QPushButton { background-color : darkgrey; color: white }")
    button_inforeg.setFixedSize(32,32)
    button_inforeg.setToolTip('<img src="%s"> ' % ("Images/registrationinfo.png"))
    button_inforeg.setEnabled(False)
    button_layout.addWidget(button_inforeg) 
    button_layout.addStretch()    
    sleft_frame_layout.addLayout(button_layout) 
    

    sleft_frame_layout.addStretch() 
    
    
    
    sright_frame_layout.addWidget(self.headfoldershow)  
    sright_frame_layout.addSpacing(10)
    

    
    sright_frame_layout.addSpacing(20)
    self.listWidget_results = QListWidget()
    self.listWidget_results.setObjectName("listView")
    self.listWidget_results.setViewMode(QListWidget.IconMode)
    self.listWidget_results.setFont(self.helv12)
    self.listWidget_results.setStyleSheet("QListWidget { background-color : #0c0c0b; border: none; color: #fc9c39 }")
    self.listWidget_results.setIconSize(QSize(480,640))
    self.listWidget_results.setSelectionMode(0)
    sright_frame_layout.addWidget(self.listWidget_results)  
    
    #self.suff = []
    enterinterventionIDs(self)

           
    return stack