#!/usr/bin/env python

#-----------------------------------------------------------------------------
# Imports

import sys
import os
import os.path
import platform
import subprocess
import glob
import shutil
import argparse
import tempfile
import hashlib
import xml.etree.ElementTree as ElementTree
import time

#------------------------------------------------------------------------------
# Constants

progstr = [
    "Vocalizer Single Package Tool",
    "0.0.1",
    "Copyright (C) 2015 Nuance Communications, Inc."
]

usage = \
    "\n" \
    + "   singlepackage.py [-h] [-V] [-v] [-b BASETOOLPATH]\n" \
    + "                    (-r REPACK [ -p PIPELINE ] | -m MAINCLC -p PIPELINE )\n" \
    + "                    -o OUTPUTPKG \n" \
    + "                    [-k [yes|no]]\n" \
    + "                    [-c [CLC [CLC ...]]]\n" \
    + "                    [-f [FILES [FILES ...]]]"

OK=0
NOT_IMPLEMENTED=1
FILE_NOT_FOUND=2
VCLCDATAPACK_ERROR=3
VCLCDATAWALKER_ERROR=4
UNKNOWN_OPERATION_MODE=5
MISSING_TOOL=6
OUTPUT_ALREADY_EXISTING=7
INPLACE_NOT_POSSIBLE=8

verbose=True
CLEANUP=True

#------------------------------------------------------------------------------
# Globals

baseToolPath = os.path.abspath(os.path.dirname(os.path.abspath(__file__))+"/vclcdatatools")

#------------------------------------------------------------------------------
# Argument parsing

def create_arg_parser():
    """Create argument parser for commands and options."""
    global progstr
    parser = argparse.ArgumentParser(description=progstr[0],
                                     usage=usage,
                                     fromfile_prefix_chars='@')

    parser.add_argument('-V', '--version', action='version', version=progstr[0] + ' v' + progstr[1])
    parser.add_argument('-v', '--verbose', help="print more logging information", action='store_true')

    parser.add_argument('-b', '--basetoolpath', help="path to vclcdata tools directory", default="")

    parser.add_argument('-r', '--repack', help="repack package from existing package REPACK", default="")
    parser.add_argument('-k', '--pckgdata', help="package data according to V6 standard", default="")
    parser.add_argument('-p', '--pipeline', help="pipeline header filename", default="")
    parser.add_argument('-m', '--mainclc', help="main clc data filename", default="")

    parser.add_argument('-o', '--outputpkg', required=True, help="single package output filename")

    parser.add_argument('-c', '--clc', help="additional clc data filename(s)", nargs='*', default = [])
    parser.add_argument('-f', '--files', help="other (eg backend) data filename(s)", nargs='*', default = [])
    return parser

#------------------------------------------------------------------------------
# util functions

def BaseToolPath():
  global baseToolPath;

  return baseToolPath


def ToolSuffix():
  if platform.system() == 'Windows':
    return ".exe"
  elif platform.system() == 'CYGWIN_NT-10.0':
    return ".exe"
  elif platform.system() == 'Linux':
    return ".exe"
  elif platform.system() == 'Darwin':
    return ".exe"
  else:
    return ""


def ToolPath():
  if platform.system() == 'Windows':
    return os.path.abspath(BaseToolPath() + "/Windows")+"/"
  elif platform.system() == 'CYGWIN_NT-10.0':
    return os.path.abspath(BaseToolPath() + "/Windows")+"/"
  elif platform.system() == 'Linux' and platform.machine() == 'x86_64':
    if platform.linux_distribution()[0] in ['CentOS', 'Red Hat Enterprise Linux Server']:
      return os.path.abspath(BaseToolPath() + "/CentOS64/")+"/"
    else:
      return os.path.abspath(BaseToolPath() + "/Linux64/")+"/"
  elif platform.system() == 'Linux':
    if platform.linux_distribution()[0] in ['CentOS', 'Red Hat Enterprise Linux Server']:
      return os.path.abspath(BaseToolPath() + "/CentOS/")+"/"
    else:
      return os.path.abspath(BaseToolPath() + "/Linux/")+"/"
  elif platform.system() == 'Darwin':
    return os.path.abspath(BaseToolPath() + "/Darwin/")+"/"
  else:
    return BaseToolPath()

def ToolPathArg(patharg):
  if platform.system() == 'CYGWIN_NT-10.0':
    return subprocess.check_output(['/usr/bin/cygpath', '-m', patharg]).strip()
  else:
    return patharg

