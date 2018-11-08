import pandas as pd
from os import walk

mypath=input('My path: ')

df_list=[]
file_list=[]
sfile_list=[]
dir_list=[]
path_dict=dict()
path_dict1=dict()
cutout_list=[]

for (dirpath, dirnames, filenames) in walk(mypath):
    sdir=dirpath
    for (sdirpath, sdirnames, sfilenames) in walk(sdir):
        sfile_list.append(sfilenames)
    for sfile in sfile_list[0]:
        if '.png' in sfile:
            path_dict[sfile]=sdir
    for each_fits in path_dict:
        each_dir=each_fits[:-5]
        if each_dir not in file_list:
            path=sdir
        fits_dir=sdir
        path_dict1[each_fits]=fits_dir
        file_list.append(each_dir)
        cutout_list.clear()
    path_dict.clear()
    sfile_list.clear()

for key,val in path_dict1.items():
    cube=[val,key]
    df_list.append(cube)

# Create pandas dataframe
df_dir=pd.DataFrame(data=df_list,columns=['parent_dir', 'fits_name'])
df_dir.to_pickle("./directory_map.pkl")
print (df_dir)
