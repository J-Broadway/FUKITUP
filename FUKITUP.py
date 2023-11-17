import init
init.main()

from colorama import init, Fore, Style
# Initialize Colorama
init(autoreset=True)
# Custom Colors
DEFAULT = Style.RESET_ALL
LIGHT_YELLOW = '\033[93m'
MAGENTA = '\033[95m'

from PIL import Image
import subprocess
import click
import cv2
import sys
import os

# Global Variable Initialization
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

    # Folder paths
    raw_folder = os.path.join(media_info['folder_path'], media_info['folder_name'] + '_raw')
    output = 'rgb:{}.rgb'.format(raw_folder + '\\' + media_info['folder_name'])

    # Make directory to store RAW images and append new metadata to dictionary
    os.makedirs(raw_folder)
    media_info['raw_folder_path'] = raw_folder

    # Determine media type
    if media_info['media_type'] == 'image':

        # Run Image Magick and convert each img to raw .rgb file format.
        cmd = 'magick convert {} {}'.format(media_info['media_path'], output)
        subprocess.run(cmd, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    if media_info['media_type'] == 'video':
        import glob

        # Naming definitions
        name = media_info['name']
        filetype = media_info['filetype']

        # Make directory to store video frames and append new metadata to dictionary
        seq_folder = os.path.join(media_info['folder_path'], media_info['folder_name'] + '_seq')
        os.makedirs(seq_folder)
        media_info['seq_folder_path'] = seq_folder

        # Run FFMPEG to get video frames
        cmd = f'ffmpeg -i {name}.{filetype} {seq_folder}\\{name}%04d.png'
        subprocess.run(cmd, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Run Image Magick and convert each img to raw .rgb file format
        # Iterate over each .png file in the seq_folder_path
        for png_file in glob.glob(os.path.join(seq_folder, '*.png')):
            # Construct the output file path
            output = 'rgb:{}.rgb'.format(os.path.join(raw_folder, os.path.basename(png_file).replace('.png', '')))

            # Construct and run the command
            cmd = 'magick convert {} {}'.format(png_file, output)
            subprocess.run(cmd, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            # print(png_file, os.path.isfile(png_file))
            # print(output, os.path.isfile(output))

        exit()
        pass

def sox_effects(sox_params):
    # Make directory to store modified SOX image and add new meta data to media_info dictionary.
    output = os.path.join(media_info['folder_path'], media_info['folder_name'] + '_sox')
    media_info['sox_folder_path'] = output
    os.mkdir(output)

    if media_info['media_type'] == 'image':
        print(
            f"""
        {LIGHT_YELLOW}Applying audio effects...
        {MAGENTA}{sox_params}
        """)

        # Run SOX
        raw_file = os.path.join(media_info['raw_folder_path'], media_info['folder_name'])
        output = os.path.join(output, media_info['folder_name'])
        cmd = f'sox -t ul -c 1 -r 41k {raw_file}.rgb -t raw {output}_sox.rgb {sox_params}'
        subprocess.run(cmd, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    if media_info['media_type'] == 'video':
        print(sox_params, 'video')

def reconvert():
    # Reconvert raw .rgb back to its original file type
    og_file = os.path.join(media_info['sox_folder_path'], os.path.basename(media_info['sox_folder_path']))
    filetype = media_info['filetype']
    width = media_info['width']
    height = media_info['height']

    # For Output
    filename = os.path.join(media_info['folder_path'], media_info['name'] + '_fckt')
    media_info['fkt_filename'] = f'{filename}.{filetype}'  # Append to dictionary
    output = f'{filename}.{filetype}'

    # Execute conversion
    cmd = f'magick convert -size {width}x{height} -depth 8 rgb:{og_file}.rgb {output}'
    subprocess.run(cmd, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

@click.command()
@click.option('--load_media', '-l')
@click.option('--open_folder', '-o')
@click.option('--load_preset', '-lp')
@click.option('--info', '-i', is_flag=True)
@click.option('--sox_params', '-sox')
@click.option('--bypass', '-b', is_flag=True)
def click_params(load_media, open_folder, load_preset, info, sox_params, bypass):
    # load_media, open_folder, load_preset, info, sox_params, bypass
    options_list = [None, None, None, None, None, None]

    # Update list based on provided options
    if load_media:
        options_list[0] = load_media
    if open_folder:
        options_list[1] = open_folder
    if load_preset:
        options_list[2] = load_preset
    if info:
        options_list[3] = info
    if sox_params:
        options_list[4] = sox_params
    if bypass:
        options_list[5] = bypass

    startup(*options_list)

def startup(load_media=None, open_folder=None, load_preset=None, info=None, sox_params=None, bypass=None):
    global media_info

    if sox_params is None:
        path = 'sox_params.txt'
        # Open the file and read its contents
        with open(path, 'r') as file:
            sox_params = file.read()

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
                print(f'{LIGHT_YELLOW}Making directory: {DEFAULT}"{folder_path}"')


        # Make folder path and append new metatdata
        os.makedirs(folder_path)
        media_info['folder_path'] = folder_path
        media_info['folder_name'] = os.path.basename(folder_path)

        # If '-b or --bypass' flag is used then skip the user prompt.
        if bypass:
            fukitup_(sox_params=sox_params, user_prompt=False)
        else:
            fukitup_(sox_params=sox_params)

    if open_folder:
        print(open_folder)
    if load_preset:
        print(load_preset)
    if info:
        print(info)

def fukitup_(sox_params=None, user_prompt=None):
    if user_prompt:
        name = '"{}.{}"'.format(media_info['name'], media_info['filetype'])
        print(
            f"""
            {Fore.GREEN}{name}{LIGHT_YELLOW} successfully loaded.{DEFAULT}
            ------------------------------------------------
            | FUKITUP | 
              ^
            """
        )
        user_input = input('Watcha wanna do: ').lower()
        if user_input == 'f':
            convert_to_raw()  # Convert to raw .rgb files
            sox_effects(sox_params)  # Apply SOX effects to raw images
            reconvert()  # Reconvert raw .rgb files back to it's original file.
    else:
        convert_to_raw()  # Convert to raw .rgb files
        sox_effects(sox_params)  # Apply SOX effects to raw images
        reconvert()  # Reconvert raw .rgb files back to it's original file.

    exit()

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
    # load_media, open_folder, load_preset, info, sox_params
    options_list = [None, None, None, None, None]

    if user_input == 'l':
        options_list[0] = dequote(input(f'Media Path: '))
    if user_input == 'e':
        exit()

    return options_list

def load_menu():
    startup(*load_menu_txt())

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

    if args_len > 1:
        try:
            """Custom error handling for click"""
            click_params(standalone_mode=False)
        except click.ClickException as e:
            if args[0] == '-l' and args_len <= 2:
                user_input = input('Media Input: ')
                startup(load_media=user_input)
            else:
                click_error()


if __name__ == '__main__':
    main()
