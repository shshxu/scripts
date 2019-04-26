import shutil, os, subprocess, time, filecmp

stg_dict = dict([(i, stg) for (i,stg) in enumerate(os.listdir('E:\Users\SpO_MS_VOP\_stage'))])
for(k,v) in stg_dict.items():
    print("{k}: {v}".format(k=k,v=v))

stage=raw_input('Choose a stage (e.g. 0, 1, or n for a new stage): ').lower()
if stage == 'tttt':
    lan='fif'
    language = 'finnish'
    voice='satu'
    ref_vop='1.0.3'
    tar_vop='1.0.4-SNAPSHOT'
    extra_test='inpENG'
    fb_num = 'XXXXXX' 
    stage = 'x'

wd = 'E:\Users\SpO_MS_VOP'
def new_stage(vop):
    vop_path = stage_path + '\_' + vop
    os.makedirs(vop_path)
    ver_path = vop_path + '\\versions.txt'
    version_file = open(ver_path, 'w+')
    version_file.writelines(v_lines)
    version_file.close()
    print ('*********** Downloading new stage '+ vop + '...**********')
    stage=subprocess.Popen(["E:\Users\SpO_MS_VOP\_tools\_staging_tool\\bin\stage.exe",ver_path,vop_path],shell=True)
    stage.wait()
    print ('############## '+vop + ' stage downloaded ##################')


if stage == 'n':
    stage = raw_input('Please enter the project name: ').lower()
    engine_nr = raw_input('Please enter the engine version (e.g. 3.4.3):  ')
    cmn_nr = raw_input('Please enter the common version (e.g. 1.0.16): ')
    with open('_files/versions.txt') as v:
        v_lines = v.readlines()
    v.close()
    v_lines = [line.replace('engine_nr',engine_nr) for line in v_lines]
    v_lines = [line.replace('cmn_nr',cmn_nr) for line in v_lines]
    stage_path =  wd + '\_stage' + '\\' + stage
    new_stage('ref')
    new_stage('tar')
else:
    stage = stg_dict[int(stage)]
    stage_path =  wd + '\_stage' + '\\' + stage


lan=raw_input('Please enter 3 letter language token (e.g. PTP): ').upper()
voice=raw_input('Please enter the voice name (e.g. Petra): ').lower()
ref_vop=raw_input('Please enter the reference vop version(e.g. 1.0.1): ')
tar_vop=raw_input('Please enter the target vop version(e.g. 1.0.2-SNAPSHOT): ')
extra_test= raw_input('Please enter the extra test suite(e.g. inpENG, or x if no extra suite needed): ')
fb_num = raw_input('Please enter the FB ticket number(e.g. 123456): ')
langmap={}
with open('E:/Users/Andreas.Windmann/scripts/langmap.txt') as f:
    for line in f:
        rline=line.replace('\n','')
        (key, val) = rline.split('\t')
        langmap[key] = val

language = langmap[lan] 

#VOP_RT_ref-e-h-1-1-5_target-e-h-1-1-6-snapshot
rt_name = 'VOP_RT_ref-e-h-' + ref_vop.replace('.','-') + '_target-e-h-' +tar_vop.replace('.','-')+ '_' + stage
#work_path = os.path.abspath('../../stages')+'\\'+lan+'\\'+ voice +'\\'+rt_name
voice_path = wd + '\\'+lan+'\\'+ voice 
file_path = 'E:\Users\SpO_MS_VOP\_tools\_files'
ex = '.utf8'
rt_path = voice_path + '\\' + rt_name +  '\\' 
verions_path = rt_path + 'versions'
extra_path = 'E:\Users\SpO_MS_VOP\_extra_test' + '\\' + extra_test
#E:\Users\SpO_MS_VOP\_extra_test\inpENG
if not os.path.isdir(verions_path):
    os.makedirs(verions_path)


#fetch test suite:
suite_path = 'E:\Users\SpO_MS_VOP'+'\\'+lan+'\\'+'_test_suite'
if os.path.exists(suite_path):
    print 'test suite found'
    n = len(os.listdir(suite_path))
    no_suite  = 'f'
    if n == 0:
        no_suite  = 't'
else:
    no_suite  = 't'
#print '************** \n No test suites found, please fetch the test suite manually, and then run the batch files. \n**************'
#work_path = 'E:\Users\Shanshan.Xu\stages'+'\\'+lan+'\\'+ voice + '\\MS-VOP-RT_' + ref_vop.strip('.') + '_' +tar_vop.strip('.')




def rt_procedures(vop):
    vop_nr = vop.replace('.', '')
    if 'SNAPSHOT' in vop:
        wav_vop_path = rt_path + 'target_pcm'
        vop_folder= stage_path + '\_tar'
    else:
        wav_vop_path = rt_path + 'reference_pcm'
        vop_folder = stage_path + '\_ref'
    #os.makedirs(vop_folder)
###deleting old vops if exists
    if os.path.exists(vop_folder+ '\languages' + '\\' + lan.lower()):
        shutil.rmtree(vop_folder+ '\languages'+ '\\' +lan.lower())


