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
n=0
df1_list=[]
df2_list=[]
df_list=[]
name_list=[]
name_list1=[]
fits_list=[]
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
    index=fits_list.index(target)
    index_format='{:010d}'.format(index)
    try:
        os.mkdir('cutout/'+str(index_format))
    except:
        print('Folder '+str(index_format)+' already exists!')
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
                image_name='{:010d}.jpeg'.format(i)
                imsave(image_name,im)
                ra, dec=file_wcs.all_pix2world(x,y,0)
                cube2=[int(i),float(ra),float(dec),int(x),int(y),int(index)]
                df2_list.append(cube2)
                cutout_list.append(image_name)
                shutil.move(image_name,'cutout/'+str(index_format))
                x=x+500
                i=i+1
            except:
                x=x+500
        else:
            x=0
            y=y+500
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
            if path not in fits_list:
                cube1=[path,int(n)]
                df1_list.append(cube1)
                fits_list.append(path)
            cutout(path,ra)
            index=fits_list.index(path)
            index_format='{:010d}'.format(index)
            df2=pd.DataFrame(data=df2_list,columns=['file_id','RA','Dec','x_pix','y_pix','dir_id'])
            df2.to_pickle('./cutout/'+str(index_format)+'/big_map.pkl')
            print(df2)
            file_list.append(each_dir)
            cutout_list.clear()
            print (each_fits+' done! '+str(count)+'/'+str(num_fits))
            count=count+1
            n=n+1
            df2_list.clear()
    path_dict.clear()
    sfile_list.clear()

df1=pd.DataFrame(data=df1_list,columns=['parent directory','dir_id'])
df1.to_pickle("./cutout/directory_map.pkl")
print (df1)
