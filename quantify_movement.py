#!/usr/bin/python

import numpy as np
from scipy import ndimage, misc
import os
from matplotlib import pyplot as plt
from PIL import Image
from skimage.filter import threshold_adaptive

###############################################################################

def tabulate_data(data):
    table = ""
    for row in data:
        new_row = ''
        for number in row:
            new_row += str(number) + '\t'
        table += new_row +"\n"
    return table

###############################################################################

def draw_mask((a,b),r, img):
    '''
    create circular mask (True within
    circle), of radius r, centred on
    (row, col) = (a,b)
    '''
    y,x = np.ogrid[-a:1024-a, -b:1280-b]
    mask = x*x + y*y <= r*r
    img *= mask
    return img

def get_well_mask(sobel_ims, x_offset=5, y_offset=5):
    centre = (510, 630)
    well_mask = draw_mask(centre, 640, np.ones((1024, 1280)))
    return well_mask

###############################################################################
#
#   Image processing functions


def blur_gauss(images):
    blur_images = []
    for image in images:
        blur = ndimage.filters.gaussian_filter(image, 1.5)
        blur_images.append(blur)
    return blur_images

def run_sobel(images, sobel_c = 0):
    sobel_images = []
    for image in images:
        sx = ndimage.sobel(image, axis=0, mode='reflect', cval=sobel_c)
        sy = ndimage.sobel(image, axis=1, mode='reflect', cval=sobel_c)
        sob = np.hypot(sx, sy)
        sob = sob * 100 / sob.mean()
        sobel_images.append(sob)
    return sobel_images

def threshold_images(images, offset_arg):
    binary_masks = []
    for img in images:
        img = threshold_adaptive(img, 21, offset=-160)#img > threshold
        binary_masks.append(img)
    return binary_masks

###############################################################################


# setup and array sized as a 96-well plate

rows = ['A','B','C','D','E','F','G','H']
cols = range(1,13)

wells = [row+str(col) for row in rows for col in cols]

data = np.zeros((8,12,62))
for T in range(0,62):
    T = str(T)
    in_dir = '/path/to/experiment/directory/T' + T + '/'
    base_name =  'name_of_your_files_T' + str(T)
    masks = []
    #os.mkdir(in_dir +'redgreen/')
    for i, well in enumerate(wells):
        # convert row and column names into array indices
        arr_row = rows.index(well[0])
        arr_col = cols.index(int(well[1:]))

        # read in the 2 image files for the current well
        filename = base_name + '_' +  well + '_'
        img_a = misc.imread(in_dir + filename + 'a.tif', flatten=True)
        img_b = misc.imread(in_dir + filename + 'b.tif', flatten=True)
        
        # package images as a list for convenience
        images = [img_a, img_b]

        # gaussian blur images to ameliorate noise
        gauss = blur_gauss(images)
        # Find edges by Sobel filter
        sobs = run_sobel(gauss)
    # Build a mask for the sides of the well 
        well_mask = get_well_mask(sobs)
    # Threshold sobel images to bring up worms in binary mask
        masks = threshold_images(sobs, -150) 

    
        mask1 = masks[0].astype(int)
        mask2 = masks[1].astype(int)

        mask_frame1 = ndimage.morphology.binary_closing(mask1, iterations=2)
        mask_frame2 = ndimage.morphology.binary_closing(mask2, iterations=2) 

    # Find moving worms by difference of images
        img_a = gauss[0]
        img_b= gauss[1]
        moved_a_b = (abs(img_a - img_b)>6).astype(int)

 
        moving_img = mask_frame2 * moved_a_b * well_mask 
        still_img = mask_frame2 * np.logical_not(moving_img) * well_mask
    # construct red/green images:
        # make a blank array for the blue channel of RGB
        blue = np.zeros((1024,1280))
        # construct RGB image from red and green data and empty blue channel
        rgb_img = np.dstack((still_img, moving_img, blue))
        misc.imsave(in_dir+'redgreen/' + T +'_' + well + '_b.png', rgb_img)
    # calculate fractional mobility score
        moving = np.sum(moving_img)
        still = np.sum(still_img)
        score = float(moving) /(still+moving)
        data[arr_row, arr_col, int(T)] = score
# save data:
    outdir = '/'.join(in_dir.split('/')[:-2])
    outname = "_".join(base_name.split('_')[:-1])
    print str(T) + '\t' + outdir + '/' + outname
    np.save(outdir + '/' + outname + '.npy', data)
# uncomment these two lines to output data to screen in CSV format.
    #data = tabulate_data(data)
    #print data
