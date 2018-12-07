# IPython
from IPython.core.interactiveshell import InteractiveShell
InteractiveShell.ast_node_interactivity = "all"
from IPython import display

from scipy.misc import imshow, toimage, imsave, imread
import pandas as pd
import numpy as np
import os
import shutil
import time
import gc
import glob
import matplotlib as plt
from matplotlib import pyplot

# AstroPy
from astropy import units as u
from astropy.io import fits
from astropy.wcs import WCS
from astropy.coordinates import SkyCoord, Angle
from astropy.nddata import Cutout2D

# My parameters
from make_cutout_para import prep

start_time = time.time()

class FITS():
    def __init__(self, fits_dir, band = None):
        self.dir = fits_dir
        self.band = band
        self.file = fits.open(fits_dir)
        self.data = self.file[0].data
        self.wcs  = WCS(self.file[0].header)
        self.dim  = self.data.shape


    def cutout(self, pos = (50, 50), size = (64, 64), save_to_dir = None, scale_func = None):
        # Crop
        cutout = Cutout2D(
            data=self.data,
            position = pos, #SkyCoord(row['ra'], row['dec'], unit="deg", frame="fk5"),
            size = size,
            wcs = self.wcs)

        if scale_func is None:
            scale_func = lambda x:x

        output, check_nan, p_high = scale_func(cutout.data)

        if np.isnan(check_nan) == False:

            check_nan = 0
            # Determine file extension
            ext = save_to_dir.split('.')[-1]

            if ext == 'fits':
                # Create a new fits object and add cutout data
                new_file        = self.file # fits.PrimaryHDU()
                new_file[0].data   = output

                # Add coord info to the header
                new_coords      = cutout.wcs
                # Update new FITS coords
                new_file[0].header.update(new_coords.to_header())

                # Save the new fits file
                new_file.writeto(save_to_dir)

            elif ext in ('jpeg', 'jpg', 'png'):
                imsave(save_to_dir, output)

            else:
                raise Exception('The file extension must be one of the following: fits, jpeg, jpg, png. "{}" was given instead.'.format(ext))
        else:
            check_nan = 1

        return output, check_nan, p_high

    def get_boundary(self, stride = 16,):
        # get the boundary for x and y, return two lists
        x_list=[]
        y_list=[]

        x_num = self.dim[1]
        y_num = self.dim[0]

        for n in range(int( x_num/stride ) + 1):
            if x_num-n>0.5*stride:
                x_list.append(int(n*stride))
        for n in range(int( y_num/stride ) + 1):
            if y_num-n>0.5*stride:
                y_list.append(int(n*stride))

        return x_list, y_list


def percentile_normalization(data, percentile_low = 1.5, percentile_high = 1.5, p_low_feed = None, p_high_feed = None, scale_coef = 1):

    p_low  = np.percentile(data, percentile_low)
    p_high = np.percentile(data, 100 - percentile_high)

    # Artificially set p_low and p_high
    if p_low_feed:
        p_low = p_low_feed

    if p_high_feed:
        p_high = p_high_feed

    # Bound values between q_min and q_max
    normalized = np.clip(data, p_low, p_high)
    # Shift the zero to prevent negative vlaues
    normalized = normalized - np.min(normalized)
    # Normalize so the max is 1
    normalized /= np.max(normalized)
    # Scale
    normalized *= scale_coef

    '''
    The line below is added by Ben in order to check if most of the data entries are NaN.
    '''

    check_nan = np.percentile(normalized, 70)

    return normalized, check_nan, p_high


def count(n):
    # define a function to add accumulatively
    n = n + 1
    return n


def main():
    # main function
    s,data_dir,save_dir = prep()
    df1_list = []
    df2_list = []
    i = 0
    n = 0

    # get a list of all FITS files under the desired directory
    name_list = glob.glob(data_dir+'/**/*.fits', recursive= True)
    num_fits = len(name_list)
    for each_fits in name_list:
        print ('Working on '+each_fits+' '+str(n+1)+'/'+str(num_fits))

        # build dataframe1
        cube1=[each_fits,np.int32(n)]
        df1_list.append(cube1)

        # input FITS
        file = FITS(each_fits)
        # get the x and y lists
        x_list, y_list = file.get_boundary(stride = s)
        # define scale_func
        sf = lambda data: percentile_normalization(data, percentile_high=1., percentile_low=30)
        # loop over x and y list
        for y in y_list:
            for x in x_list:
                image_id = '{:010d}'.format(i)+'.jpeg'
                fits_id = '{:010d}'.format(n)

                # make seperate dirs for each FITS file
                if os.path.isdir(save_dir+'/'+fits_id) == False:
                    os.mkdir(save_dir+'/'+fits_id)

                # save arrays as images
                data, check_nan, p_high = file.cutout(pos=(x, y), save_to_dir=str(save_dir+'/'+fits_id+'/'+image_id) ,scale_func=sf)
                # check if the data is full of NaN
                if check_nan == 0:

                    # get ra, dec according to wcs and build df2
                    ra, dec=file.wcs.all_pix2world(x,y,0)
                    cube2=[np.int32(i),np.float32(ra),np.float32(dec),np.int32(x),np.int32(y),np.float32(p_high),np.int32(n)]
                    df2_list.append(cube2)
                    # accumulatively add 1 to file_id
                    i = count(i)

        # save dataframe2
        df2=pd.DataFrame(data=df2_list,columns=['file_id','RA','Dec','x_pix','y_pix','q_max','dir_id'])
        df2.to_pickle(save_dir+'/'+fits_id+'/big_map.pkl')
        print(df2)


        # after each loop is done, clear df2
        df2_list.clear()
        print (each_fits+' done! '+str(n+1)+'/'+str(num_fits))
        n = count(n)


    # save dataframe1
    df1=pd.DataFrame(data=df1_list,columns=['parent directory','dir_id'])
    df1.to_pickle(save_dir+"/directory_map.pkl")
    print (df1)
    # print how much time used
    print("--- %s seconds ---" % (time.time() - start_time))



if __name__ == '__main__':

    main()
