@echo off


set VE_ENGINE_PATH=change_stage_path
set TXT_FILES_DIR=change_txt_path
set WAV_FILES_DIR=change_wav_path
set SSFT_TTS_TSOLOG_ENABLE=TRUE
set SSFT_TTS_TSOLOG_APPEND=TRUE
set RSLOGDEV_ENABLE=FALSE
set RSLOGDEV_LEVEL=6

set SSFTTTSSDK=%VE_ENGINE_PATH%
set PATH=%VE_ENGINE_PATH%\common\speech\components;%PATH%

mkdir %WAV_FILES_DIR% 1> nul 2>&1
for %%x in (%TXT_FILES_DIR%\*.txt) do (
	set SSFT_TTS_TSOLOG_FILENAME=%WAV_FILES_DIR%\%%~nx
	%VE_ENGINE_PATH%\test_rsauto\vecmdline.exe -l "change_language" -n change_voice -O embedded-high -f %%~dpnx.txt -c "text/plain;charset=utf-8" -o %WAV_FILES_DIR%\%%~nx.pcm
	echo '%%~dpnx.txt' --- '%WAV_FILES_DIR%\%%~nx.pcm'
)