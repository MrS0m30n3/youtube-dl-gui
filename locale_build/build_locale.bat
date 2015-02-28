@echo off

REM Author: Sotiris Papadopoulos
REM Last-Edited: 25/02/2015
REM Script to auto-create a locale file.

REM Usage: build_locale.bat <locale> <locale_file>
REM Example: build_locale.bat gr_GR gr.po

REM To create a new locale file copy youtube_dl_gui.po
REM to a new locale file (e.g. gr.po) edit it with your
REM favorite editor and then run this script.

REM You also need to install gettext for Windows

set FILENAME=youtube_dl_gui

set /a args=0
for %%A in (%*) do set /a args+=1

if not %args% == 2 (
	echo Usage: %~n0.bat "locale" "locale_file"
	echo Example: %~n0.bat gr_GR gr.po
) else (
	mkdir ..\%FILENAME%\locale\%1\LC_MESSAGES

	msgfmt.exe --output-file %FILENAME%.mo %2

	move %2 ..\%FILENAME%\locale\%1\LC_MESSAGES\%FILENAME%.po 1>NUL
	move %FILENAME%.mo ..\%FILENAME%\locale\%1\LC_MESSAGES\ 1>NUL

	tree /F ..\%FILENAME%\locale\%1

	echo Done
)
