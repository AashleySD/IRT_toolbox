"""
Authors: Aashley Sardjoe Mishre [1] and Oleh Dzyubachyk [2]
Affiliations: 1. Leiden university medical center, Radiology department, 2. Leiden university medical center, Division of Image Processing (LKEB)
Date: 03-08-2021
Last updated:27-12-2021
    
Title script: image_overlap
Purpose: The function overlap_images overlays the reference image (orange) on the post-baseline image (blue) 

"""

import operator #
from PIL import Image
from matplotlib import cm
import numpy as np
from os import remove, path
import cv2
from PyQt5.QtGui import QImage, qRgb
from common_functions import saveRescaledImg

def overlap_images(numpy_fixed,numpy_moving):    
    im_fixed = saveRescaledImg(numpy_fixed,'tempfix.png',None,2)#.convertToFormat(QImage.Format_Indexed8) 
    im_moving = saveRescaledImg(numpy_moving,'tempmov.png',None,2)#.convertToFormat(QImage.Format_Indexed8) 
   
    lutb, luto = np.ndarray(shape=(256,3),dtype='uint8'), np.ndarray(shape=(256,3),dtype='uint8')
    for ii in range(256):
        lutb[ii] = [0,round(127/255*ii),ii]
        luto[ii] = [ii,round(128/255*ii),0]
   
    fixed_arr_tocolor = np.array(Image.open('tempfix.png').convert('L'))
    fixed_color = lutb[fixed_arr_tocolor,:]

    mov_arr_tocolor = np.array(Image.open('tempmov.png').convert('L'))
    mov_color = luto[mov_arr_tocolor,:]
    
    imvis_overlap = Image.fromarray(fixed_color + mov_color)
    imvis_overlap.save('result.png')
    imvis_overlap = QImage('result.png').scaled(640,480)
    
    [f for f in ['result.png','tempfix.png','tempmov.png'] if path.isfile(f) and remove(f)]
    
    return imvis_overlap