def Tool(name):
    return ToolPath() + name + ToolSuffix()

    
def last_one_replace(s, old, new):
    return (s[::-1].replace(old[::-1], new[::-1], 1))[::-1]    

#------------------------------------------------------------------------------

def listdir_fullpath(d):
    return [os.path.join(d, f) for f in glob.glob(d)]

#------------------------------------------------------------------------------

def VCLCDataPack(args):
  global verbose
  result = OK
  cmd = [ Tool("vclcdatapack") ] + args
  if verbose:
    print "###################################################"
    print "VCLCDataPack: %s" % cmd
    print "###################################################"
  try:
    output = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
    if "ERROR:" in output:
      print "\n### error running VCLCDataPack (1):\n"
      print output
      result = VCLCDATAPACK_ERROR
    elif verbose:
      print output
  except OSError:
    print "\n### error running VCLCDataPack (2)\n"
    result = VCLCDATAPACK_ERROR
  except subprocess.CalledProcessError as e:
    print "\n### error running VCLCDataPack (3, retval=%d)\n" % e.returncode
    result = VCLCDATAPACK_ERROR
  return result


def VCLCDataWalkerExtract(filename):
  global verbose
  result = OK
  output = []
  cmd = [ Tool("vclcdatawalker"), "--extract", ToolPathArg(filename) ]
  if verbose:
    print "###################################################"
    print "VCLCDataWalkerExtract: %s" % cmd
    print "###################################################"
  try:
    output = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
    if "ERROR:" in output:
      print "\n### error running VCLCDataWalker (1):\n"
      print output
      result = VCLCDATAWALKER_ERROR
    elif verbose:
      print output
  except OSError:
    print "\n### error running VCLCDataWalker (2):\n"
    print output
    result = VCLCDATAWALKER_ERROR
  except subprocess.CalledProcessError as e:
    print "\n### error running VCLCDataWalker (3, retval=%d):\n" % e.returncode
    print output
    result = VCLCDATAWALKER_ERROR
  return result


def GetVoconVersionNumber(filename):
    global verbose
    result=OK
    version=""
    output=""
    cmd = [ Tool("vclcdatawalker"), ToolPathArg(filename) ]
    if verbose:
      print "###################################################"
      print "GetVoconVersionNumber: %s" % cmd
      print "###################################################"
    try:
      try:
        output = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
      except subprocess.CalledProcessError as e:
        print "\n### warning: error spawning child process - 2nd and last attempt..."
        time.sleep(1)
        output = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
      if "ERROR:" in output:
        print "\n### error retrieving version number from '%s' (1)\n" % filename
        print output
        result = VCLCDATAWALKER_ERROR
      else:
        version = output.split()[5]
    except OSError:
      print "\n### error retrieving version number from '%s' (2)\n" % filename
      print output
      result = VCLCDATAWALKER_ERROR
    except subprocess.CalledProcessError as e:
      print "\n### error retrieving version number from '%s' (3, retval=%d)\n" % (filename, e.returncode)
      print output
      result = VCLCDATAWALKER_ERROR
    return [ result, version ]


def GetCLCDataVersionNumber(filename):
    result=OK
    version="0.0.0"

    f1 = open(filename,'rb')
    line = f1.readline()
    while line:
      if "<dataversion>" in line:
        s=line
        s=s.replace("<dataversion>", "")
        s=s.replace("</dataversion>", "")
        s=s.replace(" ", "")
        s=s.strip()
        s=s.replace("_", ".")
        f1.close()
        return [ result, s ]
      line = f1.readline()

    f1.close()
    return [ result, version ]

def GetFingerprint(filename):
    hash = hashlib.md5()
    with open(filename, 'rb') as file_to_check:
        while True:
            data = file_to_check.read(512)
            if not data:
                break
            hash.update(data)
    return hash.hexdigest()

def ReGenerateMetainfoFile(metainfoOldFn, metainfoFn, names, voconVersions, dataVersions, filesToPack):
  t = ElementTree.parse(metainfoOldFn)
  r = t.getroot()
  names2 = []
  voconVersions2 = []
  dataVersions2 = []
  for child in r:
    if child.tag == "LANGDATA":
      name=child.find('NAME').text
      voconVersion=child.find('VOCONVERSION').text
      dataVersion=child.find('DATAVERSION').text
      #print child.tag
      #print "   "+name
      #print "   "+voconVersion
      #print "   "+dataVersion
      if not name in names2:
        names2.append(name)
        voconVersions2.append(voconVersion)
        dataVersions2.append(dataVersion)
  for name in names:
    if name in names2:
      i=names.index(name)
      n=names2.index(name)
      voconVersions2[n]=voconVersions[i]
      dataVersions2[n]=dataVersions[i]
    else:
      names2.append(name)
      voconVersions2.append(voconVersion)
      dataVersions2.append(dataVersion)

  os.remove(metainfoOldFn)
  filesToPack.remove(metainfoOldFn)
  GenerateMetainfoFile(metainfoFn, names2, voconVersions2, dataVersions2, filesToPack)

  return

