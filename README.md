# acute_assay
Supporting information for **"An image-based assay for the rapid quantification of *C. elegans* movement in response to genetic and chemical perturbations"**

## Overview
The files here should be sufficient to reproduce the data acquisition and analysis pipeline described in our paper, used in conjunction with several other packages of freely-available software.

The files are:


| File        | Description     |
| ------------- |:-------------| 
| NIS_elements_example_script.xml     | An example microscope control macro for use in Nikon NIS elements sortware|
| export_nd2.py      | Custom python script to extract individual 8-bit TIFF images from Nikon ND2 files     | 
| quantify_movement.py | Custom python script to analyse a set of 8-bit image files from an experiment, return mobility scores     |
| quantify_movement_adult.py | As above but tuned for larger, adult worms. Ignores eggs in the well|
| example_levamisole_data.npy| numpy array containing sample FMS data for a range of levamisole concentrations|
| levamisole_analysis.ipynb  | An example jupyter (formerly ipython notebook) file illustrating normalization and plotting of data|

Required third-party software:
1. Python 2.7
- numpy
- scipy
- matplotlib
- scikit-image
2. ImageMagick (for export_nd2.py): https://www.imagemagick.org/script/index.php
3. bfconvert: http://www.openmicroscopy.org/site/support/bio-formats5.4/users/comlinetools/
4. Jupyter: http://jupyter.org/


## Example Data
A set of example images is available at https://osf.io/p372e/

Running quantify_movement.py on the example images should recreate the fractional mobility score data in `example_levamisole_data.npy`

An example jupyter notebook, `levamisole_analysis.ipynb` (nbviewer link) illustrates the normalization of data and plotting procedure dose-response curves and time-response curves, using the data in `example_levamisole_data.npy`. This notebook can be viewed online at QQQQQQQQQQQQQQQQQQQQQQQ
