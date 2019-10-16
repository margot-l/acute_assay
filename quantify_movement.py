import numpy as np
from scipy import ndimage, misc
import os
#from matplotlib import pyplot as plt
from PIL import Image
from skimage.filters import threshold_local, threshold_otsu

###############################################################################
#
# Change me!

def tabulate_data(data):
    table = ""
    for row in data:
        new_row = ''
        for number in row:
            new_row += str(number) + '\t'
        table += new_row +"\n"
    return table



###############################################################################


def draw_mask(center,r, img):
    '''
    create circular mask (True within
    circle), of radius r, centred on
    (row, col) = (a,b)
    '''
    a = center[0]
    b = center[1]
    y,x = np.ogrid[-a:1024-a, -b:1280-b]
    mask = x*x + y*y <= r*r
    img *= mask
    return img

def get_well_mask(sobel_ims, x_offset=5, y_offset=5):
    masks = []
    for im in sobel_ims:
        t_hold = threshold_otsu(im)
        mask = im>t_hold
        cleaned = ndimage.morphology.binary_opening(mask, iterations=2)
        dilated = ndimage.morphology.binary_dilation(cleaned, iterations=6)
        masks.append(dilated)
    chord_mask = masks[0] * masks[1] 
    centre = (510, 630)
    well_mask = draw_mask(centre, 640, np.ones((1024, 1280)))
    return well_mask

###############################################################################

###############################################################################
#
#   Image processing functions

def norm_image(images):
    normed_images = []
    for img in images:
        norm = np.log(img)
        normed_images.append(norm)
    return normed_images

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
        img = img > threshold_local(img, 21, offset=-160)#img > threshold
        binary_masks.append(img)
    return binary_masks

###############################################################################

def quick_quant(fn,b_dir,r,c,tps):
    # setup and array sized as a 96-well plate
    
    rows = ['A','B','C','D','E','F','G','H'][0:r]
    cols = range(1,(c+1))
    
    wells = [row+str(col) for row in rows for col in cols]
    
    data = np.zeros((r,c,(tps+1)))
    for T in range((tps+1)):
        T = str(T)
        in_dir = b_dir+'Images/T' + T + '/'
        base_name =  fn+'_T' + T
        masks = []
    
        for i, well in enumerate(wells):
            # convert row and column names into array indices
            arr_row = rows.index(well[0])
            arr_col = cols.index(int(well[1:]))
    
            # read in the 3 image files for the current well
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
    
            blue = np.zeros((1024,1280))
    
            rgb_img = np.dstack((still_img, moving_img, blue))
    
            misc.imsave(in_dir+'redgreen/T' + T +'_' + well + '_b.png', rgb_img)
    
            moving = np.sum(moving_img)
            still = np.sum(still_img)
            score = float(moving) /(still+moving)
            data[arr_row, arr_col, int(T)] = score
        #data = tabulate_data(data)
        #print data
        np.save('/'.join(in_dir.split('/')[:-2])+ '/' + '_'.join(base_name.split('_')[:-1]) + '.npy', data)
        print ('_'.join(base_name.split('_')[:-1])+'_'+T)
