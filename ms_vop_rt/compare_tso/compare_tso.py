# coding=utf-8
'''
Created on 06.01.2016

Interpreter: Python 2.7 32-bit

Dependencies: nuanlib.egg, _bootstrap.py

This script compares TSO logs regarding the output after RETTT, NOR and SPT.
Also the audio files are compared.
The Result is stored in an html file, which supports playback of the audio files and quickview of the tso-logs.

It allows the comparison between a baseline-tso and a reg-test-tso with a timestamp.
If there are more than one timestamp-tso the latest timestamp will be used for comparison.

With -status a status bar is shown in the console, which is usefull for local runs, but should not be used for the use on the jenkins-server.

Usage: tso-compare.py <folder> <outputfile.html> <-status>

The -status argument is optional.

@author: gunnar_laux
'''

import os
import sys
import difflib
import codecs
import glob
import datetime
import time
import filecmp
from _bootstrap import nuanlib
from nuanlib import tts
from nuanlib.qa.qa_common import get_input_from_tso
from nuanlib.qa.qa_common import QA_FileReference

if len(sys.argv) < 2:
    sys.exit("Warning! Not enough arguments! Usage: tso-compare.py <compare-folder> <outputfile.html>")    
         
########################################### Arguments ###########################################
st_compare_dir = sys.argv[1]
st_output_file = sys.argv[2]
b_statusbar = False
try:
    if sys.argv[3] == "-status":
        b_statusbar = True
    else:
        sys.exit("Invalid 3rd argument! Please use -status")
except:
    pass
#################################################################################################

################################ Hardcoded for Testing ##########################################
# st_compare_dir = "\\\\ac-srvfile01\\SpeechOutput2\\Jenkins\\p4projects\\autops_mib3_audi_speechoutput_main\\AUDI_high\\tts_regression\\czc_Zuzana\\"
# st_compare_dir = "c:\\Users\\gunnar_laux\\workspace\\tso_compare\\for_sinlge_folder\\test\\"
# st_output_file = "result_%s.html"%(datetime.date.today())
# b_statusbar = True
#################################################################################################

#Error Counters
dct_error_counters = {"RETTT" : 0,
                       "NOR" : 0,
                       "SPT" : 0,
                       }
i_missing_tso = 0
i_no_match = 0

