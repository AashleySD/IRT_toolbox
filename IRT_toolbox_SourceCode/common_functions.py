"""
Authors: Aashley Sardjoe Mishre [1] and Oleh Dzyubachyk [2]
Affiliations: 1. Leiden university medical center, Radiology department, 2. Leiden university medical center, Division of Image Processing (LKEB)
Date: 03-08-2021
Last updated: 27-12-2021
    
Title script: common_functions
Purpose: This script includes functions that are used for: image alignment, image registration and semi-automated ROI delineations

"""

#from PIL import Image
from PyQt5.QtGui import QImage
from os import path
import numpy as np
import pyelastix
import cv2
from math import floor,ceil

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

class QDrawableLabel(QLabel):
    def __init__(self, parent=None, lWidth=600, lHeight=600):
        super(QDrawableLabel, self).__init__(parent)
        self.setStyleSheet("QDrawableLabel {background-color:#0c0c0b} " )
        self.iHeight = lHeight
        self.iWidth = lWidth
        self.setFixedHeight(self.iHeight+50)
        self.setFixedWidth(self.iWidth)
        pixmap = QPixmap(self.iWidth,self.iHeight+50)
        pixmap.fill(QColor("#0c0c0b"))
        self.setPixmap(pixmap)
        
        self.storeRow_coordinates = []
        self.storeCol_coordinates = []
        
        self.pen = QPen();
        self.pen.setColor(Qt.red)
        self.pen.setWidth(4)
        
        self.image = None
        self.clickable = True


    def mousePressEvent(self, event):
        if self.clickable:
            ex = event.x()
            ey = event.y()
            if (0 < ex < self.iWidth) and (0 < ey < self.iHeight):  
                if (len(self.storeRow_coordinates) > 0) and (len(self.storeCol_coordinates) > 0):
                    canvas_image = QPainter(self.pixmap())
                    canvas_image.setPen(self.pen)
                    canvas_image.drawLine(QPoint(self.storeRow_coordinates[-1],self.storeCol_coordinates[-1]),QPoint(ex,ey))#,width=4, fill='red')
                self.storeRow_coordinates.append(ex)
                self.storeCol_coordinates.append(ey)
            self.update()
     
    def setClickable(self, bclickable):     
        self.clickable = bclickable
    
    def setfilename(self, FileName):
        helv10 = QFont('Helvetica', 10)
        helv10.setBold(True)
        canvas_image = QPainter(self.pixmap())
        canvas_image.setPen(QColor("orange"))
        canvas_image.setFont(helv10)
        fn_string = FileName
        canvas_image.drawText(QRect(10,self.iHeight+2,self.iWidth-10,20),Qt.AlignLeft,fn_string)
        canvas_image.end()
        
    def setMeanT(self, temp_mean):
        helv10 = QFont('Helvetica', 10)
        helv10.setBold(True)
        canvas_image = QPainter(self.pixmap())
        canvas_image.setPen(QColor("orange"))
        canvas_image.setFont(helv10)
        meanT_string = "Mean temperature: " + str(round(temp_mean,2))
        canvas_image.drawText(QRect(10,self.iHeight+15,self.iWidth-10,20),Qt.AlignLeft,meanT_string)
        canvas_image.end()
        
    def setMaxT(self, temp_max):
        helv10 = QFont('Helvetica', 10)
        helv10.setBold(True)
        canvas_image = QPainter(self.pixmap())
        canvas_image.setPen(QColor("orange"))
        canvas_image.setFont(helv10)
        maxT_string = "Max temperature: " + str(round(temp_max,2))
        canvas_image.drawText(QRect(10,self.iHeight+30,self.iWidth-10,20),Qt.AlignLeft,maxT_string)
        canvas_image.end()
        
    def setImage(self, image):
        canvas_image = QPainter(self.pixmap())
        if image is not None:
            canvas_image.drawImage(0,0,image.scaled(self.iWidth, self.iHeight))
        else:
            self.pixmap().fill(QColor("#0c0c0b"))
        
        self.image = image

    def getROImask(self,imgtemp_shp):
    
        INT_MAX = 1000
         
        def onSegment(p,q,r):
            return ((q[0] <= max(p[0],r[0])) and (q[0] >= min(p[0],r[0])) and (q[1] <= max(p[1],r[1])) and (q[1] >= min(p[1],r[1])))
         
        def orientation(p,q,r):
             
            val = (((q[1] - p[1]) * (r[0] - q[0])) - ((q[0] - p[0]) * (r[1] - q[1])))
            if val == 0:
                return 0
            if val > 0:
                return 1 # Collinear
            else:
                return 2 # Clock or counterclock
         
        def doIntersect(p1,q1,p2,q2):
             
            o1 = orientation(p1,q1,p2)
            o2 = orientation(p1,q1,q2)
            o3 = orientation(p2,q2,p1)
            o4 = orientation(p2,q2,q1)
         
            return ((o1 != o2) and (o3 != o4)) or ((o1 == 0) and onSegment(p1,p2,q1)) or ((o2 == 0) and onSegment(p1,q2,q1)) or ((o3 == 0) and onSegment(p2,p1,q2)) or ((o4 == 0) and onSegment(p2,q1,q2))
         
        def is_inside_polygon(points,p):
             
            n = len(points)
            
            if (n < 3):
                return False
             
    
            extreme = (INT_MAX,p[1])
            
            count,i = 0,0
            while True:
                next = (i + 1) % n
                if (orientation(points[i],p,points[next]) > 0) and doIntersect(points[i],points[next],p,extreme):
                    count += (((i < n) and (p[1] != points[i][1])) or ((i == n-1) and (p[1] != points[next][1])))#(p[1] != points[next][1]) and 
                # if (doIntersect(points[i],points[next],p,extreme)):
                    # if orientation(points[i],p,points[next]) == 0:
                        # return onSegment(points[i],p,points[next])
                    # count += 1
                i = next
                if (i == 0):
                    break

            return (count % 2 == 1)

        
        sR = self.storeRow_coordinates.copy()
        sC = self.storeCol_coordinates.copy()
        if (sR[0]-sR[-1])*(sR[0]-sR[-1])+(sC[0]-sC[-1])*(sC[0]-sC[-1]) < 25:
            sR = sR[:-1]
            sC = sC[:-1]
        sR.append(sR[0])
        sC.append(sC[0])
        
        y_image_coord = np.array(sR)
        x_image_coord = np.array(sC)     
        width_original,heigth_original = imgtemp_shp # imgtemp.shape
        resizefactorx = self.iHeight / width_original
        resizefactory = self.iWidth / heigth_original
        x_image_coord = x_image_coord / resizefactorx
        y_image_coord = y_image_coord / resizefactory

        
        P = [(x,y) for (x,y) in zip(x_image_coord,y_image_coord)]
        ROI_mask = np.zeros((width_original,heigth_original))
        for xx in range(floor(np.min(x_image_coord))+1,ceil(np.max(x_image_coord))):
            for yy in range(floor(np.min(y_image_coord))+1,ceil(np.max(y_image_coord))):
                if is_inside_polygon(P,(xx,yy)): 
                    ROI_mask[xx,yy] = 1.


        return ROI_mask
        
    def saveToFile(self, filename):
        canvas_image = QPixmap(self.pixmap())
        file = QFile(filename);
        file.open(QIODevice.WriteOnly);
        canvas_image.save(file,'png')
        
    def clear(self):
        if self.image is not None:
            self.setImage(self.image)

        self.update()
        self.storeRow_coordinates = []
        self.storeCol_coordinates = []

