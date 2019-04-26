Purpose:
  With this tool, a single voice package can be generated. There are two
  modes:
    - pack a voice package from scratch (with -m, see example 1)
    - repack an existing voice package with new data (with -r, see example 2)
  
Content:
  _readme.txt           this file  
  singlepackage.py      single package python script
  vclcdatatools         exe tools to extract and pack CLC archives for
                        different platforms (Windows, Linux, MacOS X).
                        (May be located at a different place in vocvoc_int)
  testdata              Directory containing test data to be used for the given 
                        examples. (This directory is not contained in vocvoc_int)      

Usage:
   singlepackage.py [-h] [-V] [-v] [-b BASETOOLPATH]
                    (-r REPACK [ -p PIPELINE ] | -m MAINCLC -p PIPELINE )
                    -o OUTPUTPKG 
                    [-c [CLC [CLC ...]]]
                    [-f [FILES [FILES ...]]]

Arguments:
  -h, --help            show this help message and exit
  -V, --version         show program's version number and exit
  -v, --verbose         print more logging information
  -b BASETOOLPATH, --basetoolpath BASETOOLPATH
                        path to vclcdata tools directory
  -r REPACK, --repack REPACK
                        repack package from existing package REPACK
  -p PIPELINE, --pipeline PIPELINE
                        pipeline header filename
  -m MAINCLC, --mainclc MAINCLC
                        main CLC data filename.
  -o OUTPUTPKG, --outputpkg OUTPUTPKG
                        single package output filename
  -c [CLC [CLC ...]], --clc [CLC [CLC ...]]
                        additional CLC data filename(s), eg voice CLC data file
                        and/or foreign CLC data files
  -f [FILES [FILES ...]], --files [FILES [FILES ...]]
                        other (eg backend) data filename(s)

Limitations:
  - Currently, the repackaging mode supports only to add new data or to replace already
    existing data. It is currently not possible to remove eg 'clc_ged_anna_cfg3.dat' and 
    replace it with eg 'clc_ged_anna_cfg4.dat'.
  - Repacking does not work in place. You have to name input and output packages 
    differently. 

Example 1: Generate the single voice pack for anna, embedded compact from scratch:

  python singlepackage.py \
       -m testdata/clc_ged_cfg3.dat \
       -p testdata/ve_pipeline_ged_anna_22_embedded_compact.hdr \
       -c testdata/clc_ged_anna_cfg3.dat \
          testdata/clc_eng_cfg3.dat \
          testdata/clc_frf_cfg3.dat \
          testdata/clc_ged_mpthreevadml.dat \
          testdata/clc_iti_cfg3.dat \
          testdata/clc_spe_cfg3.dat \
       -f testdata/select_anna_bet3f22.dat \
       -o ged-anna-embedded-compact.dat

Example 2: Update pipeline header and backend data of voice package anna
  python singlepackage.py \
       -r ged-anna-embedded-compact.dat \
       -p testdata/ve_pipeline_ged_anna_22_embedded_compact.hdr \
       -f testdata/select_anna_bet3f22.dat \
       -o ged-anna-embedded-compact.new.dat
    


