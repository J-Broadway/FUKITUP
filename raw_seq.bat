@echo off
setlocal EnableDelayedExpansion

call ascii.bat

:: Ask the user for video info
set /p video_path="Enter the path to the video: "
set /p width="Enter video width: "
set /p height="Enter video height: "

:: Create a new directory with the same name as the video
set video_name=%video_path%
for /F "delims=" %%i in ("%video_path%") do (
	set video_name=%%~ni
	set "filepath=%%~pi"
	set ext=%%~xi
)

cd %filepath%
mkdir %video_name%

:: FFMPEG 
ffmpeg -i %video_name%%ext% %video_name%/%video_name%%%d.png
echo FFMPEG conversion complete... Converting to raw

:: Start Magick convert
set raw_dir=%video_name%_raw
cd %video_name%
mkdir %raw_dir%

:: Loop through every .png and convert to .raw
for %%f in ("%cd%\*.png") do (
	:: This is the full name extension
    set "png=%%~nxf"
	set "png_name=!png:~0,-4!"
	echo Converting !png! to .raw...
	magick convert !png! rgb:%raw_dir%/!png_name!.rgb
)

:: Apply SOX effect
cd %raw_dir%
for %%f in ("%cd%\*.rgb") do (
    set "rgb=%%~nxf"
	set "rgb_name=!rgb:~0,-4!"
	echo Apply SOX affects to !rgb!
	
	sox -t ul -c 1 -r 41k !rgb! -t raw !rgb_name!_sox.rgb phaser
	magick convert -size %width%x%height% -depth 8 rgb:!rgb_name!_sox.rgb moshed_!rgb_name!.png
	
)

echo DONE!
pause
