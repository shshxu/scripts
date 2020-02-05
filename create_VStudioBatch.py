# -*- coding: utf-8 -*-
import pandas as pd
import re, sys, os
#from importlib import reload
#reload(sys)
#sys.setdefaultencoding('utf8')
import codecs
import data
from data.slots_dict import slots_dict

script_path = os.path.dirname(sys.argv[0])

def win32_unicode_argv():
    # Solution copied from http://stackoverflow.com/a/846931/145400
 
    from ctypes import POINTER, byref, cdll, c_int, windll
    from ctypes.wintypes import LPCWSTR, LPWSTR
 
    GetCommandLineW = cdll.kernel32.GetCommandLineW
    GetCommandLineW.argtypes = []
    GetCommandLineW.restype = LPCWSTR
 
    CommandLineToArgvW = windll.shell32.CommandLineToArgvW
    CommandLineToArgvW.argtypes = [LPCWSTR, POINTER(c_int)]
    CommandLineToArgvW.restype = POINTER(LPWSTR)
 
    cmd = GetCommandLineW()
    argc = c_int(0)
    argv = CommandLineToArgvW(cmd, byref(argc))
    if argc.value > 0:
        # Remove Python executable and commands if present
        start = argc.value - len(sys.argv)
        return [argv[i] for i in
                xrange(start, argc.value)]

def get_package_info(lang, pack_type):
    voice = data.get_voice_for_lang(lang)
    types=['vao','rAPDB','tAPDB']
    pack=types[pack_type-1]
    global lang_voice_domain
    lang_voice_domain= ('_').join([lang, voice,'SDS'])
    markup_mapping=os.path.join(script_path, '..\\..\\',pack+'_'+lang_voice_domain,'MappingFile_'+lang_voice_domain+'.xlsx' )
    #pack_lang_voice_type = ('_').join([pack_type, lang_voice_type])
    #VStudioScript_CAC_Sinji-ML_SDS_explicit.txt
    #c:\_projects\NTG_One\vao_GED_Petra-ML_SDS\_testing\VStudioBatch_spec_GED_Petra-ML_SDS_explicit.txt
    global vss_batch_fromMapping, vss_batch_spm, vss_batch_different
    vss_batch_fromMapping= os.path.join(script_path, '..\\..\\',pack+'_'+lang_voice_domain,'_testing','VStudioBatch_spec_'+lang_voice_domain+'_explicit_fromMappingFile.txt' )
    vss_batch_spm = os.path.join(script_path, '..\\..\\',pack+'_'+lang_voice_domain,'_testing','VStudioBatch_spec_'+lang_voice_domain+'_explicit.txt' )
    vss_batch_different = os.path.join(script_path, '..\\..\\',pack+'_'+lang_voice_domain,'_testing','VStudioBatch_spec_'+lang_voice_domain+'_different.csv')
    return  markup_mapping

def read_xlsx(markup_mapping):
    """
    Arguments: Mappingfile_marked (xlsx)
    returns: concept ids  (list)
            sources texts (list)
    """
    df_mapping = pd.read_excel(markup_mapping,encoding='utf-8')
    # Copying over prompt text to source col in case empty
    #df_mapping.loc[df_mapping['Source'].isnull(), 'Source'] = df_mapping['PromptText']
    concept_IDs = df_mapping[['Prompt_Concept_ID','Level_ID']].apply(lambda x: '_'.join(x), axis =1).tolist()
    # To handle rare cases where Source column is empty
    df_mapping['Source'].fillna(df_mapping['PromptText'], inplace=True)
    source_texts = df_mapping['Source'].tolist()
    #print(type(concept_IDs),concept_IDs[:5])
    return concept_IDs, source_texts


def filled_with_click(source_texts, placeholder):
    """
    Arguments: source texts (list)
                placeholder (str)
    returns: filled texts  (list)
    """
    filled_texts=[]
    filled_open=[]
    #pattern=re.compile(r'\<[^\>]+\>')

    for source in source_texts:
        #source = source.replace('> ', '>  ')
        #filled = '\\tn=SDS-PP\\' + re.sub(r'(\<[^\>]+\>\s?){1,}', placeholder+' ', source)
        filled = '\\tn=SDS-PP\\'+ re.sub(r'\<[^\>]+\>', unicode(placeholder, "utf-8"), source, flags=re.UNICODE)
        #filled = filled.replace('  ',' ')

        
        filled_open.append(filled)
    

    """
    looking for sentences ending with ',' and then add a click
    """
    for f in filled_open:
        if not f.endswith((u'。', u'.',u'!',u'?',u'？',u'！', unicode(placeholder, "utf-8"), unicode(placeholder, "utf-8") + ' ')):
            f = f + ' ' + unicode(placeholder, "utf-8")

        #pattern = re.compile("({}\s*)+".format(placeholder))
        #f = re.sub(pattern,placeholder+' ',f)
        if f.endswith(' '):
            f = f[:-1]
        f = re.sub(r'\s(?=[?!.,])','',f )
        filled_texts.append(f)

    

    return filled_texts

