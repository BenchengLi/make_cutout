import os
from os import walk

file_list=[]
dir_list=[]
target_list=[]
fits_list=[]
path_dict=dict()

for (dirpath, dirnames, filenames) in walk('./'):
    dir_list.append(dirpath)
    file_list.append(filenames)
for x in file_list:
    for y in x:
        if '.fits' in y:
            fits_list.append(y)
for path in dir_list:
    if 'mosaic' in path:
        target_list.append(path)
for target in target_list:
    target=target[2:]
    for y in fits_list:
        if target in y:
            path_dict[target]=y
    print ('mv '+ target +'/'+path_dict.get(target)+' ./')
    print('rm -r '+target)
