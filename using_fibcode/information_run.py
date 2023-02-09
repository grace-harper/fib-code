import copy
import datetime as dt
import json
import logging
import os
import pprint
import sys
import time

from fib_code.classic_fib_decoder import ClassicFibDecoder
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


def setup_logging(udirpath, uniq):
    log_folder_path = os.path.join("FibCodeLogs", udirpath)
    if not os.path.exists(log_folder_path):
        os.makedirs(log_folder_path)

    log_file_path = os.path.join(log_folder_path, uniq + ".log")

    logger = logging.getLogger(uniq)
    f_handler = logging.FileHandler(log_file_path)
    f_format = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    f_handler.setFormatter(f_format)
    f_handler.setLevel(logging.INFO)
    logger.addHandler(f_handler)
    logger.setLevel(logging.INFO)

    results_path = "results"
    results_storage_path = os.path.join(results_path, udirpath, f"{uniq}")
    if not os.path.exists(results_storage_path):
        os.makedirs(results_storage_path)
    results_writer = write_results_wrapper(results_storage_path)

    return logger, results_writer


def run_decoder(logger, given_codeword, L, given_error, only_hori, only_verti):
    error = copy.deepcopy(given_error)
    decoder = ClassicFibDecoder(error, logger)
    decoder.decode_fib_code(only_hori=only_hori, only_verti=only_verti)
    decoder.board.shape = (L // 2, L)
    given_codeword.shape = (L // 2, L)
    return 1 if (decoder.board == given_codeword).all() else 0


def test_errors(
    logger,
    results_writer,
    error_generator,
    Lstack=[4, 8, 16, 32, 64],
    pstack=[0.2],
    round_count=10000,
):
    results = {}
    for p in pstack:
        curprobres = results[p] = {}  # new file
        curprobres["info"] = "Lsize"
        curprobres["roundsize"] = round_count

        for L_size in Lstack:
            curprobres[L_size] = {}
            # append to file

            verti_success = 0
            hori_success = 0
            norm_success = 0

            start = time.perf_counter()
            for i in range(round_count):
                logger.info(
                    f"Running at {dt.datetime.now()}... p={p}, L={L_size}  on round: {i}... current info is H:V:N={hori_success}:{verti_success}:{norm_success}"
                )

                codeword = generate_init_code_word(
                    L_size
                )  # generate an initial codeword. The default one bit at bottom center and cellular automata rules upward
                error_board, error_mask = error_generator(
                    codeword=codeword, probability_of_error=p
                )  # Add errors to your code!
                hori_success += run_decoder(
                    logger, codeword, L_size, error_board, True, False
                )
                verti_success += run_decoder(
                    logger, codeword, L_size, error_board, False, True
                )
                norm_success += run_decoder(
                    logger, codeword, L_size, error_board, False, False
                )

                if i % 100 == 0:
                    logger.info(f"Current Error Board: {error_board}")
            end = time.perf_counter()

            curprobres[L_size]["vertical_success"] = verti_success / round_count
            curprobres[L_size]["horizontal_success"] = hori_success / round_count
            curprobres[L_size]["both_success"] = norm_success / round_count
            curprobres[L_size]["runtime"] = end - start

            fin_line = f"FINISHED LP: @ {dt.datetime.now()} ---> L={L_size}, p={p},  H:V:N={hori_success/round_count}:{verti_success/round_count}:{norm_success/round_count}"
            logger.info(fin_line)
            print(fin_line)
        results_writer(curprobres, f"probability_of_error={p}")

    return results


def main(uniq):
    logger, results_writer = setup_logging("vertical_tracetrack_error", uniq)

    res = test_errors(
        logger,
        results_writer,
        generate_vertical_racetrack_error,
        Lstack=[16],
        pstack=[0.20],
        round_count=10,
    )


if __name__ == "__main__":
    main("test1")
