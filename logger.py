import logging
import os
import sys

def initialise_logger(log_folder: str, name: str) -> logging.Logger:
    '''Creates a timestamped logger with three handlers; a debug file, an info stream, and an error stream.
Debug log files are stored in a singular file providing a history for every individual run session.
A linked debug log file is also provided as the 0th log file, linking to the latest log file.
Time of creatation is also stamped at the beginning of the info stream and debug file.'''
    #generate log filename
    iteration = 1
    for log in os.listdir(log_folder):
        try:
            if os.path.splitext(log)[1] == os.path.extsep+'log' and int(os.path.splitext(log)[0]) >= iteration:
                iteration = int(os.path.splitext(log)[0]) + 1
        except ValueError:
            continue
    log_file = os.path.join(log_folder, str(iteration)+os.path.extsep+'log')

    #create formatter
    stamp_format = logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s', '%d/%m/%Y %H:%M:%S')

    #create full file handler
    full_file_handler = logging.FileHandler(log_file, mode='x')
    full_file_handler.setFormatter(stamp_format)
    full_file_handler.setLevel(logging.DEBUG)

    #create info stream handler
    info_stream_handler = logging.StreamHandler(sys.stdout)
    info_stream_handler.setFormatter(stamp_format)
    info_stream_handler.setLevel(logging.INFO)

    #create error stream handler
    error_stream_handler = logging.StreamHandler(sys.stderr)
    error_stream_handler.setFormatter(stamp_format)
    error_stream_handler.setLevel(logging.ERROR)

    #create logger
    logger = logging.Logger(name)
    logger.addHandler(full_file_handler)
    logger.addHandler(info_stream_handler)
    logger.addHandler(error_stream_handler)
    logger.info('Log started.')

    #generate latest log filename
    latest_log = os.path.join(log_folder, '0_latest.log')

    #delete old latest log
    try:
        os.remove(latest_log)
    except FileNotFoundError:
        pass

    #link latest log
    os.link(log_file, latest_log)
    return logger
