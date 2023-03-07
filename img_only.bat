@echo off
setlocal EnableDelayedExpansion

:: Ask the user for video info
set /p img_path="Enter IMG path: "

:: De-Quote
set img_path=%img_path:"=%

:: Create a new directory with the same name as the video
set video_name=%img_path%
for /F "delims=" %%i in ("%img_path%") do (
	set img_name=%%~ni
	set "img_directory=%%~pi"
	set ext=%%~xi
)

:: Grab media resolution
ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=s=x:p=0 %img_path% > dbres_temp.txt
set /p resolution=<dbres_temp.txt

:: Delete temp file
del dbres_temp.txt

:: Start fukin shit up
cd /d %img_directory%
mkdir %img_name%_bend && cd %img_name%_bend || (
	:OVERWRITE
	set /p answer="Do you want to overwrite the file? (Y/N): "
	if /I "!answer!"=="Y" (
		cd %img_name%_bend
	) else ( 
		if /I "!answer!"=="N" (
			echo Exiting the script...
			pause
			exit /b
		) else (
			echo Invalid Input. Please choose "Y" or "N".
			goto OVERWRITE
			
		)
	)
)

:: Start Magick convert
:: Convert img to .raw
echo Converting %img_name%%ext% to raw format...
magick convert "%img_path%" rgb:%img_name%.rgb
goto SOX

:: Apply SOX effect
:SOX
echo Applying audio effects...
set /p sox_params=<%~dp0sox_params.txt
@echo %sox_params%

sox -t ul -c 1 -r 41k %img_name%.rgb -t raw %img_name%_sox.rgb %sox_params%
magick convert -size %resolution% -depth 8 rgb:%img_name%_sox.rgb %img_name%_moshed%ext%

echo DONE!
start "" %img_name%_moshed%ext%

set /p what_next="What do you wanna do next?: "
if /I "!what_next!"=="R" (
	goto SOX
)

::Clean Up
echo Cleaning up temp files...
del *.rgb /Q