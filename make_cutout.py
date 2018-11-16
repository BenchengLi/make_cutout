from astropy.io import fits
from astropy.wcs import WCS
from astropy.nddata import Cutout2D
import numpy as np
import pandas as pd
from scipy.misc import imsave
from PIL import Image
from scipy.misc import imshow, toimage, imsave, imread
from IPython.core.interactiveshell import InteractiveShell
InteractiveShell.ast_node_interactivity = "all"
import os
from os import walk, path
import shutil
import pickle
import time
import gc

mypath=input('My path: ')
ra=input('Radius of cutout image: ')
scale=input('The scale(integer) of cutout: ')
strid=input('The stride: ')
start_time=time.time()
i=0
m=0
n=0
x=-1
df1_list=[]
df2_list=[]
name_list=[]
file_list=[]
sfile_list=[]
path_dict=dict()

def cutout(target,radius):
    global i
    global n
    global x
    global m
    try:
        file=fits.open(target,ignore_missing_end=True)
        file_data=file[0].data
        file_wcs=WCS(file[0].header)
        file_wcs.sip=None
        num=int(len(file_data))
        index_format='{:010d}'.format(n)
        try:
            os.mkdir('cutout/'+str(index_format))
        except:
            print('Folder '+str(index_format)+' already exists!')
        x=0
        y=0
    except:
        print('Cannot open '+str(target))
        x=-1
    while True:
        if x==-1:
            break
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
                data_std=np.std(data2)
                if data_std<1:
                    data_thre=np.percentile(data2,60)
                    data2=(data2-data_thre)*1/data_std+data_thre
                    data_max=np.percentile(data2,int(scale))
                data3=data2/data_max*255
                flat_data3=data3.ravel()
                data3_max=np.percentile(flat_data3,90)
                if np.isnan(data3_max)==False:
                    im=Image.fromarray(data3)
                    if im.mode != 'RGB':
                        im=im.convert('RGB')
                    image_name='{:010d}.jpeg'.format(i)
                    imsave(image_name,im)
                    ra, dec=file_wcs.all_pix2world(x,y,0)
                    cube2=[np.int32(i),np.float32(ra),np.float32(dec),np.int32(x),np.int32(y),np.float32(data_max),np.int32(n)]
                    df2_list.append(cube2)
                    shutil.move(image_name,'cutout/'+str(index_format))
                    i=i+1
                x=x+int(strid)
            except:
                x=x+int(strid)
        else:
            x=0
            y=y+int(strid)
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
    num_fits=len(name_list)
    for each_fits in path_dict:
        print ('Working on '+each_fits+' '+str(m+1)+'/'+str(num_fits))
        path=dirpath+'/'+each_fits
        cube1=[path,np.int32(n)]
        df1_list.append(cube1)
        cutout(path,ra)
        if x==-1:
            print(str(path)+' not working')
            df1_list.remove(cube1)
        else:
            index_format='{:010d}'.format(n)
            df2=pd.DataFrame(data=df2_list,columns=['file_id','RA','Dec','x_pix','y_pix','q_max','dir_id'])
            df2.to_pickle('./cutout/'+str(index_format)+'/big_map.pkl')
            print(df2)
            print (each_fits+' done! '+str(m+1)+'/'+str(num_fits))
            n=n+1
        m=m+1
        df2_list.clear()
        gc.collect()
    path_dict.clear()

df1=pd.DataFrame(data=df1_list,columns=['parent directory','dir_id'])
df1.to_pickle("./cutout/directory_map.pkl")
print (df1)
print("--- %s seconds ---" % (time.time() - start_time))

