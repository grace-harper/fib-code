import datetime
import logging
import os


def new_logger_for_classic_fib_code_decoder(
    log_folder_path: str,
    name: str,
    log_level,
) -> logging.Logger:
    """Creates a new logger that can be passed to the decoder

    Args:
        log_folder_path (str): Path to folder where logs should be written to
        name (str): Identifying information about the decoder instance this logger will be passed to. Will be used when naming logger and naming logfile.
        log_level (logging._Level): Minimum level logger should log. Note, setting this to logging.NOTSET causes the logging not to log anything

    Returns:
        logging.Logger: Logger to be passed to decoder.
    """
    tt = datetime.datetime.now()
    unique_log_info = f"{name}_{tt}"
    if log_level == logging.NOTSET:  # Then turn off logging
        logger = logging.getLogger(
            unique_log_info
        )  # TODO -- find better way to  not log output
        logger.addFilter(lambda record: 0)
        logger.setLevel(log_level)
        return logger
    # Create a custom logger
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
