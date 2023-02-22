import copy
import datetime as dt
import json
import logging
import os
import pprint
import sys
import time

import numpy as np
from fib_code.classic_fib_decoder import ClassicFibDecoder, FibCodeMetadata
from fib_code.code_generator import generate_init_code_word
from fib_code.error_generator import (
    generate_racetrack_error,
    generate_vertical_racetrack_error,
)

ERROR_TYPE = "error_type"
V_RACETRACK = "vertical_racetrack"
H_RACETRACK = "horizontal_racetrack"
HORI = "horizontal decoder"
VERTI = "vertical decoder"
BOTH = "both decoder"

round_size = "rounds_size"
success_rate = "success_rate"


def write_results_wrapper(res_folder):
    def write_results(results, info):
        filename = info + "_results.txt"
        res_file_store_path = os.path.join(res_folder, filename)
        with open(res_file_store_path, "w") as f:
            json.dump(results, f, indent=4)

    return write_results


def setup_logging(log_folder_path, results_folder_path, uniq):
    cur_run_log_folder_path = os.path.join(log_folder_path, uniq)
    if not os.path.exists(cur_run_log_folder_path):
        os.makedirs(cur_run_log_folder_path)

    log_file_path = os.path.join(cur_run_log_folder_path, f"{uniq}.log")

    logger = logging.getLogger(uniq)
    f_handler = logging.FileHandler(log_file_path)
    f_format = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    f_handler.setFormatter(f_format)
    f_handler.setLevel(logging.INFO)
    logger.addHandler(f_handler)
    logger.setLevel(logging.INFO)

    results_storage_path = os.path.join(results_folder_path, f"{uniq}")
    if not os.path.exists(results_storage_path):
        os.makedirs(results_storage_path)
    results_writer = write_results_wrapper(results_storage_path)

    return logger, results_writer


def run_decoder(logger, given_codeword, L, given_error, probes):
    error = copy.deepcopy(given_error)
    decoder = ClassicFibDecoder(error, logger, probe_fundamental_indices=probes)
    decoder.decode_fib_code(meta_only=True)
    decoder.board.shape = (L // 2, L)
    given_codeword.shape = (L // 2, L)
    return 1 if (decoder.board == given_codeword).all() else 0


def test_errors(logger, results_writer, infodict):
    error_board = np.array(infodict["error_board"])
    print(error_board)
    L_size = infodict["L"]
    i = infodict["round"]
    good_hori_delta = infodict["H"]
    good_verti_delta = infodict["V"]
    good_norm_delta = infodict["N"]

    codeword = generate_init_code_word(L=L_size)
    fb = FibCodeMetadata(L_size)
    start = time.perf_counter()

    labels = ["hori", "verti", "norm"]
    good = [good_hori_delta, good_verti_delta, good_norm_delta]
    current = [
        run_decoder(
            logger, codeword, L_size, error_board, [fb.fundamental_hori_probe_indx]
        ),
        run_decoder(
            logger, codeword, L_size, error_board, [fb.fundamental_verti_probe_indx]
        ),
        run_decoder(
            logger,
            codeword,
            L_size,
            error_board,
            [fb.fundamental_hori_probe_indx, fb.fundamental_verti_probe_indx],
        ),
    ]

    for l, g, v in zip(labels, good, current):
        assert g == v, f"{l} FAILED with {v} instead of expected {g}"


def main(uniq):
    fib_code_log_path = "/Users/graceharperibm/correcting/Fib/ClassicFibInfo/logfib"
    results_folder_path = "/Users/graceharperibm/correcting/Fib/ClassicFibInfo/results"

    logger, results_writer = setup_logging(fib_code_log_path, results_folder_path, uniq)

    info = "/Users/graceharperibm/correcting/Fib/ClassicFibInfo/logfib/get_small_runs/exp_{}.json"

    for i in range(1, 13):
        fileinfo = info.format(i)
        cinfo = ""
        with open(fileinfo, "r") as f:
            cinfo = json.load(f)
        test_errors(logger, results_writer, cinfo)


main("trash")
