import sys
import subprocess
import pkg_resources

# Check if requirements are satisfied
dependencies = ['click==8.1.7', 'Pillow', 'opencv-python']

def main():
    try:
        pkg_resources.require(dependencies)
    except:
        requirements()

def requirements():
    install_list = []
    install_prompt = []
    for item in dependencies:
        try:
            pkg_resources.require(item)
            # If requirement is already installed append value 0
            install_list.append([item, 0])
        except:
            # If requirement is NOT installed append value 1
            install_list.append([item, 1])
            install_prompt.append(item)
    check = sum(x[1] for x in install_list)
    if check > 0:
        while True:
            print('FUKITUP requires {prompt}'.format(prompt=install_prompt))
            answer = input('Install? (Y/N): ')
            answer = answer.upper()
            if answer == 'Y':
                for item in install_list:
                    if item[1] == 1:
                        requirement = item[0]
                        print('Installing', requirement, '(This may take awhile...)')
                        subprocess.check_call([sys.executable, '-m', 'pip', 'install', requirement])
                break
            if answer == 'N':
                print('Operation canceled')
                exit()
    else:
        pass

if __name__ == "__main__":
    main()