class QDoubleStack(QWidget):
    def __init__(self, parent=None):
        super(QWidget, self).__init__(parent)
        
        helv20 = QFont('Helvetica', 20) 

        
        stack_layout = QHBoxLayout()
        stack_layout.setContentsMargins(0,0,0,0)
        
        self.setAutoFillBackground(True)
        pal = QPalette()
        pal.setColor(QPalette.Window, QColor("#0c0c0b"));
        self.setPalette(pal)

        self.left_frame = QWidget()
        self.left_frame.setStyleSheet("QWidget {background-color: #171719}")
        self.left_frame.setFixedWidth(340)    
        self.left_frame_layout = QVBoxLayout()
        self.left_frame.setLayout(self.left_frame_layout)
        
        lbl = QLabel("IRT Toolbox")
        lbl.setStyleSheet("QLabel {background-color: #171719; color: white}")
        lbl.setFont(helv20)
        
        self.left_frame_layout.addSpacing(20)
        self.left_frame_layout.addWidget(lbl)
        
        self.right_frame = QWidget()
        self.right_frame.setStyleSheet("background-color: #0c0c0b")
        self.right_frame_layout = QVBoxLayout()
        self.right_frame.setLayout(self.right_frame_layout)
    
        self.lbl = QLabel("")
        self.lbl.setStyleSheet("QLabel { background-color: #0c0c0b; color: white}")
        self.lbl.setFont(helv20)    
    
        self.right_frame_layout.addSpacing(20)
        self.right_frame_layout.addWidget(self.lbl)  
        self.right_frame_layout.addSpacing(20)
    
        stack_layout.addWidget(self.left_frame)
        stack_layout.addWidget(self.right_frame)
        self.setLayout(stack_layout)
        


        
    def setLabel(self, txt):
        self.lbl.setText(txt);

    def leftFrame(self):
       return self.left_frame;
       
    def leftFrameLayout(self):
       return self.left_frame_layout;
       
    def rightFrame(self):
       return self.right_frame;

    def rightFrameLayout(self):
       return self.right_frame_layout;

