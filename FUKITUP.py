import init
init.main()

from PIL import Image
import subprocess
import click
import sys
import cv2
import os

def load_menu_txt():
    print('| Load Media | Open Folder | Load Preset | Info | ')
    print('  ^            ^             ^    ^        ^')
    return input("Whatcha wanna do: ").lower()


def re_run(flag, input=''):
    # Re-run FUKITUP.py with proper click formatting
    command = [sys.executable, 'FUKITUP.py', f'-{flag}']
    if input:
        command.append(input)
    subprocess.run(command)

def dequote(path):
    return path.strip("'\"")

def is_valid_media(ext, media_types):
    return ext.lower() in media_types

def get_image_attributes(path):
    try:
        with Image.open(path) as img:
            width, height = img.size
            return {
                'name': os.path.splitext(os.path.basename(path))[0],
                'width': width,
                'height': height,
                'filetype': img.format.lower()
            }
    except Exception as e:
        return str(e)

def get_video_attributes(path):
    try:
        cap = cv2.VideoCapture(path)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        cap.release()
        return {
            'name': os.path.splitext(os.path.basename(path))[0],
            'width': width,
            'height': height,
            'frames': frames,
            'fps': fps,
            'filetype': os.path.splitext(path)[1].lstrip('.').lower()
        }
    except Exception as e:
        return str(e)

def classify_media(path):
    image_formats = {'png', 'jpg', 'tif', 'tiff'}
    video_formats = {'mp4', 'mov', 'gif'}

    _, ext = os.path.splitext(path)
    ext = ext.lstrip('.')

    if is_valid_media(ext, image_formats):
        return get_image_attributes(path)
    elif is_valid_media(ext, video_formats):
        return get_video_attributes(path)
    else:
        return "invalid"

def loading(path):
    print('Loading: ' + path)
    path = dequote(path)

    if not os.path.exists(path):
        print("The inputted path is not valid.")
        return

    media_info = classify_media(path)
    if media_info == "invalid":
        print("The file extension is not a valid media file type.\nAcceptable image formats: png, jpg, tif, tiff.\nAcceptable video formats: mp4, mov, gif.")
    else:
        print(media_info)

@click.command()
@click.option('--load_media', '-l')
@click.option('--open_folder', '-o')
@click.option('--load_preset', '-lp')
@click.option('--info', '-i', is_flag=True)
def startup(load_media, open_folder, load_preset, info):
    if load_media:
        loading(load_media)
    if open_folder:
        print(open_folder)
    if load_preset:
        print(load_preset)
    if info:
        print(info)

def main():
    args_len = len(sys.argv)
    args = sys.argv[1:]  # Get command line arguments except the filename

    try:
        """Custom error handling for click"""
        startup(standalone_mode=False)
    except click.ClickException as e:
        def click_error():
            print(e.message)
            exit()

        if '-l' in args:
            media_input = input('Media Path: ')
            re_run(flag='l', input=media_input)
        elif '-o' in args:
            folder_input = input('Folder Path: ')
            re_run(flag='o', input=folder_input)
        elif '-lp' in args:
            preset_load = input('Preset to load: ')
            re_run(flag='lp', input=preset_load)
        elif '-i' in args:
            print("Error related to info option:", e.message)
            re_run(flag='i')
        else:
            click_error()

    if len(sys.argv) == 1:
        re_run(flag=load_menu_txt())


if __name__ == '__main__':
    main()
