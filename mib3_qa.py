import shutil
import os
from os.path import isfile, join
from os import listdir
#import pandas as pd


lan_list = ['ITI', 'GED', 'DUN', 'SPE', 'FRF', 'ENG',  'SWS', 'ENU', 'FRC', 'SPM', 'KOK', 'JPJ', 'MNC', 'MNT', 'CAH', 'TRT','NON','RUR','PLP','CZC','PTP','PTB']
#spec_lan_list = ['ITI', 'GED', 'DUN', 'SPE', 'FRF', 'ENG',  'SWS', 'ENU', 'FRC', 'SPM', 'KOK', 'JPJ', 'MNC', 'MNT', 'CAH', 'TRT', 'NON']
work_path = os.getcwd()

#test_case_folder = 'k:\\358471_AudiCRQ_distance_units\\MIB3_QA\\testcases'
test_case_folder = 'testcase'

file_list = [f for f in listdir(test_case_folder) if isfile(join(test_case_folder,f)) ]

os.chdir(work_path)
for lan in lan_list:
    lan_test_path = lan
    if len(listdir(lan) ) == 0:
        for f in file_list:
            n_list = f.split('_')
            n_list[1] = lan
            new_name = '_'.join(n_list)
            o_path = test_case_folder + '\\' + f
            n_path = work_path + '\\'+ lan + '\\'  + new_name
            shutil.copyfile(o_path, n_path)

#creat the testcases folder
'''
for lan in lan_list:
    os.chdir(work_path)
    lan_test_path = lan 
    os.makedirs(lan_test_path)
'''



#copy the test case files to the according language folder
'''
for f in file_list:
    lan_tag = f.split('_')[1]
    print lan_tag
    o_path = test_case_folder + '\\' + f
                #n_name = id_name + '.' + o_name[1]
                # shutil.move('C:/Users/xiaoxinsoso/Desktop/aaa', 'C:/Users/xiaoxinsoso/Desktop/bbb') 
    n_path = work_path + '\\'+ lan_tag + '\\'  + f
                
                #n_path = "\\\\aac-srvjenkins01\DATA\p4projects\\autops_mib2_speechoutput_main-mib2plus\PAG\\tts_regression\\frf_monique" + "\\" + n_name
    shutil.copyfile(o_path, n_path)
'''
#adapt and copy the xlsx files
#df = pd.read_excel('CRQ-183_LAN.xlsx')

'''
for lan in lan_list:
    df = pd.read_excel('CRQ-183_LAN.xlsx')
    print(lan)
    df['File'] = df['File'].str.replace('RUR',lan)
    excel_path = work_path + '\\'+ lan+ '\\'+ 'CRQ-183_'+ lan +'.xlsx'
    df.to_excel(excel_path,index=False, engine='xlsxwriter')
'''
