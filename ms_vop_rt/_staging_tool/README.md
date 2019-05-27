# Stage

Stage is the staging tool for the Vocalizer product line. 
In this document you will find

* Version history
* Known Issues
* Solutions for Common Problems

## Important Notices

### 2017-10-16: Change of map files

The VOP .dat built by the staging tools v1.10 and later 
is smaller compared to the build by an older version of the staging tool. 
This is because the staging tools v1.10 no longer include the .map 
files of the language data files in the VOP .dat.

This has no impact on the audio output produced by the VOP. 
The .map are used for byte-swapping multi-byte data from little-endian to big-endian format.

For some VOPs like MNC Tian-Tian embedded-high 1.0.0 this brings a considerable reduction 
in heap usage (some 7MB .map are no longer loaded in memory). It may also avoid that the 
load time for this VOP explodes on particular target platforms 
(see case 132507 "Clone: [MIB2Plus] - CLONE TTS - [KPM] [VW] Setting system language 
to CN takes too long [7244765]")

## Version History

### 1.13.2 (next)

* VO-919 --pkgdata did not work correctly after being marked deprcated.

### 1.13.1 (2019-04-15)

* Skipped feature extraction component for frontend_only option

### 1.13.0 (2019-04-08)

Changes:

* Case VO-343: added support to Gilded Speech Data as Separate Tuning Resource

### 1.12.21 (2019-01-31)

* Addition of phonemes for arg


### 1.12.20 (2018-12-26)

Changes:

* Addition of phonemes for sxc

### 1.12.18 (2018-12-19)

Changes:

* Case 170807: Fix clean_stage.py for rc|asap|test vops
* Added staging support for VOPs with ML 2.0


### 1.12.17 (2018-12-04)

Changes:

* Updated vclcdatawalker/vclcdatapacker binaries to a9b480155617 revision

### 1.12.16 (2018-12-03)

Changes:

* Added ability to create pipeline using puncptn_v2. (Case 169887) 
* Updated vclcdatawalker/vclcdatapacker binaries to 6bada6a7357b revision 

### 1.12.15 (2018-11-20)

Changes:

* Added a new option to the 'stage' utility: '--frontend_only=yes', to be used for FE (Front End) only staging. (Case 167468) 

### 1.12.13 (2018-09-06)

Changes:

* Support for 'MRCC' as bet3type value in metadata.json of the backend package (Case 163620)

### 1.12.12 (2018-08-16)

Changes:

* Support for testX vop (Case 161324)
* rsmcorpus_preload_static.exe requires executable flag to run in Linux  (Case 158399)
* add fe_lid/fe_clc_ml/fe_voice_switch components for xpremium-high (Case 161668)
* Update staging tool to support multiple tuning package (Case 161933)
* add LID components to sxc and doc languages (Case 162418)

Bugfixes:

* None

### 1.12.11 (2018-07-24)

Changes:

* Improved cache feature

Bugfixes:

* Fixed Handle ParseError error in ve-voppackage-pipeline (160855)

### 1.12.10 (2018-07-20)

Changes:

* Changed stage script to write tuning resources in order(Case 157798)
* patch to make singlepackage.py work in cygwin
* Updated staging tool to support Hulsi lipsync(Case 160452)

### 1.12.9 (2018-07-6)

Changes:

* Updated staging tool to support staging of ASAP VOPs (Case 158448)

Bugfixes: None

### 1.12.8 (2018-06-29)

Bugfixes:

* Fix incorrect vclc tool version on Linux

### 1.12.7 (2018-06-25)

Changes:

* Updated CLC tools to build rev dca836e2b072 from vocvoc_int
* Additional testing for dictionary resource (Case 147632)
* Additional testing for extra hdr keys

Bugfixes: None

### 1.12.6 (2018-06-12)

Changes:

* Updated "extraesclang" key condition to fix VOP accept failure (Case 156989)

### 1.12.5 (2018-05-25)

Changes:

* Support additional extra parameters and made changes in pipeline_spec.py (Case 152794)
* Fixed failure of [ML-Bundling] ENG VOP and made changes in hdr.py (Case 150270)
* Add missing pipeline components 'fe_lid, fe_clcml, fe_voiceswitch' for THT (Case 114452)

### 1.12.4 (2018-04-16)

Changes:

* Fixed failure on vocalizer-6.2.3 and voices with extra CLCs (Case 152537)


### 1.12.3 (2018-03-29)

Changes:

* Support RETTT tunning resource in BE package (Case 147627)
* Support specifying the load_mode for tuning resources (Case 147629)
* Add support for BET5 hdr parameters (Case 148172)
* Updated phonemetables

### 1.12.2 (2018-02-20)

Bugfixes:

* Fix release build

### 1.12.1 (2018-02-20)

Changes:

* Added bet4 tuning parameters. (Case 146848)

Bugfixes: None

### 1.12 (2017-09-18)

Changes:

* Added '--keep-going' parameter. (Case 132795)

Bugfixes: None

### 1.11 (2017-09-18)

Changes:

* Removed JAVA dependency (Case 130483)
  ** Added '--cache' and '--discard-cache' parameter.
  Note: '--ivy-cache' and '--discard-ivy-cache' parameters are deprecated.
* Automatically install dependencies when runnning from source build (Case 130483)
* Allow redirecting location for pip data via STAGE_PIP_DATA_PATH environment variable (Case 133835)
* Added support for SHC and fe/fe_wmp component (Case 134174)

Bugfixes:

* VOPs that include tuning resource (i.e. EMOJI) can now be staged properly (Case 130655)
* Fix exe build of staging tool to include all dependencies correctly (Case 133360)

### 1.10

Changes:

* Added support for staging new binary packages (Case 108831)
* Added support for staging wildcard files from containers (Case 128653)
* Updated VCLC Tools for latest versions to support CRF MDE/POS for KOK, GED, ENU (Case 128646)

Bugfixes: None

### 1.9 (2017-06-05)

Changes:

* Added support for BET5 voices (Case 126700)
* Added support for additional VOP component next to BE/FE (Case 127071)
* Added support to retrieve the --product key automatically from version file (Case 112135)
  ** It will use 've' as product if all VOP packages are for VE.
  ** It will use 'vocalizer6' as product if all VOP packages are for VS.
  ** It will fall back to 've' as product if there are mix VOP packages i.e. few of them for VE and few of them for VS.
  ** It will fall back to 've' as product if there are no VOP packages.
  Note: Use --product to overwrite default feature.

Bugfixes: None

### 1.8 (2017-05-31)

Changes:

* Added support for additional BET4 keys (Case 126666)
* Added support for staging new vocs-enterprise packages (Case 128161)
* Added support for RETTT tuning resources (Case 126698)

Bugfixes:

* Fix broken staging for VE 2.0 (Case 127375)

### 1.7 (2017-05-18)

Changes:

* Add support for RC vops

Bugfixes:

* Fix length of RC version to 9 instead of 10 digits (Case 123117)
* Fix support for EPrem VOPs

### 1.6 (2017-02-23)

Changes:

* Support `--no-generate` option. 
  Passing this will not download/build VOPs again the already exist on disk
  **Use this feature with care and only if you know what you are doing.**
* Add support for official root CAs to cacerts used by Ivy
  This is in preparation of moving Artifactory to a fully trusted certificate chain

Bugfixes:

* Fix `nativetypeofchar`generation for V6.0.x and V6.2.x. 
  Previously, nativetypeofchar would be generated as `windows-Unicode` of `windows-utf-8` if `Unicode/utf-8` 
  was the native character type set in the metadata. This has been fixed to correctly be set to `Unicode` 
  and `utf-8` in the generated HDR.

### 1.5 (2017-01-18)

Changes:
Bugfixes:

### 1.2 (2017-01-18)

Changes:
Bugfixes:

### 1.1 (2017-01-18)

Changes:

* The default value for nlucompatvc6be changed from 'yes' to 'no'

Bugfixes:
*

### 1.0 (2017-01-18)

Initial release

## Known Issues

## Solutions for Common Problems