###################################### object to store result of comparison ######################################
class tso_result():
    #constructur
    def __init__(self, st_tso_file_1, st_tso_file_2, st_ort, st_rettt_1, st_rettt_2, st_nor_1, st_nor_2, st_spt_1, st_spt_2):
        self.st_tso_file_1 = st_tso_file_1
        self.st_tso_file_2 = st_tso_file_2
        self.st_ort = st_ort
        self.st_rettt_1 = st_rettt_1
        self.st_rettt_2 = st_rettt_2
        self.st_nor_1 = st_nor_1
        self.st_nor_2 = st_nor_2
        self.st_spt_1 = st_spt_1
        self.st_spt_2 = st_spt_2
        if self.st_rettt_1 == self.st_rettt_2 and self.st_nor_1 == self.st_nor_2 and self.st_spt_1 == self.st_spt_2:
            self.b_match = True
        else:
            self.b_match = False
    
    #returns a tuple of the given type
    def get_type_tuple(self, st_type):
        if st_type == "RETTT":
            return [self.st_rettt_1,self.st_rettt_2]
        elif st_type == "NOR":
            return [self.st_nor_1,self.st_nor_2]
        elif st_type == "SPT":
            return [self.st_spt_1,self.st_spt_2]
        else:
            raise RuntimeError, "Wrong type!"
    
    #compares types rettt, nor or spt, and returns True if match
    def is_equal(self, st_type):
        if st_type == "RETTT" and self.st_rettt_1 == self.st_rettt_2:
            return True
        elif st_type == "NOR" and self.st_nor_1 == self.st_nor_2:
            return True
        elif st_type == "SPT" and self.st_spt_1 == self.st_spt_2:
            return True
        else:
            return False
    
    #returns comparison result in html format    
    def get_html_compare(self, st_type):

        seqm = difflib.SequenceMatcher(None, self.get_type_tuple(st_type)[0], self.get_type_tuple(st_type)[1])        
        
        if self.is_equal(st_type):
            st_result = """
        SIM: 100%% 
        File 1:    <FONT COLOR="#66CC33">%s</FONT>
        File 2:    <FONT COLOR="#66CC33">%s</FONT>
        """%(self.get_type_tuple(st_type)[0],self.get_type_tuple(st_type)[1])
            
        else:
            diff_line = "<FONT COLOR=\"#9999FF\">"
            
            output_1 = []
            output_2 = []
            st_result = ""
            for opcode, a0, a1, b0, b1 in seqm.get_opcodes():
                if opcode == 'equal':
                    output_1.append("<FONT COLOR=\"#9999FF\">" + seqm.a[a0:a1] + "</FONT>")
                    output_2.append("<FONT COLOR=\"#9999FF\">" + seqm.b[b0:b1] + "</FONT>")
                    for x in seqm.a[a0:a1]:
                        diff_line = diff_line + "-"
                elif opcode == 'insert':
                    output_1.append("<FONT COLOR=\"#FF0000\">" + seqm.a[a0:a1] + "</FONT>")
                    output_2.append("<FONT COLOR=\"#FF0000\">" + seqm.b[b0:b1] + "</FONT>")
                    for x in seqm.b[b0:b1]:
                        diff_line = diff_line + "<FONT COLOR=\"#0000CC\">I</FONT>"
                elif opcode == 'delete':
                    output_1.append("<FONT COLOR=\"#FF0000\">" + seqm.a[a0:a1] + "</FONT>")
                    output_2.append("<FONT COLOR=\"#FF0000\">" + seqm.b[b0:b1] + "</FONT>")
                    for x in seqm.a[a0:a1]:
                        diff_line = diff_line + "<FONT COLOR=\"#0000CC\">D</FONT>"
                elif opcode == 'replace':
                    output_1.append("<FONT COLOR=\"#FF0000\">" + seqm.a[a0:a1] + "</FONT>")
                    output_2.append("<FONT COLOR=\"#FF0000\">" + seqm.b[b0:b1] + "</FONT>")
                    for x in seqm.a[a0:a1]:
                        diff_line = diff_line + "<FONT COLOR=\"#0000CC\">R</FONT>"
                else:
                    raise RuntimeError, "unexpected opcode"
        
            st_result += "SIM: <FONT COLOR=\"#FF0000\">" + str(int(seqm.ratio() * 100)) + "% </FONT>"
            st_result += "\n"
            st_result += "        File 1   : " + "".join(output_1)
            st_result += "\n"
            st_result += "        File 2   : " + "".join(output_2)
            st_result += "\n"
            st_result += "        Diff-Type: " + diff_line + "</FONT>"
        return st_result
###################################################################################################

#get a list of all baseline tso files in the tso dir
def get_tso_list(st_tso_dir):
    print "Gathering baseline-tso..."
    ar_result = []
    for file in os.listdir(st_tso_dir):
        if file.endswith(".1.tso"):
            ar_result.append(file)
    print "Done!"
    return ar_result

#returns reg-test-filename with the latest timestamp from a baseline tso
def get_latest_timestamp(st_base_tso,st_tso_dir):
    #get all teg test tsos with timestamp belonging to the baseline tso
    print st_tso_dir + st_base_tso.replace(".1.tso","")
    ar_files = glob.glob(st_tso_dir + st_base_tso.replace(".1.tso","") + "_[0-9][0-9][0-9][0-9][0-9][0-9]-[0-9][0-9][0-9][0-9][0-9][0-9].1.tso")
    print "Files:"  + str(ar_files)
    try:
        return max(ar_files, key=os.path.getctime)
    except:
        return "No regression-test tso found"
 
