import datetime
import logging
import os




def get_or_create_logger(log_file_path, log_level):
   logger = logging.getLogger(log_file_path)  # creates if not exists
    f_handler = logging.FileHandler(
        os.path.join(log_file_path)
    )  # TODO remove hardcoded logs, make init resonsible for creating log dir tho
    f_format = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    f_handler.setFormatter(f_format)
    f_handler.setLevel(log_level)
    logger.addHandler(f_handler)
    logger.setLevel(log_level)
   

def new_logger_for_classic_fib_code_decoder(
    log_folder_path: str,
    name: str,
    log_level,
) -> logging.Logger:

    tt = datetime.datetime.now()
    unique_log_info = f"{name}_{tt}"
    logger = logging.getLogger(unique_log_info)  # TODO -- find better way to log output
    f_handler = logging.FileHandler(
        os.path.join(log_folder_path, unique_log_info + "ClassicFibCode_probs.log")
    )  # TODO remove hardcoded logs, make init resonsible for creating log dir tho
    f_format = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    f_handler.setFormatter(f_format)
    f_handler.setLevel(log_level)
    logger.addHandler(f_handler)
    logger.setLevel(log_level)

    return logger
