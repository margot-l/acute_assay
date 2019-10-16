# -*- coding: utf-8 -*-
import os
#os.chdir('/acute-assay')
import export_nd2 as ex
import quantify_movement as qq

c_dir='/Users/margotl/Documents/GitHub/acute_assay/'
d=['']
fname=["N2old_N2June_idh-2_idhg-2_KCN_03oct19_01"]

rows=8
cols=12
tps=[19]

#####

for n,f in enumerate(fname):

    d_dir=c_dir+d[n]
    i_dir=d_dir+'Images/'
    dst_dir=i_dir+f+'.nd2'
    
    if not os.path.exists(i_dir):
        os.makedirs(i_dir)
    
    ex.export_file(f,d_dir,rows,cols) 
    
    tp=tps[n]-1    
    qq.quick_quant(f,d_dir,rows,cols,tp)
    
    src=d_dir+'Images/'+f+'.npy'
    dst_dir2=d_dir+f+'.npy'