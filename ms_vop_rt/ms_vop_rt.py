import shutil, os, subprocess, time, filecmp
#import pandas as pd


lan=raw_input('Please enter 3 letter language token (e.g. PTP): ').upper()
voice=raw_input('Please enter the voice name (e.g. Petra): ').lower()
ref_vop=raw_input('Please enter the reference vop version(e.g. 1.0.1): ')
tar_vop=raw_input('Please enter the target vop version(e.g. 1.0.2-SNAPSHOT): ')
extra_test= raw_input('Please enter the extra test suite(e.g. inpENG, or x if no extra suite needed): ')

if lan == 'testtesttest':
    lan='ROR'
    language = 'romanian'
    voice='ioana'
    ref_vop='2.0.0'
    tar_vop='2.0.1-SNAPSHOT'
    #extra_test='inpENG'



langmap={}
with open('E:/Users/Andreas.Windmann/scripts/langmap.txt') as f:
    for line in f:
        rline=line.replace('\n','')
        
        (key, val) = rline.split('\t')
        langmap[key] = val

language = langmap[lan]    
current_path = os.getcwd()
#VOP_RT_ref-e-h-1-1-5_target-e-h-1-1-6-snapshot
rt_name = 'VOP_RT_ref-e-h-' + ref_vop.replace('.','-') + '_target-e-h-' +tar_vop.replace('.','-')
#work_path = os.path.abspath('../../stages')+'\\'+lan+'\\'+ voice +'\\'+rt_name
test_path = 'E:\Users\SpO_MS_VOP'+'\\'+lan+'\\'+ voice 
ex = '.utf8'
text_path = test_path + '\\' + rt_name +  '\\input_text'
wav_path = test_path + '\\' + rt_name +  '\\' 
verions_path = wav_path + 'versions'
extra_path = 'E:\Users\SpO_MS_VOP\_extra_test' + '\\' + extra_test
#E:\Users\SpO_MS_VOP\_extra_test\inpENG
os.makedirs(verions_path)

#fetch test suite:
suite_path = 'E:\Users\SpO_MS_VOP'+'\\'+lan+'\\'+'_test_suite'
if os.path.exists(suite_path):
    print 'test suite found'
    n = len(os.listdir(suite_path))
    text_path = suite_path
else:
    print '*** No test suites found, please fetch the test suite manually. ***'
    shutil.rmtree(text_path, ignore_errors=True)
    os.makedirs(text_path)

#work_path = 'E:\Users\Shanshan.Xu\stages'+'\\'+lan+'\\'+ voice + '\\MS-VOP-RT_' + ref_vop.strip('.') + '_' +tar_vop.strip('.')



def rt_procedures(vop):
    vop_nr = vop.replace('.', '')
    if 'SNAPSHOT' in vop:
        wav_vop_path = wav_path + 'target_pcm'
        vop_folder= 'E:\Users\SpO_MS_VOP\_tar'
    else:
        wav_vop_path = wav_path + 'reference_pcm'
        vop_folder = 'E:\Users\SpO_MS_VOP\_ref'
    #os.makedirs(vop_folder)



###deleting old vops if exists
    if os.path.exists(vop_folder+ '\languages' + '\\' + lan.lower()):
        shutil.rmtree(vop_folder+ '\languages'+ '\\' +lan.lower())
#E:\Users\SpO_MS_VOP\_ref\languages\ror

###creat txt2wav.bat file
    with open(current_path+'\\txt2wav_vecmdline_ldm.bat','r') as f:
        lines = f.readlines()
        lines = [line.replace('change_stage_path',vop_folder) for line in lines]
        lines = [line.replace('change_txt_path',text_path) for line in lines]
        lines = [line.replace('change_wav_path',wav_vop_path) for line in lines]
        os.makedirs(wav_vop_path)
        lines = [line.replace('change_language',language) for line in lines]
        lines = [line.replace('change_voice',voice) for line in lines]
    f.close()
    batch_file = wav_path + '\\txt2wav_' + vop_nr + '.bat'
    b = open(batch_file, 'w+')
    b.writelines(lines)
    b.close()
    print ('txt2wav_' + vop_nr + '.bat created')
