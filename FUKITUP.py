import click
import subprocess
import sys
import os

def read_default_script(config_file='config.txt'):
    """Reads and returns the default script name from the configuration file."""
    try:
        with open(config_file, 'r') as file:
            for line in file:
                if line.startswith('default_script='):
                    return line.strip().split('=')[1]
    except FileNotFoundError:
        pass
    return None

def construct_script_path(script_identifier=None):
    """Constructs the path to the script in the bin directory."""
    if script_identifier:
        script_path = os.path.join('bin', f'{script_identifier}.py')
    else:
        default_script = read_default_script()
        if default_script is None:
            print("No script specified and no default script found in config.")
            sys.exit(1)
        script_path = os.path.join('bin', f'{default_script}')

    if not os.path.exists(script_path):
        print(f"Script {script_path} does not exist in the bin directory.")
        sys.exit(1)

    return script_path

@click.command(context_settings=dict(ignore_unknown_options=True))
@click.argument('args', nargs=-1, type=click.UNPROCESSED)
def main(args):
    """Runs a script from the bin directory with given arguments."""
    if args and not args[0].startswith('-'):
        script_path = construct_script_path(args[0])
        script_args = args[1:]
    else:
        script_path = construct_script_path()
        script_args = args

    # Prepare and execute the command
    base = os.path.basename(script_path)
    print(f'Running: {base}')
    subprocess.run(['python', script_path] + list(script_args))

if __name__ == '__main__':
    main()