#function to extract Orthography(ORT), RETTT Output(RETTT), Normalization Output(NOR) and Phonetic Transcription(SPT)
def parse_tso(tso_file):    
    #parse RETTT output
    dict_result = {}
    b_found_rettt = False
    st_result = ""
    ar_tso = []
    
    #open file with support for faulty encoding
    try:
        ar_tso = codecs.open(tso_file,"r",encoding="utf-8").readlines()
    except:
        ar_tso = open(tso_file,"r").readlines()
    
    #parse RETTT
    for line in ar_tso:
        if line.startswith("------------------END LOGGING OF RETTT"):
            break
        if b_found_rettt == True:
            st_result = st_result + line
        if line.startswith("------------------START LOGGING OF RETTT"):
            b_found_rettt = True
    try:
        dict_result["RETTT"] = st_result.split("\n",1)[1].replace("\n","").replace("\r","")
    except:
        dict_result["RETTT"] = "No RETTT Output!"
     
    #fix wrong encodings    
    if  type(dict_result["RETTT"]) == str:
        dict_result["RETTT"] = dict_result["RETTT"].decode("cp437")    
     
    #parse ORT, NOR SPT with tool from r&d
    #create unique tempfile name for support of multiple instances of the function
    st_time = time.strftime("%Y%m%d-%H%M%S")
    
    filename_ldb = "temp_" + st_time + ".xml"
    filename_ref = "temp_" + st_time + ".ref"

    fe_module = None
    inp_tso = get_input_from_tso(tso_file)
    tts.tso2ldb(tso_file, filename_ldb, module=fe_module)
    ref = QA_FileReference(filename_ref)
    ref.load_ldb(filename_ldb, inp_tso)
    ref.write()
    ref.unload()
    ref.load()
    dict_result["ORT"] = ""
    dict_result["NOR"] = ""
    dict_result["SPT"] = ""
    try:
        for txt in ref.data["text"]:
            dict_result["ORT"] = dict_result["ORT"] + " " + txt
    except:
        dict_result["ORT"] = "No ORT Output!"
    try:
        for nrm in ref.data["norm"]:
            dict_result["NOR"] = dict_result["NOR"] + " " + nrm
    except:
        dict_result["NOR"] = "No NOR Output!"
    try:
        for spt in ref.data['tran']:
            dict_result["SPT"] = dict_result["SPT"] + " " + spt
    except:
        dict_result["SPT"] = "No SPT Output!"
    ref.unload()
    os.remove(filename_ldb)
    os.remove(filename_ref)
    
    return dict_result
        
################################# MAIN #########################################

print "Preparing comparison result " + st_output_file
ar_filelist = get_tso_list(st_compare_dir)
int_whole = len(ar_filelist)
ar_result =[]
int_counter = 1
int_whole = len(ar_filelist)

#create list of compare-elements for each file
for file in ar_filelist:
    st_base_tso = file
    # this had to be changed since SPOT now creates the regression test files in different files
    # the old version supported tso-files with timestamps in the same folders 
    st_latest_tso = st_compare_dir + "\\_test_data\\" + st_base_tso

    #progress counter
    if b_statusbar == True:
        sys.stdout.write("\rProgress: " + str(int(100 * float(int_counter)/float(int_whole))) + "% finished")
        sys.stdout.flush()
        int_counter += 1
        
    #parse and compare TSOs
    if os.path.exists(st_latest_tso) and os.path.exists(st_compare_dir + "\\" + st_base_tso):
        dict_parse_1 = parse_tso(st_compare_dir + "\\" + st_base_tso)
        dict_parse_2 = parse_tso(st_latest_tso)
    
    #skip files where tso is missing. This is because SPOT deletes files where reg-test passes        