###creat extra test batch
    if extra_test != 'x':
        with open(batch_file) as b:
            lines = b.readlines()
            lines = [line.replace(text_path,extra_path) for line in lines]
        b.close()
        extra_batch_file = wav_path + '\\txt2wav_' + extra_test+ '_'+vop_nr+ '.bat'
        e = open(extra_batch_file, 'w+')
        e.writelines(lines)
        e.close()
###creat verions.txt file
    version_lines = 'vop#plp#ewa#22#embedded-high#1.1.6-SNAPSHOT'
    version_lines = version_lines.replace('plp#ewa',lan.lower()+'#'+voice)
    if 'SNAPSHOT' in vop:
        version_lines = version_lines.replace('1.1.6-SNAPSHOT',vop)
    else:
        version_lines = version_lines.replace('1.1.6-SNAPSHOT',vop) 
        version_lines = version_lines.replace('vop#','vop-bin#') 
        version_lines = version_lines.replace('22#embedded-high','embedded-high') 

    version_file = verions_path + '\\'+'versions_' + vop_nr + '.txt'
    o = open(version_file, 'w+')
    o.writelines(version_lines)
    o.close()
    print ('versions_' + vop_nr + '.txt created')


###download stages
    stage=subprocess.Popen(["E:\Users\Shanshan.Xu\stages\staging-tools-1.12.21-SNAPSHOT\\bin\stage.exe",version_file,vop_folder],shell=True)
    stage.wait()

    pcm1 = subprocess.call([batch_file])
    pcm1.wait()
    #pcm_extra = subprocess.call([extra_batch_file])
    #pcm_extra.wait()




#E:\Users\SpO_MS_VOP\FIF\_test_suite
#E:\Users\SpO_MS_VOP\THT\kanya\VOP_RT_ref-e-h-1-0-2_target-e-h-1-0-3-SNAPSHOT\input_text


'''
'''

rt_procedures(ref_vop)
rt_procedures(tar_vop)



###compare pcm and tso 
tar_pcm = wav_path + 'target_pcm'
ref_pcm = wav_path + 'reference_pcm'
len_tar = len(os.listdir(tar_pcm))
d1 = set(os.listdir(tar_pcm))
match,mismatch,errors = filecmp.cmpfiles(tar_pcm,ref_pcm,d1,shallow=False)

'''
df = pd.DataFrame({
'Match':match,
'Mismatch':mismatch})
df.to_csv('compare_result.csv', sep = ';',index=False)
'''

###creat readme.txt file
with open('RT_readme.txt') as r:
    lines = r.readlines()
    lines = [line.replace('ref_vop',ref_vop) for line in lines]
    lines = [line.replace('tar_vop',tar_vop) for line in lines]
    lines = [line.replace('path_to_adapt',text_path) for line in lines]
    if extra_test ==  'x':
        lines = [line.replace('extra_path',' ') for line in lines]
    else:
        lines = [line.replace('extra_path',extra_path) for line in lines]
    if len(mismatch) == 0:
        print 'congratulation! No regressions.'
        lines = [line.replace('Match_Result','PCM Match: 100% ') for line in lines]
    else:
        percent= len(mismatch)/ len_tar
        lines = [line.replace('Match_Result','PCM Match: ' + str(percent) +'%') for line in lines]
        lines.append('Mistmatch List:')
        for m in mismatch:
            lines.append(m + '\n')
        print 'Please check the readme file for the regressions!'
    r.close()
#MS_trt_yelda_E-H_2-0-2_RT_readme.txt
readme_file =  wav_path +   'MS_'+lan.lower()+'_'+voice+'_E-H_'+tar_vop.replace('.','-').strip('-SNAPSHOT')+'_RT_readme.txt'
o = open(readme_file, 'w+')
o.writelines(lines)
o.close()

print 'done'

