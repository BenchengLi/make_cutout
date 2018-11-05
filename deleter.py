import pandas as pd
from os import walk
import shutil

dir_list=[]
dele=''

for (dirpath, dirnames, filenames) in walk('./'):
    dir_list.append(filenames)
for x in dir_list[0]:
    if '.png' in x:
        shutil.move(x, 'A/'+x)
