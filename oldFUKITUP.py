########################
# OLD CODE
########################

from colorama import init, Fore, Style

# Initialize Colorama
init(autoreset=True)

# Custom Colors
DEFAULT = Style.RESET_ALL
LIGHT_YELLOW = '\033[93m'
MAGENTA = '\033[95m'
ORANGE = '\033[38;5;202m'

from PIL import Image
import subprocess
import click
import glob
import json
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
    # Folder paths
    raw_folder = os.path.join(media_info['folder_path'], media_info['folder_name'] + '_raw')
    output = 'rgb:{}.rgb'.format(raw_folder + '\\' + media_info['folder_name'])

    # Make directory to store RAW images and append new metadata to dictionary
    os.makedirs(raw_folder)
    media_info['raw_folder_path'] = raw_folder
    re_save_dictionary(media_info, media_info['json_file_path'])

    # Determine media type
    if media_info['media_type'] == 'image':
        print(f'{LIGHT_YELLOW}Creating Raw Images...')

        # Run Image Magick and convert the img to raw .rgb file format.
        cmd = 'magick convert "{}" "{}"'.format(media_info['media_path'], output)
        subprocess.run(cmd, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    if media_info['media_type'] == 'video':

        # Naming definitions
        name = media_info['name']
        media_path = media_info['media_path']
        filetype = media_info['filetype']

        # Make directory to store video frames and append new metadata to dictionary
        seq_folder = os.path.join(media_info['folder_path'], media_info['folder_name'] + '_seq')
        os.makedirs(seq_folder)
        media_info['seq_folder_path'] = seq_folder
        re_save_dictionary(media_info, media_info['json_file_path'])

        # Run FFMPEG to get video frames
        cmd = f'ffmpeg -i "{media_path}" "{seq_folder}\\{name}%04d.png"'
        subprocess.run(cmd, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Run Image Magick and convert each img to raw .rgb file format
        # Iterate over each .png file in the seq_folder_path
        for png_file in glob.glob(os.path.join(seq_folder, '*.png')):
            # Construct the output file path
            output = 'rgb:{}.rgb'.format(os.path.join(raw_folder, os.path.basename(png_file).replace('.png', '')))

            # Clear the current line and print the status message
            sys.stdout.write("\r\033[K")  # Clear the line
            status_message = f'{LIGHT_YELLOW}Creating Raw Image:{ORANGE} "{png_file}"'
            sys.stdout.write(status_message)
            sys.stdout.flush()

            # Construct and run the command
            cmd = 'magick convert "{}" "{}"'.format(png_file, output)
            subprocess.run(cmd, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Move to the next line after the loop completes
        sys.stdout.write('\n')
        sys.stdout.flush()

def sox_effects(sox_params):
    # Make directory to store modified SOX image and add new metadata to media_info dictionary.
    output = os.path.join(media_info['folder_path'], media_info['folder_name'] + '_sox')
    media_info['sox_folder_path'] = output
    re_save_dictionary(media_info, media_info['json_file_path'])

    # Skip over folder if it already exists
    if not os.path.exists(output):
        os.mkdir(output)

    # Apply SOX audio effects to raw image
    # Determine media type
    if media_info['media_type'] == 'image':

        # Naming definitions
        raw_file = os.path.join(media_info['raw_folder_path'], media_info['folder_name'])
        output = os.path.join(output, media_info['folder_name'])

        print(
            f"""
        {LIGHT_YELLOW}Applying audio effects...
        {MAGENTA}{sox_params}
        """)

        # Run SOX
        cmd = f'sox -t ul -c 1 -r 41k "{raw_file}.rgb" -t raw "{output}_sox.rgb" {sox_params}'
        try:
            subprocess.run(cmd, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except subprocess.CalledProcessError as e:
            # Print only the stderr if it's not None
            print('An error occurred: {}'.format(e.stderr.decode()))
            exit()

    if media_info['media_type'] == 'video':
        # Variable Definitions
        raw_file = media_info['raw_folder_path']
        num_lines_in_status_message = 2

        # ANSI escape codes for status message
        def clear_lines(num_lines):
            # Move up one line and clear line
            for _ in range(num_lines):
                sys.stdout.write("\033[A\033[K")

        # Iterate over each .png file in the seq_folder_path
        for rgb_file in glob.glob(os.path.join(raw_file, '*.rgb')):
            frame = os.path.basename(rgb_file)
            raw_cursor = os.path.join(raw_file, frame)
            sox_output = os.path.join(output, os.path.splitext(frame)[0] + '_sox' + os.path.splitext(frame)[1])

            status_message = f"""
                {LIGHT_YELLOW}Applying audio effects to {ORANGE}"{frame}"
                {MAGENTA}{sox_params}
            """

            # Clear previous message
            if rgb_file != glob.glob(os.path.join(raw_file, '*.rgb'))[0]:  # Skip clearing for the first file
                clear_lines(num_lines_in_status_message + 1)

            # Print status
            sys.stdout.write(status_message)
            sys.stdout.flush()  # Clear the buffer

            # Run SOX
            cmd = f'sox -t ul -c 1 -r 41k "{raw_cursor}" -t raw "{sox_output}" {sox_params}'
            try:
                subprocess.run(cmd, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            except subprocess.CalledProcessError as e:
                # Print only the stderr if it's not None
                print('An error occurred: {}'.format(e.stderr.decode()))
                exit()

        sys.stdout.write('\n')  # Move to the next line after the loop completes
        sys.stdout.flush()


def reconvert():
    print(f'{LIGHT_YELLOW}Re-converting raw files back to png.')

    # Folder where the .rgb files are located
    sox_folder_path = media_info['sox_folder_path']
    height = media_info['height']
    width = media_info['width']

    if media_info['media_type'] == 'image':
        filetype = media_info['filetype']

    if media_info['media_type'] =='video':
        # Make new directory to store newly created images
        new_path = os.path.join(media_info['folder_path'], media_info['name'] + '_fckt')
        media_info['seq_fckt_folder_path'] = new_path
        filetype = 'png'

        # Skip over folder if it already exists
        if not os.path.exists(new_path):
            os.mkdir(new_path)

    # Iterate over each .rgb file in the sox_folder_path
    for rgb_file in glob.glob(os.path.join(sox_folder_path, '*.rgb')):
        # Variable declarations
        new_filename = os.path.basename(rgb_file).replace('.rgb', '_fckt')
        basename = os.path.basename(rgb_file)
        output = ''
        cmd = ''

        if media_info['media_type'] == 'image':
            output = os.path.join(media_info['folder_path'], new_filename + f'.{filetype}')
            cmd = f'magick convert -size {width}x{height} -depth 8 rgb:"{rgb_file}" "{output}"'

            # Update dictionary with the new output filename metadata.
            media_info['fkt_filename'] = output
            re_save_dictionary(media_info, media_info['json_file_path'])

        if media_info['media_type'] == 'video':
            output = os.path.join(f'{new_path}', f'{new_filename}.{filetype}')
            cmd = f'magick convert -size {width}x{height} -depth 8 rgb:"{rgb_file}" "{output}"'

        # Clear the current line and print the status message
        sys.stdout.write("\r\033[K")
        status_message = f'{LIGHT_YELLOW}Converting {ORANGE}"{basename}"{LIGHT_YELLOW} to {ORANGE}"{filetype}"'
        sys.stdout.write(status_message)
        sys.stdout.flush()

        # Execute conversion for each file
        subprocess.run(cmd, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    sys.stdout.write('\n')  # Move to the next line after the loop completes
    sys.stdout.flush()

def create_video_from_images():
    # If file format is video, convert image sequence into .mp4
    if media_info['media_type'] == 'video':
        seq_folder_path = media_info['seq_fckt_folder_path']
        output_folder_path = media_info['folder_path']
        output_video_file = os.path.join(output_folder_path, media_info['name'] + '_fckt.mp4')
        name =  media_info['name']
        framerate = media_info['fps']

        # Construct the FFmpeg command
        # The pattern "kev%04d_sox_fckt.png" assumes that the numbering in the filenames is zero-padded to 4 digits
        cmd = [
            'ffmpeg',
            '-framerate', str(framerate),  # Set the input frame rate
            '-i', os.path.join(seq_folder_path, f'{name}%04d_sox_fckt.png'),  # Input file pattern
            '-c:v', 'libx264',  # Set the video codec to libx264 for H.264
            '-pix_fmt', 'yuv420p',  # Set pixel format to yuv420p for compatibility
            '-vf', 'format=yuv420p',  # This ensures the output uses a pixel format compatible with most players
            output_video_file  # Output file path
        ]
        print(cmd)
        # Run the FFmpeg command
        subprocess.run(cmd, check=True)

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

    ####################################################################################################################
    # LOAD MEDIA
    ####################################################################################################################
    if load_media:
        media_info = get_media_info(load_media)
        base_folder_name = f"{media_info['name']}_fck"
        folder_path = os.path.join(media_info['root_path'], base_folder_name)

        if os.path.exists(folder_path):
            print(
                f"""
                {ORANGE}"{base_folder_name}" {DEFAULT}already exists...
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

        # Make directory to store contents
        os.makedirs(folder_path)

        # Make 'media_info.json' file and store in 'folder_path'
        json_file_path = os.path.join(folder_path, 'media_info.json')
        media_info['json_file_path'] = json_file_path
        with open(json_file_path, 'w') as json_file:
            json.dump(media_info, json_file, indent=4)

        # Append new metatdata
        media_info['folder_path'] = folder_path
        media_info['folder_name'] = os.path.basename(folder_path)

        # If '-b or --bypass' flag is used then skip the user prompt.
        if bypass:
            fukitup_(sox_params=sox_params, user_prompt=False)
        else:
            fukitup_(sox_params=sox_params, user_prompt=True)

    ####################################################################################################################
    # OPEN FOLDER
    ####################################################################################################################
    if open_folder:
        # Check if path exists
        if os.path.exists(open_folder):
            # Load media info from .json
            load_dictionary_from_json(os.path.join(open_folder, 'media_info.json'))

            successful_load()

            user_input = input(f'Whatcha wanna do: ').lower()
            if user_input == 'f':
                sox_effects(sox_params)  # Apply SOX effects to raw images
                reconvert()  # Reconvert raw .rgb files back to its original file.
                create_video_from_images()
        else:
            print(f'{Fore.RED}ERROR: Folder "{open_folder}" does not exist.')
        exit()
    if load_preset:
        print(load_preset)
    if info:
        print(info)

# Saves dictionary as a .json given a provided 'path'
def save_dictionary_as_json(dictionary, path):
    if isinstance(dictionary, dict):
        # Save the dictionary as a JSON file
        with open(path, 'w') as json_file:
            json.dump(dictionary, json_file, indent=4)
    else:
        return "Error: The variable is not a dictionary."

my_dict = {'name': 'John', 'age': 30, 'city': 'New York'}

# Loads .json file as a dictionary
def load_dictionary_from_json(json_path, specified_name=None):
    # Check if the JSON file exists
    if not os.path.exists(json_path):
        return "Error: JSON file does not exist."

    # Load the dictionary from the JSON file
    with open(json_path, 'r') as json_file:
        dictionary = json.load(json_file)

    # Determine the dictionary's name
    if specified_name is None:
        specified_name = os.path.splitext(os.path.basename(json_path))[0]

    # Assign the loaded dictionary to a global variable with the specified name
    globals()[specified_name] = dictionary
    return f"Dictionary loaded as '{specified_name}'"

# Save the specified 'dictionary' to 'json_path'
def re_save_dictionary(dictionary, json_path):
    # Ensure the provided object is a dictionary
    if not isinstance(dictionary, dict):
        return "Error: Provided object is not a dictionary."

    # Save the dictionary to the specified JSON file
    with open(json_path, 'w') as json_file:
        json.dump(dictionary, json_file, indent=4)

    return "Dictionary saved successfully."

def successful_load():
    name = '"{}.{}"'.format(media_info['name'], media_info['filetype'])
    print(
        f"""
        {Fore.GREEN}{name}{LIGHT_YELLOW} successfully loaded.{DEFAULT}
        ------------------------------------------------
        | FUKITUP | 
          ^
        """
    )

def fukitup_(sox_params=None, user_prompt=None):
    if user_prompt: # Bypass the prompt if '-b' or '--bypass' flag is used
        name = '"{}.{}"'.format(media_info['name'], media_info['filetype'])

        successful_load()

        user_input = input('Watcha wanna do: ').lower()
        if user_input == 'f':
            convert_to_raw()  # Convert to raw .rgb files
            sox_effects(sox_params)  # Apply SOX effects to raw images
            reconvert()  # Reconvert raw .rgb files back to its original file.
            create_video_from_images()
    else:
        convert_to_raw()  # Convert to raw .rgb files
        sox_effects(sox_params)  # Apply SOX effects to raw images
        reconvert()  # Reconvert raw .rgb files back to its original file.
        create_video_from_images()

    print('DONE')
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
    if user_input == 'o':
        options_list[1] = dequote(input(f'Media Path: '))
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
