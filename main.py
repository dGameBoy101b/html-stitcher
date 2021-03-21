from stitcher import Stitcher
import os
from logger import initialise_logger

def main():
    COM_SEP = ' '
    PROMPT = '{0}> '
    TEMPLATE_COM = 'template'
    NAVIGATE_COM = 'nav'
    SUB_DIR_COM = 'list'
    CLOSE_COM = 'close'
    AID_COM = 'help'
    CLEAN_COM = 'cleanup'
    COM_ERROR = 'Command not recognised!'
    LOGS_DIR = os.path.abspath('./logs')

    logger = initialise_logger(LOGS_DIR, __name__)
    directory = os.path.abspath('.')
    aid()
    while True:
        com = input(PROMPT.format(directory))
        prefix = com.partition(COM_SEP)[0]
        args = com.split(COM_SEP)[1:]
        try:
            if prefix == CLOSE_COM:
                close()
            elif prefix == AID_COM:
                aid()
            elif prefix == NAVIGATE_COM:
                directory = navigate(directory, args[0])
            elif prefix == SUB_DIR_COM:
                subDirectories(directory)
            elif prefix == TEMPLATE_COM:
                template(directory, args[0], args[1], logger=logger)
            elif prefix == CLEAN_COM:
                cleanup(directory, logger=logger)
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
    CLEANUP_HELP = 'cleanup: cleanup all the temporary files in the current directory'

    print(CLOSE_HELP)
    print(AID_HELP)
    print(NAVIGATE_HELP)
    print(SUB_DIRECTORIES_HELP)
    print(TEMPLATE_HELP)
    print(CLEANUP_HELP)
    print()
    return

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
    return

def template(directory: str, in_file: str, out_file: str = None, passes: int = -1, logger = None):
    OUT_PREFIX = 'out_'
    FEEDBACK = 'Finished stitching in {0}'
    ERROR = 'Error: {0}!'

    if out_file == None:
        out_file = OUT_PREFIX + in_file
    try:
        Stitcher(directory, in_file, out_file, passes, logger)
        if logger is None:
            print(FEEDBACK.format(os.path.join(directory, out_file)))
        else:
            logger.info(FEEDBACK.format(os.path.join(directory, out_file)))
    except Exception as e:
        if logger is None:
            print(ERROR.format(e))
        else:
            logger.error(e)
        raise
    print()
    return

def cleanup(directory: str, logger = None):
    TMP_SUFFIX = '.tmp'
    FEEDBACK = 'Cleaned {} files up'
    FEEDBACK_ONE = 'Cleaned 1 file up'

    #find temp files
    to_clean = list()
    for file in os.listdir(directory):
        if os.path.splitext(file)[1] == TMP_SUFFIX:
            to_clean.append(file)

    #remove temp files
    for file in to_clean:
        if logger is not None:
            logger.info(f'Cleaning up {file}')
        os.remove(os.path.join(directory, file))

    #report success
    
    if len(to_clean) == 1:
        message = FEEDBACK_ONE
    else:
        message = FEEDBACK.format(len(to_clean))
    if logger is None:
        print(message)
    else:
        logger.info(message)
    print()
    return

if __name__ == '__main__':
    main()