###creat txt2wav.bat file
    with open(file_path +'\\txt2wav_vecmdline_ldm.bat','r') as f:
        lines = f.readlines()
        lines = [line.replace('change_stage_path',vop_folder) for line in lines]
        lines = [line.replace('change_txt_path',suite_path) for line in lines]
        lines = [line.replace('change_wav_path',wav_vop_path) for line in lines]
        os.makedirs(wav_vop_path)
        lines = [line.replace('change_language',language) for line in lines]
        lines = [line.replace('change_voice',voice) for line in lines]
    f.close()
    batch_file = rt_path + '\\txt2wav_' + vop_nr + '.bat'
    b = open(batch_file, 'w+')
    b.writelines(lines)
    b.close()
    print ('txt2wav_' + vop_nr + '.bat created')
###creat extra test batch
    if extra_test != 'x':
        with open(batch_file) as b:
            lines = b.readlines()
            lines = [line.replace(suite_path,extra_path) for line in lines]
        b.close()
        extra_batch_file = rt_path + '\\txt2wav_' + extra_test+ '_'+vop_nr+ '.bat'
        e = open(extra_batch_file, 'w+')
        e.writelines(lines)
        e.close()
    else:
        pass
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
    #print ('versions_' + vop_nr + '.txt created')


###download stages
    print ('****Downloading VOP ' + vop + '...**** \n \n')
    stage=subprocess.Popen(["E:\Users\SpO_MS_VOP\_tools\_staging_tool\\bin\stage.exe",version_file,vop_folder],shell=True)
    stage.wait()

    #pcm_extra = subprocess.call([extra_batch_file])
    #pcm_extra.wait()
rt_procedures(ref_vop)
rt_procedures(tar_vop)


###run the batch files to generate pcms
if os.path.exists(suite_path):
    ref_batch_file = rt_path + '\\txt2wav_' +ref_vop.replace('.', '') + '.bat'
    tar_batch_file = rt_path + '\\txt2wav_' +tar_vop.replace('.', '') + '.bat'
    pcm1 = subprocess.call([ref_batch_file])
    pcm2 = subprocess.call([tar_batch_file])
###run the extra batch files
    ref_extra_file = rt_path + '\\txt2wav_' + extra_test+ '_'+ref_vop.replace('.', '') + '.bat'
    tar_extra_file = rt_path + '\\txt2wav_' + extra_test+ '_'+tar_vop.replace('.', '') + '.bat'
    if os.path.exists(ref_extra_file):
        extr1 = subprocess.call([ref_extra_file])
        extr2 = subprocess.call([tar_extra_file])
###compare pcm and tso 
    tar_pcm = rt_path + 'target_pcm'
    ref_pcm = rt_path + 'reference_pcm'
    len_tar = len(os.listdir(tar_pcm))
    d1 = set(os.listdir(tar_pcm))
    match,mismatch,errors = filecmp.cmpfiles(tar_pcm,ref_pcm,d1,shallow=False)
else:
    mismatch = []

#E:\Users\SpO_MS_VOP\_stage\wv-icas\_tar
v_file = stage_path + '\_tar\\versions.txt'
with open(v_file) as v:
    v_lines = v.readlines()
    enging_nr = v_lines[0].split('#')[-1]
    cmn_nr = v_lines[1].split('#')[-1]
v.close()


###creat readme.txt file
with open('_files\RT_readme.txt') as r:
    lines = r.readlines()
    lines = [line.replace('tickert_number',fb_num) for line in lines]
    lines = [line.replace('ref_vop',ref_vop) for line in lines]
    lines = [line.replace('tar_vop',tar_vop) for line in lines]
    lines = [line.replace('enging_nr',enging_nr) for line in lines]
    lines = [line.replace('cmn_nr',cmn_nr) for line in lines]

r.close()
if extra_test ==  'x':
    lines = [line.replace('extra_path',' ') for line in lines]
else:
    lines = [line.replace('extra_path',extra_path) for line in lines]
if no_suite  == 't':
    print '****************** \n No test suites found, please fetch the test suite manually, and then run the batch files. \n******************'
elif len(mismatch) == 0:
    print 'congratulation! No regressions.'
    lines = [line.replace('Match_Result','PCM Match: 100% \nTSO Match: 100% ') for line in lines]
else:
    percent= len(mismatch)/ len_tar
    lines = [line.replace('Match_Result','PCM Match: ' + str(percent) +'%') for line in lines]
    lines.append('Mistmatch List: \n')
    for m in mismatch:
        lines.append(m + '\n')
    print '****************** \n Regression test fails. Please check the readme file for the mismatch list. \n******************'
#MS_trt_yelda_E-H_2-0-2_RT_readme.txt
readme_file =  rt_path +   'MS_'+lan.lower()+'_'+voice+'_E-H_'+tar_vop.replace('.','-').strip('-SNAPSHOT')+'_RT_readme.txt'
o = open(readme_file, 'w+')
o.writelines(lines)
o.close()

print 'done.'

