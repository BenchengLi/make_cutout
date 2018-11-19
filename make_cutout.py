from astropy.io import fits
from astropy.wcs import WCS
from astropy.nddata import Cutout2D
import numpy as np
from numpy import ma, ndarray
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
from make_cutout_para import prep

start_time=time.time()
i,s,m,n,mypath,ra,scale,df1_list,df2_list,name_list,file_list,sfile_list,path_dict = prep()

#Open a FITS file, read its data, create its corresponding folder and get the size of x and y pix
def open_fits(target):
    global file_data, file_wcs, x_size, y_size
    file=fits.open(target,ignore_missing_end=True)
    file_data=file[0].data
    file_wcs=WCS(file[0].header)
    file_wcs.sip=None
    x_size=int(np.ma.size(file_data,1))
    y_size=int(np.ma.size(file_data,0))

# generate a list for all x and y values
def get_boundary(num1,num2):
    global x_list, y_list
    x_list=[]
    y_list=[]
    for n in range(int(num1/s)+1):
        if num1-n>0.5*s:
            x_list.append(int(n*s))
    for n in range(int(num2/s)+1):
        if num2-n>0.5*s:
            y_list.append(int(n*s))

#Prepare the data for cutout process
def normal_data(data):
    global data3,data_max,nan_count,data3_max
    flat_data=np.ravel(data)
    data_max=np.percentile(flat_data,int(scale))
    data1=np.maximum(data,0)
    data2=np.minimum(data1, data_max)
    data3=data2/data_max*255
    flat_data3=np.ravel(data3)
    # Check if more than 30% of pix value is NaN (Directly count NaN in ndarray is not easy...)
    data3_max=np.percentile(flat_data3,30)

#save data array into jpeg images and build up our big_map
def save(data):
    im=Image.fromarray(data)
    if im.mode != 'RGB':
        im=im.convert('RGB')
    image_name='{:010d}.jpeg'.format(i)
    imsave(image_name,im)
    ra, dec=file_wcs.all_pix2world(x,y,0)
    cube2=[np.int32(i),np.float32(ra),np.float32(dec),np.int32(x),np.int32(y),np.float32(data_max),np.int32(n)]
    df2_list.append(cube2)
    shutil.move(image_name,'cutout/'+str(index_format))

#cut FITS file
def cutout(target,radius):
    global i, m,n,x,y,index_format
    open_fits(target)
    get_boundary(x_size,y_size)
    index_format='{:010d}'.format(n)
    folder_name='cutout/'+str(index_format)
    if os.path.exists(folder_name)==False:
        os.mkdir(folder_name)
    else:
        print(folder_name+' already exists!')
    # loop
    for y in y_list:
        for x in x_list:
            cutout=Cutout2D(data=file_data, position=(x,y), size=int(radius), wcs=file_wcs,mode='partial')
            data=cutout.data
            normal_data(data)
            if np.isnan(data3_max)==False:
                save(data3)
                i=i+1


# Scan through the directory looking for FITS file
for (dirpath, dirnames, filenames) in walk(mypath):
    for sfile in filenames:
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

# build up our directory_map
df1=pd.DataFrame(data=df1_list,columns=['parent directory','dir_id'])
df1.to_pickle("./cutout/directory_map.pkl")
print (df1)
print("--- %s seconds ---" % (time.time() - start_time))
