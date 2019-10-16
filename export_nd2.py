#!/usr/bin/python

##############################################################################
# export_nd2.py
#
# Requires bftools and imagemagick
# Converts a Nikon image stack format *.nd2 file from NIS Elements to 
# constituent TIF files, converts these files to 8-bit TIF and renames to
# include coordinates of the microtitre plate well.
# Note that the path to bftools (line 64) will depend on your installation
#
##############################################################################
import subprocess
import os 

def get_row(img_number,rows,cols):
    row_dict = {0:'A', 1:'B', 2:'C', 3:'D', 
                4:'E', 5:'F', 6:'G', 7:'H'}
    # use integer division to get key to row_dict
    # subtract one to count from zero
    # there are two images per well * 12 wells per row
    # so 24 images in each row.
    row_key = int((int(img_number) - 1) / (2*cols))
    row = row_dict[row_key]
    return row

def get_column(img_number,rows,cols):
    # 3 images per well
    well_number = int(1 + (int(img_number) - 1) / 2)
    if well_number in list(range((cols+1),(cols*2+1))) + list(range((cols*3+1),(cols*4+1))) + \
                      list(range((cols*5+1),(cols*6+1))) + list(range((cols*7+1),(cols*8+1))):
        # These rows were imaged in reverse order,
        # so calculate column position then reverse it
        well_number = int((well_number + (rows*cols-1)) % cols)
        well_number = int(cols- well_number)
    else:
        well_number = int(1+ (well_number + (rows*cols-1)) % cols)
    return str(well_number)

def get_new_filename(filename,rows,cols):    
    file_details = filename[:-4].split('_')
    img_number = int(file_details[-1][1:]) + 1
    row = get_row(img_number,rows,cols)
    col = get_column(img_number,rows,cols)
    coords = row + col
    rep_number = 1 + (int(img_number) - 1) % 2
    if rep_number == 1:
        rep = 'a'
    elif rep_number == 2:
        rep = 'b'
    print (coords, rep)
    new_filename = '_'.join(file_details[:-1]) \
                + '_' + coords + '_' + rep +'.tif'
    return new_filename

##########


def export_file(filename,b_dir,rows,cols):
    nd_file = filename+'.nd2'
    nd_path = b_dir+'Images/'
    export_path = nd_path
    
    bf_call = '/Applications/bftools/bfconvert ' + nd_path + nd_file +  ' '+ export_path + nd_file[:-4] + '_T%t_M%s.tif'
    subprocess.call(bf_call, shell = True)
    
    t_list = []
    for filename in os.listdir(export_path):
        if not filename.endswith('.tif'):
            continue
        print("tif:", filename)
        t_point = filename.split('_')[-2]
        if t_point not in t_list:
            print (t_point)
            os.mkdir(export_path + t_point)
            os.mkdir(export_path + t_point + '/redgreen')
            t_list.append(t_point)
        new_filename = get_new_filename(filename,rows,cols)
        im_call = '/opt/local/bin/convert ' + export_path + filename + \
                ' -auto-level -depth 8 ' + \
                export_path + t_point + '/' + new_filename
        subprocess.call(im_call, shell=True)
        os.remove(export_path + filename)
    
    