def compare_texts(concept_IDS, filled_texts, vss_batch_spm):
    """
    Arguments: 
                concept ids  (list)
                filled texts  (list)
                vss_batch_spm: excel file

                
    output: list of unmatched texts; export to a seperate txt file
    """
    df_filled = pd.DataFrame({'ID':concept_IDs, 'filled': filled_texts})
    df_filled = df_filled.set_index('ID')

    """
    open _testing\VStudioBatch_spec_XXX_explicit.txt as df_spm
    """
    f = open(vss_batch_spm)
    lines = f.readlines()
    f.close()

    spm_ID = [l[:-2] for l in lines[8::3]]
    spm_text = [l[:-1] for l in lines[9::3]]
    df_spm = pd.DataFrame({'ID':spm_ID, 'text_spm':spm_text}).set_index('ID')

    """
    concate df_filled and df_spm, then choose the rows where spm and mapping file filled text are different
    """
    #df_filled.reset_index(drop=True, inplace=True)
    #df_spm.reset_index(drop=True, inplace=True)
    if df_filled.shape!= df_spm.shape :
        print "Wrong number of rows in mapping file and the existing VStudioBatch file!"
    else:
        df_compare = pd.concat([df_filled, df_spm], axis=1, sort=True)
        df_different = df_compare.loc[df_compare['filled'] != df_compare['text_spm']]
        df_different.to_csv(vss_batch_different, encoding='utf-8', sep=';')
        print vss_batch_different

def save_as_txt(lang, concept_IDs, filled_texts, placeholder):
    """
    Arguments:  lang code (str)
                concept ids  (list)
                filled texts  (list)
                placeholder (str)

                
    output: vss_XXX_batch.txt 
    """


    header = '[HEADER]\r\nPromptSculptor Script\r\nScriptVersion = v2.0.0\r\nScriptEncoding = UTF-8\r\nLanguage = {}\r\nDomain = SDS\r\n[TTS]\r\n'.format(lang)
    with codecs.open(vss_batch_fromMapping, 'w', 'utf-8') as f:
        f.write(header)

        for i in range(len(concept_IDs)) :
            concept_id = concept_IDs[i]
            filled = filled_texts[i]
            to_write = concept_id+';\r\n'+filled+'\r\n\r'
            f.write(to_write)
        f.close()
    print('++++++++++++++++++++++++++++++++++++++\nDone! Generated Batch script.\r\n'+'The following file(s) are created:\n{}'.format(vss_batch_fromMapping))

if __name__ == '__main__':
    sys.argv = win32_unicode_argv()
    if len(sys.argv) < 3 or sys.argv[1] in ['-h', '/h', 'help', '/?']:
        sys.exit("Usage:\n"
                    "python markup_to_VSSbatch.py <LANG code> <Package Type> [<placeholder>]\n"
                    "<LANG code>: e.g ENG\n"
                    "<Package Type>: 1 - vao; 2 - rAPDB; 3 - tAPDB (e.g \"1\")\n"
                    "<placeholder>: e.g \"zwanzig Klick\"\n"
                    )    
    
    lang = sys.argv[1].upper()
    pack_type=int(sys.argv[2])

    placeholder_dict = {
        "ARW": "تسعة و تسعون كَلِيك",
        "CAC": "Click",
        "CAH": "Click",
        "CZC": "padesát Klik",
        "DAD": "tredive Klik",
        "DUN": "dertig Klik",
        "ENG": "Twenty-two Click",
        "ENU": "Twenty Click",
        "FRC": "trente Clic",
        "FRF": "trente Clic",
        "GED": "zwanzig Klick",
        "ITI": "Trentatré Clic",
        "JPJ": "九つ Click",
        "KOK": "Click",
        "MNC": "仈十 Click",
        "MNT": "仈十 Click",
        "NON": "Klikk",
        "PLP": "Pięćdziesiąt Klik",
        "PTB": "Trinta Click",
        "PTP": "trinta Click",
        "RUR": "test Клик",
        "SIC": "仈十 Click",
        "SPE": "treinta Clic",
        "SPM": "treinta Clic",
        "SWS": "Klick",
        "THT": "Click",
        "TRT": "Kırk Dört Klik"
    }

    if len(sys.argv) == 4:
        placeholder = (sys.argv[3]).encode('utf-8')
    else:
        placeholder = placeholder_dict[lang]
    markup_mapping = get_package_info(lang, pack_type)
    concept_IDs, source_texts = read_xlsx(markup_mapping)
    filled_texts = filled_with_click(source_texts, placeholder)
    save_as_txt(lang, concept_IDs, filled_texts, placeholder)
    compare_texts(concept_IDs, filled_texts, vss_batch_spm)