def saveRescaledImg(img,fn_imvis='',mask=None,scale=1):

    rescaled = (255.0 / img.max() * (img - np.min(img[np.nonzero(img)])))
    imsize = np.shape(rescaled)
    
    imref_img = QImage(rescaled.astype(np.uint8), imsize[1], imsize[0], QImage.Format_Grayscale8)
    
    if mask is not None:
        imref_img = imref_img.convertToFormat(QImage.Format_RGB32)
        mask_img = QImage(32 * mask.astype(np.uint8), imsize[1], imsize[0], QImage.Format_Grayscale8).convertToFormat(QImage.Format_RGB32)
        p = QPainter()

        p.begin(mask_img)
        p.setCompositionMode(QPainter.CompositionMode_Overlay)
        p.fillRect(0,0,imsize[1],imsize[0], Qt.red)
        p.end()
        

        p.begin(imref_img)
        p.setCompositionMode(QPainter.CompositionMode_Screen)#RasterOp_SourceXorDestination
        p.drawImage(0,0,mask_img)
        p.end()

    if scale != 1:
        imref_img = imref_img.scaled(QSize(scale*imsize[1],scale*imsize[0]))
    
    if fn_imvis != '':
        imref_img.save(fn_imvis)
    
    return imref_img
    
def getbackofneck_coordinates(thresholded_img,img):
    No_rows = thresholded_img.shape[0]
    list_Pix = np.zeros((No_rows))
    
    for i in range(No_rows):
        list_Pix[i] = sum(thresholded_img[i,:])
        if list_Pix[i] == 0:
            list_Pix[i] = 2*thresholded_img.shape[1] #if a row has no foreground pixels.. assing a very large number to this, so that it will not be detected as the width with the smallest row
     
    shortest_row = np.min(list_Pix) #take the row number whith the smallest amount of foreground pixels.. this should be the neck since it has the smallest width in the thoracic area
    shortest_row_list = ([h for h, x in enumerate(list_Pix) if x == shortest_row]) # check if there are more rows having this same amount of foreground pixels
    Neck_row = shortest_row_list[len(shortest_row_list)-1] #take the last one... this would be closer at the base of the neck
    
    Neck_line = ([h for h, x in enumerate(thresholded_img[Neck_row,:]) if x == 1])
    storefirstpix = 0
    for jj in range(len(Neck_line)):
        if storefirstpix == 0 and img[Neck_row,Neck_line[jj]]>30:
            storefirstpix = Neck_line[jj]
    
    Neck_col = storefirstpix;
    return Neck_row,Neck_col
    
