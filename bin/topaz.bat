@echo off
setlocal

:: Check if a media path is provided and prompt inline if not
if "%~1"=="" (
    set /p media_path=Media: 
) else (
    set media_path=%~1
)

:: Extract the file name without extension and the root directory
for %%A in ("%media_path%") do (
    set "file_name=%%~nA"
    set "root_directory=%%~dpA"
)

:: Construct the output file path
set "output_file=%root_directory%%file_name%_topaz.mp4"

:: FFMPEG command
ffmpeg -loop 1 -r 29 -i "%media_path%" -vf "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2" -t 1 -pix_fmt yuv420p "%output_file%"