def GenerateMetainfoFile(metainfoFn, names, voconVersions, dataVersions, filesToPack):
  m = open(metainfoFn, 'wb')

  m.write("<METAINFO>")
  for name in names:
    n=names.index(name)
    m.write("  <LANGDATA>\n")
    m.write("    <NAME>"+name+"</NAME>\n");
    m.write("    <VOCONVERSION>"+voconVersions[n]+"</VOCONVERSION>\n")
    m.write("    <DATAVERSION>"+dataVersions[n]+"</DATAVERSION>\n")
    m.write("  </LANGDATA>\n")

  filesToPack.sort()
  for f in filesToPack:
    if os.path.exists(f):
      m.write("  <FILE>\n")
      m.write("    <NAME>"+os.path.splitext(os.path.basename(f))[0]+"</NAME>\n")
      m.write("    <FINGERPRINT>"+GetFingerprint(f)+"</FINGERPRINT>\n")
      m.write("  </FILE>\n")

  m.write("</METAINFO>\n");
  m.close()
  return
#------------------------------------------------------------------------------
# pack function

def PackCLC(parser, args):
      if args.repack == "":
        mainclc = args.mainclc
        print "packaging %s ...\n" % args.outputpkg
      else:
        mainclc = args.repack
        print "repackaging %s ...\n" % args.outputpkg

      if args.pipeline != "" and not os.path.exists(args.pipeline):
        print "\n### pipeline file '%s' missing\n\n" % args.pipeline
        parser.print_help()
        return FILE_NOT_FOUND
      if args.mainclc != "" and not os.path.exists(args.mainclc):
        print "\n### main clc file '%s' missing\n\n" % args.mainclc
        parser.print_help()
        return FILE_NOT_FOUND
      for f in [ mainclc ] + args.clc:
        if not os.path.exists(f):
            print "\n### clc file '%s' missing\n\n" % f
            parser.print_help()
            return FILE_NOT_FOUND
      for f in args.files:
        if not os.path.exists(f):
            print "\n### file '%s' missing\n\n" % f
            parser.print_help()
            return FILE_NOT_FOUND

      # for main CLC file: extract and save the version number
      [ result, version ] = GetVoconVersionNumber(mainclc)
      if result != OK:
        return result

      print "   OUTPUT               : %s " % args.outputpkg
      print "   INPUT"
      if args.repack == "":
        print "      MAINCLC           : %s " % mainclc
        print "      MAINCLC VERSION   : %s" % version
        print "      PIPELINE          : %s " % args.pipeline
      else:
        print "      REPACKCLC         : %s " % mainclc
        print "      REPACKCLC VERSION : %s" % version
        if (args.pipeline == ""):
          print "      PIPELINE          : (use existing pipeline.dat)"
        else:
          print "      PIPELINE          : %s " % args.pipeline
      for f in args.clc:
        print "      CLC               : %s " % f
      for f in args.files:
        print "      FILE              : %s " % f
      print ""

      if mainclc in args.clc:
        args.clc.remove(mainclc)
      allclc = [ mainclc ] + args.clc

      # collect vocon versions of the CLC's
      voconVersions=[]
      dataVersions=[]
      names = []
      for c in allclc:
        if IsFileML2(c):
            continue
        [ result, v ] = GetVoconVersionNumber(c)
        name=os.path.splitext(os.path.basename(c))[0]
        if (len(name.split("_")) == 3) and name not in names:
          names.append(name)
          voconVersions.append(v)
          dataVersions.append("");

      tmp=tempfile.mkdtemp(prefix="spkg.")

      # create an output directory to collect all files to be packed
      outtmpdir=os.path.abspath(tmp+ "/" + os.path.basename(args.outputpkg))
      os.mkdir(outtmpdir)

      # for each CLC file: create a tmp directory, where the extracted CLC files go to
      for c in allclc:
        clctmpdir=os.path.abspath(tmp+ "/" + os.path.basename(c))
        os.mkdir(clctmpdir)

      # for each CLC file: extract and rename file and move to output directory
      for c in allclc:
        clcfile=os.path.abspath(c)
        clcname=os.path.basename(clcfile).replace(".dat", "")
        clctmpdir=os.path.abspath(tmp+ "/" + os.path.basename(c))
        oldcwd = os.getcwd()
        os.chdir(clctmpdir)
        if IsFileML2(clcname):
            shutil.copy(clcfile, clctmpdir) #this replaces the extraction: result = VCLCDataWalkerExtract(clcfile)
            shutil.copy(clcfile, outtmpdir)  # this replaces the renaming(which also moves to main folder): os.rename(f, os.path.abspath(outtmpdir + "/" + clcname + "_" + f))
            os.chdir(oldcwd)
            result = OK
            continue
        result = VCLCDataWalkerExtract(clcfile)
        if result == OK:
          if c != args.repack:
            for f in os.listdir("."):
              # collect data versions the CLC's
              if f == "pipeline.dat" and clcname in names:
                n=names.index(clcname)
                [ result2, dataVersions[n] ] =  GetCLCDataVersionNumber(f)

              if os.path.exists(os.path.abspath(outtmpdir + "/" + clcname + "_" + f)) == True:
                os.remove(os.path.abspath(outtmpdir + "/" + clcname + "_" + f))

              os.rename(f, os.path.abspath(outtmpdir + "/" + clcname + "_" + f))

          else:
            for f in os.listdir("."):
              if f != "pipeline.dat":
                os.rename(f, os.path.abspath(outtmpdir + "/" + f))
        else:
          break
        os.chdir(oldcwd)

      # for each file: move file to output directory
      for f in args.files:
        shutil.copy(f, os.path.abspath(outtmpdir + "/" + os.path.basename(f)))

      if result == OK:
        # pack all the data into output data file
        filesToPack = [ ]

        if args.repack == "":
          for c in allclc:
            if IsFileML2(c):
                pattern = os.path.join(outtmpdir,os.path.basename(c)) #adding ml files one by one
            else:
                pattern=outtmpdir+ "/" + os.path.basename(c).replace(".dat", "") + "_*.dat"
            files = listdir_fullpath(pattern)
            for f in files:
              if os.path.basename(f) == "pipeline.dat":
                files.remove(f)
            for f in files:
              if f not in filesToPack:
                filesToPack = filesToPack + [ f ]

          for f in args.files:
            if f not in filesToPack:
              filesToPack = filesToPack + [ os.path.abspath(outtmpdir + "/" + os.path.basename(f)) ]
        else:
          pattern=outtmpdir+ "/*.dat"
          files = listdir_fullpath(pattern)
          for f in files:
            if os.path.basename(f) == "pipeline.dat":
              files.remove(f)
          filesToPack = filesToPack + files


        if args.pipeline == "":
          args.pipeline = os.path.abspath(tmp+ "/" + os.path.basename(args.repack) + "/pipeline.dat")

        metainfo=os.path.abspath(tmp + "/" + "metainfo.dat")
        if args.repack == "":
          GenerateMetainfoFile(metainfo, names, voconVersions, dataVersions, filesToPack);
        else:
          metainfoOld = os.path.abspath(outtmpdir+ "/metainfo.dat")
          ReGenerateMetainfoFile(metainfoOld, metainfo, names, voconVersions, dataVersions, filesToPack);

        for i, f in enumerate(filesToPack):
          filesToPack[i] = ToolPathArg(f)
        result = VCLCDataPack(["-v", version, ToolPathArg(args.outputpkg), ToolPathArg(args.pipeline) ] + [ ToolPathArg(metainfo) ] + filesToPack)

      # remove tmp file from vclcdatapack
      if CLEANUP and os.path.exists(args.outputpkg + ".tmp"):
        os.remove(args.outputpkg + ".tmp")

      # for each CLC file: remove tmp directory
      if CLEANUP and os.path.exists(tmp) == True:
        shutil.rmtree(tmp, True)

      return result