def align_images(fixed_image,moving,threshold_background):
    redflag = 0
    fixed = fixed_image    
    [thres_fixed,flagfixed] = threshold_image(fixed,threshold_background)
    [thres_moving,flagmoving] = threshold_image(moving,threshold_background)
    moving_aligned = []
    if (not flagfixed) and (not flagmoving):
        fixed_neckbase_row,fixed_neckbase_col = getbackofneck_coordinates(thres_fixed,fixed)
        moving_neckbase_row,moving_neckbase_col = getbackofneck_coordinates(thres_moving,moving)
        
        shift_rows = fixed_neckbase_row - moving_neckbase_row;
        shift_columns = fixed_neckbase_col - moving_neckbase_col;
        
        rows,cols = fixed.shape
        
        M = np.float64([[1,0,shift_columns],[0,1,shift_rows]])
        moving_aligned = cv2.warpAffine(moving,M,(cols,rows)) 
    
        find_middle_column = [i for i, x in enumerate(thres_fixed[fixed_neckbase_row,:]) if x == 1]
        middle_column_fixed = round((find_middle_column[len(find_middle_column)-1] + find_middle_column[0]) / 2)
        uppercut = []
        
        for rr in range(0,rows):
            for cc in range(0,cols):
                if moving_aligned[rr,cc] == 0:
                    fixed[rr,cc] = 0
  
    else:
        redflag = 1
    
    return fixed, moving_aligned, redflag
    
    
def IRT_registration(post, pre):
    params=pyelastix.get_default_params(type='BSPLINE')
    params.FixedInternalImagePixelType = "float"
    params.MovingInternalImagePixelType = "float"
    params.FixedImageDimension =2
    params.MovingImageDimension =2
    params.UseDirectionCosines = "true"
    params.Registration = "MultiResolutionRegistration"
    params.Interpolator= "BSplineInterpolator"
    params.ResampleInterpolator= "FinalNearestNeighborInterpolator"
    params.Resampler ="DefaultResampler"
    params.FixedImagePyramid =  "FixedRecursiveImagePyramid"
    params.MovingImagePyramid = "MovingRecursiveImagePyramid"
    params.Optimizer = "AdaptiveStochasticGradientDescent"
    params.Transform = "BSplineTransform"
    params.Metric = "AdvancedMattesMutualInformation"
    params.FinalGridSpacingInPhysicalUnits = 16
    params.FinalGridSpacingInVoxels = 16
    params.HowToCombineTransforms  ="Compose"
    params.NumberOfHistogramBins =32
    params.ErodeMask= "false"
    params.NumberOfResolutions=4
    params.MaximumNumberOfIterations=450
    params.MaximumStepLength=0.5
    params.NumberOfSpatialSamples=2048
    params.NewSamplesEveryIteration = "true"
    params.ImageSampler= "Full"
    params.BSplineInterpolationOrder = 1
    params.FinalBSplineInterpolationOrder = 3
    params.DefaultPixelValue = 0
    # Apply the registration (im1 and im2 can be 2D or 3D)
    [im1_deformed, field] = pyelastix.register(post, pre, params, verbose = 0)    
    return [im1_deformed]
    
def threshold_image(img,threshold_background):
    redflag = 0
    No_rows = img.shape[0];
    No_cols = img.shape[1];
    thresholded_img = np.zeros((No_rows,No_cols))

    for r in range(0,No_rows):
        arraycol = np.zeros((No_cols-1))
        for cols in range(1,No_cols):
            arraycol[cols-1] = abs(img[r,cols] - img[r,cols-1])    #determines the difference between consecutive pixels to get a gradient in each row

        findlargestpeaks = [i for i, x in enumerate(arraycol) if x > np.mean(arraycol)]
       
        if len(findlargestpeaks) != 0: 
            counter = 1
            storepeak = np.zeros(len(findlargestpeaks))
            
            for cols_peak in range (0, len(findlargestpeaks)-1):  
                if img[r,findlargestpeaks[cols_peak]] > threshold_background: #take the pixel with a temperature higher than room temperature
                    storepeak[counter] = findlargestpeaks[cols_peak]
                    counter += 1;
                    
            storepeak_indx_nonzero = [i for i, x in enumerate(storepeak) if x > 0] #remove all low temperature pixels
            if len(storepeak_indx_nonzero) > 2:
                storepeak_abovezero = storepeak[storepeak_indx_nonzero]
                array_storepeak = len(storepeak_abovezero)
                thresholded_img[r,int(storepeak_abovezero[0]):int(storepeak_abovezero[array_storepeak-1])] = 1; # fill in the pixels in between the two jump with ones in the row
            else:
                redflag = 1
        else:
            reflag = 1
    
    return thresholded_img, redflag

    
    
 