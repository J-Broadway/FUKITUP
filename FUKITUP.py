import init
init.main()

from colorama import init, Fore, Style
# Initialize Colorama
init(autoreset=True)
# Custom Colors
DEFAULT = Style.RESET_ALL
LIGHT_YELLOW = '\033[93m'

from PIL import Image
import subprocess
import click
import cv2
import sys
import os

# Global Variable initialization
media_info = None

def dequote(path):
    return path.strip("'\"")

def is_valid_media(ext, media_types):
    return ext.lower() in media_types

def get_media_info(path):
    print(Fore.YELLOW + f'{LIGHT_YELLOW}Loading: {DEFAULT}' + path)
    path = dequote(path)

    if not os.path.exists(path):
        print(Fore.RED + f"ERROR: The inputted path, '{path}' is not valid.")
        load_menu()

    media_info = classify_media(path)
    if media_info == "invalid":
        print("The file extension is not a valid media file type.\nAcceptable image formats: png, jpg, tif, tiff.\nAcceptable video formats: mp4, mov, gif.")
    else:
        return media_info

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

def get_image_attributes(path):
    try:
        with Image.open(path) as img:
            width, height = img.size
            return {
                'media_type': 'image',
                'media_path': path,
                'name': os.path.splitext(os.path.basename(path))[0],
                'width': width,
                'height': height,
                'filetype': img.format.lower(),
                'root_path': os.path.dirname(path)
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
            'media_type': 'video',
            'media_path': path,
            'name': os.path.splitext(os.path.basename(path))[0],
            'width': width,
            'height': height,
            'frames': frames,
            'fps': round(fps, 2),
            'filetype': os.path.splitext(path)[1].lstrip('.').lower(),
            'root_path': os.path.dirname(path)
        }
    except Exception as e:
        return str(e)

def convert_to_raw():
    print(f'{LIGHT_YELLOW}Creating Raw Images...')
    print(media_info)

    # Make directory to store RAW img formats.
    raw_folder = os.path.join(media_info['folder_path'], media_info['folder_name'] + '_raw')
    output = 'rgb:{}.rgb'.format(raw_folder + '\\' + media_info['folder_name'])
    print(output)
    os.makedirs(raw_folder)

    # Run Image Magick
    cmd = 'magick convert {} {}'.format(media_info['media_path'], output)
    print(cmd)
    subprocess.run(cmd, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Determine media type
    if media_info['media_type'] == 'image':
        img = media_info['media_path']




@click.command()
@click.option('--load_media', '-l')
@click.option('--open_folder', '-o')
@click.option('--load_preset', '-lp')
@click.option('--info', '-i', is_flag=True)
def click_params(load_media, open_folder, load_preset, info):
    if load_media:
        startup(load_media=load_media)

def startup(load_media=None, open_folder=None, load_preset=None, info=None):
    global media_info

    if load_media:
        media_info = get_media_info(load_media)
        base_folder_name = f"{media_info['name']}_fck"
        folder_path = os.path.join(media_info['root_path'], base_folder_name)

        if os.path.exists(folder_path):
            print(
                f"""
                {LIGHT_YELLOW}{base_folder_name} already exists...{DEFAULT}
                ----------------------------------
                | Overwrite | Keep Both | Cancel |
                  ^           ^           ^
                """
            )
            user_choice = input(f"Choose an action: ").lower()
            if user_choice == 'o':
                import shutil
                shutil.rmtree(folder_path)  # Remove the existing folder and all its contents
            elif user_choice == 'c':
                startup(load_media=load_menu_txt())
            elif user_choice == 'k':
                # Find the highest existing folder number
                counter = 2
                while os.path.exists(f"{folder_path}_{counter}"):
                    counter += 1
                folder_path = f"{folder_path}_{counter}"
                print(f'Making directory {folder_path}')

        # Make folder path directory
        os.makedirs(folder_path)

        # Append new info to media_info dictionary
        media_info['folder_path'] = folder_path
        media_info['folder_name'] = os.path.basename(folder_path)

        # Start creating raw imges.
        convert_to_raw()

    if open_folder:
        print(open_folder)
    if load_preset:
        print(load_preset)
    if info:
        print(info)

def load_menu_txt():
    load_media = None
    open_folder = None
    load_preset = None
    info = None

    print(
        f"""
        --------------------------------------------------------
        | Load Media | Open Folder | Load Preset | Info | Exit |
          ^            ^             ^    ^        ^      ^
        """
    )
    user_input = input(f'Whatcha wanna do: ').lower()

    if user_input == 'l':
        load_media = dequote(input(f'Media Path: '))
    if user_input == 'e':
        exit()

    return load_media

def load_menu():
    startup(load_media=load_menu_txt())

# This isn't really the main function... The function that's doing the most is actually the startup() function.
def main():

    args_len = len(sys.argv)
    args = sys.argv[1:]  # Get command line arguments except the filename

    # If FUKITUP.py is run directly (without arguments) then bring ser to load menu.
    if args_len == 1:
        load_menu()

    def click_error():
        print('CLICK EXCEPTION WAS RAISED')
        print(e.message)
        exit()

    try:
        """Custom error handling for click"""
        click_params(standalone_mode=False)
    except click.ClickException as e:
        if args[0] == '-l':
            user_input = input('Media Input: ')
            startup(load_media=user_input)
        else:
            click_error()


if __name__ == '__main__':
    main()