#------------------------------------------------------------------------------
# pack function for V6.0.x engines

def PackCLCV60x(parser, args):
      mainclc = args.mainclc
      print "packaging V6 %s ...\n" % args.outputpkg


      print "      V6 MAINCLC           : %s " % mainclc
      for f in args.clc:
        print "      V6 CLC               : %s " % f
      for f in args.files:
        print "      V6 FILE              : %s " % f

      # for each file: move file to output directory
      outdir=os.path.dirname(args.outputpkg)

      basnam=os.path.basename(args.outputpkg)
      parts = basnam.split("_")
      baselang = parts[0]
      basevoice = parts[1]
      mainclc_basenam=os.path.basename(mainclc)
      mainclc_dirnam=os.path.dirname(mainclc)
      if ("_bet4_" in args.outputpkg):
        dest_mainclc = os.path.abspath(mainclc_dirnam + "/" + basevoice + "_bet4_" + mainclc_basenam)
      elif ("_bet3_" in args.outputpkg):
        dest_mainclc = os.path.abspath(mainclc_dirnam + "/" + basevoice + "_bet3_" + mainclc_basenam)
      else:
        dest_mainclc = os.path.abspath(mainclc_dirnam + "/" + basevoice + "_" + mainclc_basenam)
      os.rename(mainclc, dest_mainclc)   # Add voice prefix for all V6 models and voice model too for bet4/bet3
      shutil.copy(dest_mainclc, os.path.abspath(outdir))
      for f in args.clc:
        f_basenam=os.path.basename(f)
        parts = f_basenam.split("_")
        f_lang = parts[1]
        f_dirnam=os.path.dirname(f)
        if ("_bet4_" in args.outputpkg):
          dest_f = os.path.abspath(f_dirnam + "/" + basevoice + "_bet4_" + f_basenam)
        elif ("_bet3_" in args.outputpkg):
          dest_f = os.path.abspath(f_dirnam + "/" + basevoice + "_bet3_" + f_basenam)
        else:
          dest_f = os.path.abspath(f_dirnam + "/" + basevoice + "_" + f_basenam)
        os.rename(f, dest_f)   # Add voice prefix for all V6 models and voice model too for bet4/bet3
        if (f_lang != baselang):
          clclangdir = last_one_replace(outdir, baselang, f_lang)   # Replace only the last one language string instance
          if not os.path.exists(clclangdir):
              os.makedirs(clclangdir)
          shutil.copy(dest_f, os.path.abspath(clclangdir))
        else:
          shutil.copy(dest_f, os.path.abspath(outdir))
      for f in args.files:
        f_basenam=os.path.basename(f)
        f_dirnam=os.path.dirname(f)
        if ("_ling_" in f):   # "_ling_" is present in some files of HULSI voices
          dest_f = os.path.abspath(f_dirnam + "/" + basevoice + "_" + f_basenam)
          os.rename(f, dest_f)   # Add voice prefix for some files of HULSI voices
          shutil.copy(dest_f, os.path.abspath(outdir))
        else:
          shutil.copy(f, os.path.abspath(outdir))

      result = 0

      return result

