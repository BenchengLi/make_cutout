from astropy.io import fits
from astropy.wcs import WCS
from astropy.nddata import Cutout2D
from astropy.coordinates import SkyCoord, Galactic,FK5
import numpy as np
import pandas as pd
from scipy.misc import imsave
from scipy.misc import toimage
import matplotlib.pyplot as plt
import astropy.units as u
from PIL import Image
from scipy.misc import imshow, toimage, imsave, imread
from IPython.core.interactiveshell import InteractiveShell
InteractiveShell.ast_node_interactivity = "all"
from IPython import display
import os
from os import walk
import shutil

cutout_list=[]
mypath=input('My path: ')
ra=input('Radius of cutout image: ')
scale=input('The scale(integer) of cutout: ')

def cutout(target,radius):
    file=fits.open(target)
    file_data=file[0].data
    file_wcs=WCS(file[0].header)
    ra,dec=file_wcs.all_pix2world([0],[0],1)
    file_wcs.sip=None
    num=int(len(file_data))
    x=0
    y=0
    while True:
        if x <= num:
            try:
                cutout=Cutout2D(data=file_data, position=(x,y), size=int(radius), wcs=file_wcs,mode='partial')
                data=cutout.data
                flat_data=data.ravel()
                flat_data = flat_data[np.logical_not(np.isnan(flat_data))]
                data_min=np.percentile(flat_data,100-int(scale))
                data_max=np.percentile(flat_data,int(scale))
                if data_min < 0:
                    #for b in data:
                        #for i,c in enumerate(b):
                            #if np.isnan(c)==True:
                                #b[i]=data_min
                    data=data-data_min
                    data1=np.maximum(data,0)
                    data2=np.minimum(data1,data_max)
                    data3=data2/(data_max)*255
                else:
                    data1=np.maximum(data,data_min)
                    data2=np.minimum(data1,data_max)
                    data3=data2/data_max*255
                #print (data3)
                im=Image.fromarray(data3)
                if im.mode != 'RGB':
                    im=im.convert('RGB')
                fits_name='cutout_'+str(x)+'_'+str(y)+'.png'
                imsave(fits_name,im)
                cutout_list.append(fits_name)
                x=x+int(radius)
            except:
                x=x+int(radius)
        else:
            x=0
            y=y+int(radius)
        if y>num:
            break

file_list=[]
sfile_list=[]
dir_list=[]
path_dict=dict()

for (dirpath, dirnames, filenames) in walk(mypath):
    dir_list.append(dirpath)
for mysondir in dir_list:
    sdir=mysondir
    for (sdirpath, sdirnames, sfilenames) in walk(sdir):
        sfile_list.append(sfilenames)
    for sfile in sfile_list[0]:
        if '.fits' in sfile:
            path_dict[sfile]=sdir
    for each_fits in path_dict:
        each_dir=each_fits[:-5]
        if each_dir not in file_list:
            if not os.path.exists(sdir+'/'+each_dir):
                os.mkdir(sdir+'/'+each_dir)
            path=sdir+'/'+each_fits
            cutout(path,ra)
            shutil.move(sdir+'/'+each_fits,sdir+'/'+each_dir+'/'+each_fits)
            print(cutout_list)
            for cutouts in cutout_list:
                cutouts1=each_dir+'_'+cutouts
                shutil.move(cutouts,sdir+'/'+each_dir+'/'+cutouts1)
            file_list.append(each_dir)
            cutout_list.clear()
    path_dict.clear()
    sfile_list.clear()