#     elif not os.path.exists(st_latest_tso) and os.path.exists(st_compare_dir + "\\" + st_base_tso):              
#         i_missing_tso += 1
#         dict_parse_1 = parse_tso(st_compare_dir + "\\" + st_base_tso)
#         dict_parse_2 = {"RETTT":"Missing TSO File", "ORT":"Missing TSO File", "NOR":"Missing TSO File", "SPT":"Missing TSO File"}
#          
#     elif os.path.exists(st_latest_tso) and not os.path.exists(st_compare_dir + "\\" + st_base_tso):              
#         i_missing_tso += 1
#         dict_parse_1 = {"RETTT":"Missing TSO File", "ORT":"Missing TSO File", "NOR":"Missing TSO File", "SPT":"Missing TSO File"}
#         dict_parse_2 = parse_tso(st_latest_tso)
        
        ar_result.append(tso_result(st_base_tso, st_latest_tso, dict_parse_1["ORT"], dict_parse_1["RETTT"], dict_parse_2["RETTT"], dict_parse_1["NOR"], dict_parse_2["NOR"], dict_parse_1["SPT"], dict_parse_2["SPT"]))
    else:
        print "ERROR. TSO-file not found %s"%(file)

ar_result = sorted(ar_result, key=lambda tso_result: tso_result.b_match)

################################# Assembling html file ####################################################
st_html_body = ""

#write html element for each file comparison
for element in ar_result:
    
    st_html_body += """
        <hr>
        File 1 = <b>%s</b>
         
        <audio controls preload="none">
        <source src="%s" type="audio/wav">
        Your browser does not support the audio element.
        </audio>
        <BUTTON ONCLICK="javascript:goToURL('%s')">Open TSO File</BUTTON>
         
        File 2 = <b>%s</b> 
         
        <audio controls preload="none">
        <source src="%s" type="audio/wav">
        Your browser does not support the audio element.
        </audio>
        <BUTTON ONCLICK="javascript:goToURL('%s')">Open TSO File</BUTTON>
         
        Input:
        %s
        
        """%(st_compare_dir.replace("\\","/") + element.st_tso_file_1, st_compare_dir.replace("\\","/") + element.st_tso_file_1.replace(".1.tso",".wav"), st_compare_dir.replace("\\","/") + element.st_tso_file_1, element.st_tso_file_2.replace("\\","/"), element.st_tso_file_2.replace("\\","/").replace(".1.tso",".wav"), element.st_tso_file_2.replace("\\","/"), element.st_ort) 
    
    if element.b_match == False:
            i_no_match += 1
    
    for k in ["RETTT","NOR","SPT"]:
        if element.is_equal(k) == False:
            dct_error_counters[k] += 1

        st_html_body += k + """
        """
        st_html_body += element.get_html_compare(k)
        st_html_body += """
        
        """

st_html_header =("""<HTML>
         <HEAD>
         <meta charset="utf-8"/>
         <TITLE>TSO Comparison Result</TITLE>
         
         <script type="text/javascript">
         //<!--
         function goToURL(val){
         location.href = val; 
         }
         //-->
         </script>
         
         </HEAD>
         <BODY bgcolor="#FFFFCC">
         <BASEFONT SIZE="3" COLOR="#0000CC" FACE="Courier">
         <PRE>
         
         <b><FONT SIZE=5>TSO Comparison Result</FONT></b>
         
         <b><FONT SIZE=4>Stats:</FONT></b>
         TSO-files processed : %s 
         No-Matches:        <FONT COLOR="#FF0000">%s</FONT>
         No-Matches-RETTT:  <FONT COLOR="#FF0000">%s</FONT>
         No-Matches-NOR:    <FONT COLOR="#FF0000">%s</FONT>
         No-Matches-SPT:    <FONT COLOR="#FF0000">%s</FONT>
         TSO-Files missing: <FONT COLOR="#FF0000">%s</FONT>
         """%(len(ar_result), i_no_match, dct_error_counters["RETTT"], dct_error_counters["NOR"], dct_error_counters["SPT"], i_missing_tso))

html_file = codecs.open(st_output_file,"w",encoding="utf-8")
html_file.write(st_html_header + st_html_body)
html_file.close()