#------------------------------------------------------------------------------
# check if file is ml2 data
def IsFileML2(filename):

    if os.path.basename(filename).startswith('ml2'):
        return True
    else:
        return False

#------------------------------------------------------------------------------
# Main program

def main(argv = None):
    global baseToolPath
    global verbose

    result = OK

    parser = create_arg_parser()
    if argv is None:
        args = parser.parse_args()
    else:
        args = parser.parse_args(argv)

    verbose = args.verbose

    if args.basetoolpath != "":
      baseToolPath = os.path.abspath(args.basetoolpath)

    if os.path.exists(Tool("vclcdatawalker")) == False:
      print "\n### %s not found\n" % Tool("vclcdatawalker")
      result = MISSING_TOOL

    elif os.path.exists(Tool("vclcdatapack")) == False:
      print "\n### %s not found\n" % Tool("vclcdatapack")
      result = MISSING_TOOL

    elif args.outputpkg == args.repack:
      print "\n### input %s and output %s voice package can not be the same\n" % (args.mainclc, args.outputpkg)
      result = INPLACE_NOT_POSSIBLE

    #elif os.path.exists(args.outputpkg) == True:
    #  print "\n### %s already existing\n" % args.outputpkg
    #  result = OUTPUT_ALREADY_EXISTING

    elif args.mainclc != "" and args.pipeline != "" and args.repack == "":
      if args.pckgdata == "no":
        result = PackCLCV60x(parser, args)
      else:
        result = PackCLC(parser, args)

    elif args.mainclc == "" and args.repack != "":
      result = PackCLC(parser, args)

    else:
       print "\n### unknown operation mode\n"
       result = UNKNOWN_OPERATION_MODE
       parser.print_usage()

    return result


if __name__ == '__main__':
    sys.exit(main())
