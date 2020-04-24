from stitcher import Stitcher
import os

def main():
    COM_SEP = ' '
    PROMPT = '{0}> '
    TEMPLATE_COM = 'template'
    NAVIGATE_COM = 'nav'
    SUB_DIR_COM = 'list'
    CLOSE_COM = 'close'
    AID_COM = 'help'
    COM_ERROR = 'Command not recognised!'
    
    directory = os.path.abspath('.')
    aid()
    while True:
        com = input(PROMPT.format(directory))
        try:
            if com.partition(COM_SEP)[0] == CLOSE_COM:
                close()
            elif com.partition(COM_SEP)[0] == AID_COM:
                aid()
            elif com.partition(COM_SEP)[0] == NAVIGATE_COM:
                directory = navigate(directory, com.partition(COM_SEP)[2])
            elif com.partition(COM_SEP)[0] == SUB_DIR_COM:
                subDirectories(directory)
            elif com.partition(COM_SEP)[0] == TEMPLATE_COM:
                template(directory, com.split(COM_SEP)[1], com.split(COM_SEP)[2])
            else:
                print(COM_ERROR)
        except IndexError:
            print(COM_ERROR)

def close():
    raise SystemExit

def aid():
    CLOSE_HELP = 'close: close the program'
    AID_HELP = 'help: display this help text'
    NAVIGATE_HELP = 'nav *rel_path*: navigate your direcctory.\n\t*rel_path*: a path to navigate to that is relative to the current directory (\'..\' for the parent path)'
    SUB_DIRECTORIES_HELP = 'list: list all the files and folders in the current directory'
    TEMPLATE_HELP = 'template *in_filename* *out_filename*: stitch HTML files from the current directory into the input file and write it to the output file\n\t*in_filename*: the template filename relative to the current directory\n\t*out_filename*: the name of the output file relative to the current directory'

    print(CLOSE_HELP)
    print(AID_HELP)
    print(NAVIGATE_HELP)
    print(SUB_DIRECTORIES_HELP)
    print(TEMPLATE_HELP)
    print()

def navigate(directory: str, addend: str):
    PATH_ERROR = '{0} is not a valid directory!\n'
    
    new_path = os.path.abspath(os.path.join(directory, addend))
    if not os.path.isdir(new_path):
        print(PATH_ERROR.format(new_path))
        return directory
    else:
        subDirectories(new_path)
        return new_path

def subDirectories(directory: str):
    HEAD = 'Files and folders in the current directory are:'

    print(HEAD)
    for file in os.listdir(directory):
        print(file)
    print()

def template(directory: str, in_file: str, out_file: str = None):
    OUT_PREFIX = 'out_'
    FEEDBACK = 'Finished stitching in {0}'
    ERROR = 'Error: {0}!'

    if out_file == None:
        out_file = OUT_PREFIX + in_file
    try:
        Stitcher(directory, in_file, out_file)
        print(FEEDBACK.format(os.path.join(directory, out_file)))
    except Exception as e:
        raise
        print(ERROR.format(e))
    print()

if __name__ == '__main__':
    main()
