from __future__ import print_function
import os
import sys
import argparse
import textwrap
import zipfile
import requests

THIS_DIR = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(THIS_DIR, '..', '..'))

# mapping from local folder -> zip to copy from
ZIP_FILES = {
    'CentOS': 'vclc_tools-i86_centos.zip',
    'CentOS64': 'vclc_tools-i86_64_centos.zip',
    'Darwin': 'vclc_tools-i86_64_darwin.zip',
    'Linux': 'vclc_tools-i86_linux2.zip',
    'Linux64': 'vclc_tools-i86_64_linux2.zip',
    'Windows': 'vclc_tools-i86_win32.zip',
}

REVISION = 'f0842e51b7ea' # build from 08-09-17 11:24:52

ARTIFACTORY_URL = 'https://aac-srv-artifactory-test.nuance.com'
REPOSITORY = 'tts-snapshot'
DOWNLOAD_URL = '{base_url}/{repository}/com/nuance/vocalizer/tools/vclctools/{revision}'

TEMP_DIR = os.path.join(os.getcwd(), '_temp')


        
def _parse_args():
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter,  
                                     description="Update VCLC binaries")
    parser.add_argument('--artifactory-url', 
                        default=ARTIFACTORY_URL,
                        help=textwrap.dedent("""\
                            Artifactory URL (default: %(default)s)"""))
    parser.add_argument('--repository', 
                        default=REPOSITORY,
                        help=textwrap.dedent("""\
                            Artifactory Respository (default: %(default)s)"""))                            
    parser.add_argument('--revision', 
                        default=REVISION,
                        help=textwrap.dedent("""\
                            revision of the build to download from Artifactory - will fail for partial builds"""))
    parser.add_argument('--temp-dir', 
                        default=TEMP_DIR,
                        help=textwrap.dedent("""\
                            directory we use to download packages to %(default)s"""))
    return parser.parse_args()


def extract(zf, dst, tool):
    with open(os.path.join(THIS_DIR, dst, '%s.exe' % tool), 'wb') as fp_tool:
        fp_tool.write(zf.read('_tools/%s.exe' % tool))

    
def main():
    args = _parse_args()
    
    url = DOWNLOAD_URL.format(base_url = args.artifactory_url,
                              repository = args.repository,
                              revision = args.revision)
    
    if os.path.exists(args.temp_dir):
        for fn in map(lambda x: os.path.join(args.temp_dir, x), ZIP_FILES.values()):
            if os.path.exists(fn):
                print("Remove %s" % fn)
                os.unlink(fn)
    else:
        os.makedirs(args.temp_dir)
        
    for fn in ZIP_FILES.values():
        dlurl  = '/'.join([url,fn])
        target = os.path.join(args.temp_dir, fn)
        
        print("Download %s to %s" % (dlurl, target))
        
        r = requests.get(dlurl, stream=True)
        r.raise_for_status() # fail if we have 4xx or 5xx response
        
        with open(target, 'wb') as fp:
            for chunk in r.iter_content(1024):
                fp.write(chunk)
    
    for dst, src in ZIP_FILES.iteritems():
        print(dst, src)
        with zipfile.ZipFile(os.path.join(args.temp_dir, src), 'r') as zf:
            extract(zf, dst, 'vclcdatapack')
            extract(zf, dst, 'vclcdatawalker')    
    return 0
    
    
if __name__ == '__main__':
    sys.exit(main())
