#!/usr/bin/env python3

"""
Authors: Aashley Sardjoe Mishre [1] and Oleh Dzyubachyk [2]
Affiliations: 1. Leiden university medical center, Radiology department, 2. Leiden university medical center, Division of Image Processing (LKEB)
Email: A.S.D.Sardjoe_Mishre@lumc.nl
Date: 20-09-2021
Last updated:17-01-2022
    
Title script: MainScreen_startfunction 
Purpose: the user should start this script for running the program. This code displays the three options for analysis: 1. single subjects analysis
2. multiple subject analyses and 3. single image ROI delineations

"""

import sys
from os import environ, path, mkdir
from Single_Participant_module import createStack2, Single_participant
from RegisterData_MultipleParticipants_functions import createStack3, multi_registration_mainscreen
from ROIModule_MultiParticipants_functions import createStack4, createStack9, ROI_semiauto_mainscreen
from ROIModule_SingleParticipant_functions import createStack7, createStack8
from manualROIsegmentation import createStack5, ROI_manual_main
from AlignData_SingleParticipant_functions import createStack6
from PyQt5.QtWidgets import * 
from PyQt5.QtGui import * 
from PyQt5.QtCore import Qt
   
class irttoolbox(QMainWindow):

    def __init__(self, parent=None):
    
        super(irttoolbox, self).__init__(parent)
        
        main_frame = QWidget()
        self.setCentralWidget(main_frame)
        self.page_switch = QStackedWidget()  
        self.data_readin = []
        self.filenames = []
        self.filepathuser = []
        self.imagetemp = []
        self.alignThresh = []
        self.data_registered = []
        self.pathsubject = []
        
        self.imWidth = 640
        self.imHeight = 480
        
        width_screen = self.width()
        height_screen = self.height()
        hs4 = round(height_screen / 1.5)
        ws5 = round(width_screen / 1.5)


        self.helv20 = QFont('Helvetica', 20) 
        self.helv20.setBold(True)
        self.helv16 = QFont('Helvetica', 16)
        self.helv16.setBold(True)
        self.helv12 = QFont('Helvetica', 12)
        
        single = "#621940"
        multi = "#ED8554"
        manual = "#BE375F"
        registration_color = "#ffb980"
        ROI_color = "#ffb997"
        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0,0,0,0)

        menubar = self.menuBar()
        main_menu = menubar.addMenu("IRT Toolbox")
        home_action = QAction("Home",self)
        home_action.triggered.connect(lambda:self.home_return())
        main_menu.addAction(home_action)
        main_menu.addSeparator()
        single_subject_action = QAction("Single subject analysis",self)
        single_subject_action.triggered.connect(lambda:Single_participant(self))
        main_menu.addAction(single_subject_action)
        main_menu.addSeparator()
        automated_action = QAction("Automated image registration",self)
        automated_action.triggered.connect(lambda:multi_registration_mainscreen(self))
        main_menu.addAction(automated_action)  
        multiple_action = QAction("Semi-automated ROI extraction",self)
        multiple_action.triggered.connect(lambda:ROI_semiauto_mainscreen(self))
        main_menu.addAction(multiple_action)  
        main_menu.addSeparator()
        manual_action = QAction("Manual ROI delineations",self)
        manual_action.triggered.connect(lambda:ROI_manual_main(self))
        main_menu.addAction(manual_action)
        
        self.progress = QProgressBar()
        palette = self.progress.palette()
        palette.setColor(QPalette.Text, Qt.white);
        self.progress.setPalette(palette);
        self.progress.setStyleSheet("QProgressBar::chunk {background-color: green}") 
        self.progress.setMaximumHeight(20)
        self.progress.setMaximumWidth(350)
        self.progress.setFormat('Please wait while images are being aligned... (%p%)')
        self.progress.setAlignment(Qt.AlignCenter)
        self.progress.setVisible(False)
        self.statusBar().addPermanentWidget(QLabel(''))
        self.statusBar().addPermanentWidget(self.progress)
 
        stack1 = QWidget()
        stack1_layout = QVBoxLayout() 
        stack1.setStyleSheet('background-color: #0c0c0b') 
        
        lbl = QLabel("IRT Toolbox :: Home")
        lbl.setStyleSheet("QLabel { background-color : #0c0c0b; color : white}")
        lbl.setFont(self.helv20)

        stack1_btnGrp = QGridLayout()
        
        button_singleparticipant = QPushButton("Single subject\nanalysis")
        button_singleparticipant.setStyleSheet('color : white; background-color: ' + single) 
        button_singleparticipant.setFont(self.helv20)
        button_singleparticipant.setFixedSize(ws5,hs4)            
        button_singleparticipant.clicked.connect(lambda:Single_participant(self))
        stack1_btnGrp.addWidget(button_singleparticipant,0,0)
        
        button_multiparticipant = QPushButton("Multiple subject\nanalysis")
        button_multiparticipant.setStyleSheet('color : white; background-color: ' + multi) 
        button_multiparticipant.setFont(self.helv20)
        button_multiparticipant.setFixedSize(ws5,hs4) 
        button_multiparticipant.clicked.connect(lambda:multiple_participants_options(self))
        stack1_btnGrp.addWidget(button_multiparticipant,0,1)
        
        self.button_multipar_registration = QPushButton("Image registration")
        self.button_multipar_registration.setStyleSheet('color : white; background-color: ' + registration_color) 
        self.button_multipar_registration.setFont(self.helv20)  
        self.button_multipar_registration.setFixedSize(ws5,round(2*hs4/3)) 
        self.button_multipar_registration.clicked.connect(lambda:multi_registration_mainscreen(self))
        stack1_btnGrp.addWidget(self.button_multipar_registration,1,1)
        self.button_multipar_registration.setVisible(False)
        
        self.button_multipar_segmentation = QPushButton("ROI segmentation")
        self.button_multipar_segmentation.setStyleSheet('color : white; background-color: ' + ROI_color) 
        self.button_multipar_segmentation.setFont(self.helv20)
        self.button_multipar_segmentation.setFixedSize(ws5,round(2*hs4/3)) 
        self.button_multipar_segmentation.clicked.connect(lambda:ROI_semiauto_mainscreen(self))
        stack1_btnGrp.addWidget(self.button_multipar_segmentation,2,1)
        self.button_multipar_segmentation.setVisible(False)

        button_manual = QPushButton("Manual ROI\ndelineations")
        button_manual.setStyleSheet('color : white; background-color: ' + manual) 
        button_manual.setFont(self.helv20)        
        button_manual.setFixedSize(ws5,hs4)
        button_manual.clicked.connect(lambda:ROI_manual_main(self))
        stack1_btnGrp.addWidget(button_manual,0,2)
        
        stack1_layout.addSpacing(50)
        stack1_layout.addWidget(lbl)
        stack1_layout.addSpacing(50)
        stack1_layout.addLayout(stack1_btnGrp)
        stack1_layout.addStretch()
        stack1.setLayout(stack1_layout)
        
        self.page_switch.addWidget(stack1)
        self.stack2 = createStack2(self)
        self.page_switch.addWidget(self.stack2)     
        self.stack3 = createStack3(self)        
        self.page_switch.addWidget(self.stack3)   
        self.stack4 = createStack4(self)        
        self.page_switch.addWidget(self.stack4)      
        self.page_switch.addWidget(createStack5(self))  
        self.page_switch.addWidget(createStack6(self))   
        self.page_switch.addWidget(createStack7(self))   
        self.stack8 = createStack8(self)
        self.page_switch.addWidget(self.stack8)    
        self.stack9 = createStack9(self)
        self.page_switch.addWidget(self.stack9)                  
        self.folder = 'IRT_temp_folder'
        
        if not path.isdir(self.folder):
            mkdir(self.folder)

        main_layout.addWidget(self.page_switch)
        main_frame.setLayout(main_layout)
        self.setWindowTitle("IRT Toolbox-v_17.01.2022")

    def home_return(self):
        self.page_switch.setCurrentIndex(0)       

def multiple_participants_options(self):

    self.button_multipar_registration.setVisible(True)
    self.button_multipar_segmentation.setVisible(True)
    
def main():

    app = QApplication(sys.argv)
    ex = irttoolbox()
    ex.showMaximized()


    return app.exec_()
    
if __name__ == '__main__':
    sys.exit(main())
    
