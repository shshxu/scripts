import shutil
import os
from os.path import isfile, join
from os import listdir

lan='hei'
language = 'hebrew'
voice='carmit'
ref_vop='2.0.0'
tar_vop='2.0.1-SNAPSHOT'
test_path = 'E:\Users\Shanshan.Xu\\tests'
ex = '.utf8'


current_path = os.getcwd()
#VOP_RT_ref-e-h-2-0-1_target-e-h-2-0-2-snapshot
work_path = lan+'\\'+ voice + '\\VOP_RT_ref-e-h-' + ref_vop.replace('.','-') + '_target-e-h-' +tar_vop.replace('.','-')
text_path = test_path + '\\' + work_path +  '\\input_text'
wav_path = test_path + '\\' + work_path +  '\\' 



#current_path = os.getcwd()

work_path = 'E:\Users\Shanshan.Xu\stages'+'\\'+lan+'\\'+ voice + '\\MS-VOP-RT_' + ref_vop.strip('.') + '_' +tar_vop.strip('.')

def stage():
    os.system("stage versions.txt .")

def rt_procedures(vop):
    vop_nr = vop.replace('.', '')
    vop_folder= work_path + '\\' + vop_nr
    shutil.rmtree(vop_folder, ignore_errors=True)
    if 'ref' in vop:
        wav_vop_path = wav_path + 'reference_pcm'
    else:
        wav_vop_path = wav_path + 'target_pcm'
    os.makedirs(vop_folder)
    with open(current_path+'\\txt2wav_vecmdline_ldm.bat','r') as f:
        lines = f.readlines()
        lines = [line.replace('change_stage_path',vop_folder) for line in lines]
        lines = [line.replace('change_txt_path',text_path) for line in lines]
        shutil.rmtree(text_path, ignore_errors=True)
        os.makedirs(text_path)
        lines = [line.replace('change_wav_path',wav_vop_path) for line in lines]
        os.makedirs(wav_vop_path)
        lines = [line.replace('change_language',language) for line in lines]
        lines = [line.replace('change_voice',voice) for line in lines]
        lines = [line.replace('.txt',ex) for line in lines]
    f.close()
    batch_file = work_path + '\\txt2wav_' + vop_nr + '.bat'
    b = open(batch_file, 'w+')
    b.writelines(lines)
    b.close()
    with open('versions.txt') as f:
        lines = f.readlines()
        lines = [line.replace('plp#ewa',lan+'#'+voice) for line in lines]
        if 'SNAPSHOT' in vop:
            lines = [line.replace('1.1.6-SNAPSHOT',vop) for line in lines]
        else:
            lines = [line.replace('1.1.6-SNAPSHOT',vop) for line in lines]
            lines = [line.replace('vop#','vop-bin#') for line in lines]
            lines = [line.replace('22#embedded-high','embedded-high') for line in lines]

    f.close()
    version_file = vop_folder + '\\versions.txt'
    o = open(version_file, 'w+')
    o.writelines(lines)
    o.close()
#download stages
    #os.chdir(vop_folder)
    #stage()



rt_procedures(ref_vop)

rt_procedures(tar_vop)

