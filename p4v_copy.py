#!/usr/bin/env python
# -*- coding: utf-8 -*-


import codecs
import os
import pandas as pd
import re
import shutil

from os import listdir
from os.path import isfile, join
from shutil import copyfile, move, copy
ex_list = ['1.tso','wav']

 


work_path = os.getcwd()
#time_stamp = '181119-154622'
# path = "\\\\aac-srvjenkins01\DATA\p4projects\\autops_mib2_speechoutput_main-mib2plus\PAG\\tts_regression" + "\\" +  lan_code + "_" + voice

csv_files = [ f for f in listdir(work_path) if isfile(join(work_path,f)) and f.split('.', 1)[1] == 'csv' ]
print(csv_files)


def get_lan_id_list(f):
    f_name = f.split('.', 1)[0]
    lan = f_name.split('_')[0]
    voice = f_name.split('_')[1]



    result_file = work_path + '\\' + f
    print(result_file)
    df = pd.read_csv(result_file, header=0, delimiter = ';')
    df = df.set_index(['Result'])
    id_list = []
    id_c= df.loc['FAIL']['ID']
    if isinstance(id_c,str):
        id_list.append(id_c)
    else:
        id_list = id_c.tolist()
    



    return f_name, id_list


def extract_file(id_name, f_name, j_path, copy_path):
    print(f_name)
    '''CHANGE THE PATH HERE'''
    #path = "\\\\ac-srvfile01\SpeechOutput2\Jenkins\p4projects\\autops_mib3_audi_speechoutput_main\AUDI_high" + "\\"+ f_name+ "\_testing\_spec_implicit_wav\_test_data"
    #print path
    #path = "\\\\ac-srvfile01\\SpeechOutput2\\Jenkins\\p4projects\\autops_mib3_audi_speechoutput_main\\AUDI_high\\tts_regression" + "\\"+ f_name
    os.chdir(j_path)
    onlyfiles = [ f for f in listdir(j_path) if isfile(join(j_path,f))]
    #id_name_fg = id_name +'_'+ time_stamp
    print(id_name)
    for o in onlyfiles:
        o_name = o.split('.', 1)
        if o_name[0] == id_name:
            if o_name[1] in ex_list:
                os.chdir(j_path)
                o_path = j_path + '\\' + o
                #n_name = id_name + '.' + o_name[1]
                # shutil.move('C:/Users/xiaoxinsoso/Desktop/aaa', 'C:/Users/xiaoxinsoso/Desktop/bbb') 
                n_path = copy_path + "\\" + o
                
                #n_path = "\\\\aac-srvjenkins01\DATA\p4projects\\autops_mib2_speechoutput_main-mib2plus\PAG\\tts_regression\\frf_monique" + "\\" + n_name
                shutil.copyfile(o_path, n_path)




for f in csv_files:
    print(f)
    get_lan_id_list(f)
    f_name, id_list = get_lan_id_list(f)
    copy_path_old = work_path + "\\" +  f_name
    copy_path_new = work_path + "\\" +  f_name +  "_new_baseline"
    j_path_old =  "\\\\ac-srvfile01\\SpeechOutput2\\Jenkins\\p4projects\\autops_mib3_audi_speechoutput_main\\AUDI_high\\tts_regression" + "\\"+ f_name 
    j_path_new =  "\\\\ac-srvfile01\\SpeechOutput2\\Jenkins\\p4projects\\autops_mib3_audi_speechoutput_main\\AUDI_high\\tts_regression" + "\\"+ f_name + "\\_test_data"
    #os.mkdir(copy_path_old)
    os.mkdir(copy_path_new)
    for id_name in id_list:
        #extract_file(id_name,f,j_path_old,copy_path_old)
        extract_file(id_name,f,j_path_new,copy_path_new)
    
print('done')

   # extract_file(i)



