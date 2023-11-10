import click
import sys

load_menu         = '| Load Media | Open Folder | Load Preset | Info | '
load_menu_pointer = '  ^            ^             ^    ^        ^'


@click.command()
@click.option('--load_media', '-l')
@click.option('--open_folder', '-o')
@click.option('--load_preset', '-lp')
@click.option('--info', '-i', is_flag=True)
def startup(load_media, open_folder, load_preset, info):
    if load_media:
        print('load media')
    if open_folder:
        print('open folder')
    if load_preset:
        print(load_preset)
    if info:
        print('info')

# Custom error handling for parameters
def main():
    args = sys.argv[1:]  # Get command line arguments except the filename
    try:
        startup(standalone_mode=False)
    except click.ClickException as e:
        if '-l' in args:
            print('Yup')
        elif '-lp' in args:
            print("Error related to load preset option:", e.message)
        elif '-o' in args:
            print("Error related to open folder option:", e.message)
        elif '-i' in args:
            print("Error related to info option:", e.message)
        else:
            print("General Error:", e.message)


if __name__ == '__main__':
    main()
