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
from os import walk, path
import shutil
import pickle

cutout_list=[]
mypath=input('My path: ')
ra=input('Radius of cutout image: ')
scale=input('The scale(integer) of cutout: ')
i=0
df1_list=[]
df2_list=[]
df_list=[]
name_list=[]
name_list1=[]
file_list=[]
sfile_list=[]
dir_list=[]
path_dict=dict()
count=1

def cutout(target,radius):
    global i
    file=fits.open(target,ignore_missing_end=True)
    file_data=file[0].data
    file_wcs=WCS(file[0].header)
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
                    data=data-data_min
                    data1=np.maximum(data,0)
                    data2=np.minimum(data1,data_max)
                    data3=data2/(data_max)*255
                else:
                    data1=np.maximum(data,data_min)
                    data2=np.minimum(data1,data_max)
                    data3=data2/data_max*255
                im=Image.fromarray(data3)
                if im.mode != 'RGB':
                    im=im.convert('RGB')
                png_name='{:010d}.png'.format(i)
                index='{:010d}'.format(i)
                imsave(png_name,im)
                parent_fits=target
                df1_list.append(parent_fits)
                ra, dec=file_wcs.all_pix2world(x,y,0)
                cube1=[ra,dec,x,y,index]
                df2_list.append(cube1)
                cutout_list.append(png_name)
                shutil.move(png_name,'cutout')
                x=x+16
                i=i+1
            except:
                x=x+16
        else:
            x=0
            y=y+16
        if y>num:
            break

for (dirpath, dirnames, filenames) in walk(mypath):
    for (sdirpath, sdirnames, sfilenames) in walk(dirpath):
        sfile_list=sfilenames
        break
    for sfile in sfile_list:
        if '.fits' in sfile:
            name_list.append(sfile)
            path_dict[sfile]=dirpath
            vfile=sfile[:-5]
            for x in dir_list:
                if vfile in x:
                    del path_dict[sfile]
                    name_list.remove(sfile)
    num_fits=len(name_list)
    for each_fits in path_dict:
        each_dir=each_fits[:-5]
        print ('Working on '+each_fits+' '+str(count)+'/'+str(num_fits))
        if each_dir not in file_list:
            path=dirpath+'/'+each_fits
            cutout(path,ra)
            file_list.append(each_dir)
            cutout_list.clear()
            print (each_fits+' done! '+str(count)+'/'+str(num_fits))
            count=count+1
    path_dict.clear()
    sfile_list.clear()

df1=pd.DataFrame(data=df1_list,columns=['parent directory'])
df1.to_pickle("./directory_map.pkl")
print (df1)

df2=pd.DataFrame(data=df2_list,columns=['RA','Dec','x_pix','y_pix','dir_id'])
df2.to_pickle("./big_map.pkl")
print (df2)
