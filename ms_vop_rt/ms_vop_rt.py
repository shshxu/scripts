import shutil, os, subprocess, time, filecmp
import requests
import lxml.html as lh
import pandas as pd
from distutils.version import LooseVersion


stg_dict = dict([(i, stg) for (i,stg) in enumerate(sorted(os.listdir('E:\Users\SpO_MS_VOP\_stage')))])
for(k,v) in stg_dict.items():
    print("{k}: {v}".format(k=k,v=v))

def get_latest_version(url):
    page = requests.get(url)
    #Store the contents of the website under doc
    doc = lh.fromstring(page.content)
    #Parse data that are stored between <tr>..</tr> of HTML
    tr_elements = doc.xpath('//tr')

    #Create empty list
    col_name = []
    #For each row, store each first element (header) and an empty list
    for t in tr_elements[0]:
        name=t.text_content()
        #print(name)
        col_name.append(name)
    col_name= col_name[:-2]
    #print(col_name)

    #Since out first row is the header, data is stored on the second row onwards
    rows=[]
    for j in range(2,len(tr_elements)):
        #T is our j'th row
        T=tr_elements[j]
        #Iterate through each element of the row
        row = []
        for t in T.iterchildren():
            data=t.text_content() 
            row.append(data)
        rows.append(row[:-2])

    df=pd.DataFrame(rows, columns =col_name )
    #print(url)
    if 'engine' in url:
        df_reduced = df[df['Product']=='ve'][df['Platform']=='win64'][df["Version"].str.contains('SNAPSHOT')==0]
    else:
        df_reduced = df
        
    versions = df_reduced['Version'].tolist()
    version_latest = sorted(versions, key=LooseVersion)[-1]
    return version_latest
    #print(version_latest)
    

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
def new_stage(vop, lines):
    vop_path = stage_path + '\_' + vop
    os.makedirs(vop_path)
    ver_path = vop_path + '\\versions.txt'
    version_file = open(ver_path, 'w+')
    version_file.writelines(lines)
    version_file.close()
    print ('####################### \n Downloading new stage '+ vop + '...\n#######################')
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
    new_stage('ref',v_lines)
    new_stage('tar',v_lines)
else:
    stage = stg_dict[int(stage)]
    stage_path =  wd + '\_stage' + '\\' + stage
    if stage == 'main-line':
        url_engine='http://aac-srvtts-tools/vocaholic/engine/all/'
        url_common = 'http://aac-srvtts-tools/vocaholic/common/release/'
        engine_latest = get_latest_version(url_engine)
        common_latest = get_latest_version(url_common)
        with open(stage_path+'\_ref\\versions.txt') as v:
            v_lines = v.readlines()
        v.close()
        engine_nr = v_lines[0].split('#')[-1].strip('\n')
        cmn_nr = v_lines[1].split('#')[-1].strip('\n')
        #print(engine_nr,cmn_nr)
        #print(engine_latest, common_latest)
        #for line in lines:
            #v_lines.append(line)
        i = 1
        if engine_latest == engine_nr:
            pass
        else:
            i = 0
            v_lines = [line.replace(engine_nr, engine_latest) for line in v_lines]
        if common_latest == cmn_nr:
            pass
        else:
            i = 0
            v_lines = [line.replace(cmn_nr, common_latest) for line in v_lines]
        if i == 1:
            print('####################### \n main-line stage has the latest engine and common \n#######################')
            #print(v_lines)
        else:
            print('####################### \n Found later version of the main-line stage, downloading new main-line stage \n#######################')
            #print(v_lines)
            shutil.rmtree(stage_path)
            #os.makedirs(stage_path)
            new_stage('ref')
            new_stage('tar')
 


        '''
        platform_zip#/#com.nuance.vocalizer.engine#ve#win64-dev#engine_nr
        zip#languages/common#com.nuance.vocalizer.data.languages#common#cmn_nr
'''




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
    version_lines = version_lines.replace('1.1.6-SNAPSHOT',vop)

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

def compare_mismatch(mis_list):

    mis_path = rt_path + 'mismatch_files'
    os.makedirs(mis_path)
    os.makedirs(mis_path+'\\_test_data')

    for f in mis_list:
        o_path_ref = ref_pcm  + '\\' + f
        n_path_ref = mis_path + '\\' + f
        shutil.copyfile(o_path_ref, n_path_ref)
        o_path_tar = tar_pcm + '\\' + f
        n_path_tar = mis_path+ '\_test_data' + '\\' + f
        shutil.copyfile(o_path_tar, n_path_tar)
    with open(file_path +'\\tso_compare.bat','r') as f:
        lines = f.readlines()

        lines = [line.replace('mismatch_files_path',mis_path) for line in lines]
        lines = [line.replace('change_the_path_',rt_path) for line in lines]
    f.close()
    tso_batch_file = rt_path + '\\compare_tso.bat'
    b = open(tso_batch_file, 'w+')
    b.writelines(lines)
    b.close()
    print ('compare_tso.bat created')
    cp_tso = subprocess.call([tso_batch_file])
        
        
if extra_test ==  'x':
    lines = [line.replace('extra_path',' ') for line in lines]
else:
    lines = [line.replace('extra_path',extra_path) for line in lines]
if no_suite  == 't':
    print '####################### \n No test suites found, please fetch the test suite manually, and then run the batch files. \n#######################'
elif len(mismatch) == 0:
    print '####################### \n congratulation! No regressions.\n#######################'
    lines = [line.replace('Match_Result','PCM Match: 100% \nTSO Match: 100% ') for line in lines]
else:
    percent= len(mismatch)/ len_tar
    lines = [line.replace('Match_Result','PCM Match: ' + str(percent) +'%') for line in lines]
    lines.append('Mistmatch List: \n')
    for m in mismatch:
        lines.append(m + '\n')
    print '####################### \n Regression test fails. Please check the readme file for the mismatch list. \n#######################\nComparing .tso log ... \n#######################'
    compare_mismatch(mismatch)
    
    
readme_file =  rt_path +   'MS_'+lan.lower()+'_'+voice+'_E-H_'+tar_vop.replace('.','-').strip('-SNAPSHOT')+'_RT_readme.txt'
o = open(readme_file, 'w+')
o.writelines(lines)
o.close()




print 'done.'

