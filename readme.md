# The infrared thermography toolbox
The IRT-toolbox is an open source tool that was developed to facilitate skin temperature analyses in repeated datasets. The toolbox was designed for applications in the thoracic area, including supraclavicular brown adipose tissue in human adults. 

## Main features of the IRT-toolbox
- Conversion of thermal FLIR images into temperature maps using the Python package: flirimageextractor
- Image pre-alignment:
Image pre-alignement is performed to align each follow-up image towards the baseline image within a dataset. If this step is not performed, registration results can be severely distorted.
- Non-rigid image registration:
Non-rigid image registration is subsequently used to deform each follow-up image to fully overlap with the baseline image within a dataset using the python package: pyelastix
- ROI delineation:
ROIs that are delineated on the first image within the dataset (e.g., baseline image) can be directly transferred to all registered follow-up images, such that ROI delineations are only required on the first image in the dataset. The toolbox extracts minimum, maximum and mean skin temperatures and exports the data to Excel.

It is recommended to watch the video tutorial, which is available at:
Sardjoe Mishre, Aashley, et al. "The infrared thermography toolbox: an open-access semi-automated segmentation tool for  extracting skin temperatures in the thoracic region including supraclavicular brown adipose tissue", Journal of medical systems (2022)

## Installation
- The IRT-toolbox application (IRT-toolbox.exe) can be directly used after downloading the application without installing any additional software.
- The IRT-toolbox python source scripts require the applications: "ExifTool" and "Elastix"
- Exiftool is required to read metadata from the thermal images. Installation instructions can be found here: https://exiftool.org/install.html
- The Elastix application is required for the registration step. Installation instructions can be found here: https://elastix.lumc.nl/download.php

## Citation
If you find this software useful for your project or research, please give some credits to authors who developed it by citing the following paper:
Sardjoe Mishre, Aashley, et al. "The infrared thermography toolbox: an open-access semi-automated segmentation tool for  extracting skin temperatures in the thoracic region including supraclavicular brown adipose tissue", Journal of medical systems (2022)
