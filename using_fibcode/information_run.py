import copy
import json
import logging
import pprint
import sys

from fib_code.classic_fib_decoder import ClassicFibDecoder
from fib_code.code_generator import generate_init_code_word
from fib_code.error_generator import generate_swath_error
from fib_code.utils.logging_utils import new_logger_for_classic_fib_code_decoder

HORI = "horizontal decoder"
VERTI = "vertical decoder"
BOTH = "both decoder"

round_size = "rounds_size"
success_rate = "success_rate"


def run_decoder(logger, given_codeword, L, given_error, only_hori, only_verti):
    error = copy.deepcopy(given_error)
    decoder = ClassicFibDecoder(error, logger)
    decoder.decode_fib_code(only_hori=only_hori, only_verti=only_verti)
    decoder.board.shape = (L // 2, L)
    given_codeword.shape = (L // 2, L)
    return 1 if (decoder.board == given_codeword).all() else 0


def test_errors(
    logger, Lstack=[16, 32], pstack=[0.15, 0.2], denomstack=[3, 4, 5], round_count=10000
):
    results = {}

    HORI = "horizontal decoder"
    VERTI = "vertical decoder"
    BOTH = "both decoder"

    round_size = "rounds_size"
    success_rate = "success_rate"
    results[HORI] = {}
    results[VERTI] = {}
    results[BOTH] = {}

    for ERROR_TYPE in ["horizontal_errors", "vertical_errors"]:
        results[HORI][ERROR_TYPE] = {}
        results[VERTI][ERROR_TYPE] = {}
        results[BOTH][ERROR_TYPE] = {}

        for L in Lstack:
            results[HORI][ERROR_TYPE][L] = {}
            results[VERTI][ERROR_TYPE][L] = {}
            results[BOTH][ERROR_TYPE][L] = {}
            for p in pstack:
                results[HORI][ERROR_TYPE][L][p] = {}
                results[VERTI][ERROR_TYPE][L][p] = {}
                results[BOTH][ERROR_TYPE][L][p] = {}
                for denom in denomstack:
                    results[HORI][ERROR_TYPE][L][p][denom] = {round_size: round_count}
                    results[VERTI][ERROR_TYPE][L][p][denom] = {round_size: round_count}
                    results[BOTH][ERROR_TYPE][L][p][denom] = {round_size: round_count}

                    verti_success = 0
                    hori_success = 0
                    norm_success = 0
                    tot = 0
                    for i in range(round_count):
                        logger.info(
                            f"Running {tot} run...{L}, {p}, {denom}, {i}... current info is hori_success:{hori_success}, verti_success:{verti_success}, norm_success{norm_success}"
                        )
                        codeword = generate_init_code_word(
                            L
                        )  # generate an initial codeword. The default one bit at bottom center and cellular automata rules upward
                        errors_are_vertical = "vertical" in ERROR_TYPE
                        error_board, verti_error_mask = generate_swath_error(
                            codeword,
                            L // denom,
                            probability_of_error=p,
                            is_vertical=errors_are_vertical,
                        )  # Add errors to your code!
                        hori_success += run_decoder(
                            logger, codeword, L, error_board, True, False
                        )
                        verti_success += run_decoder(
                            logger, codeword, L, error_board, False, True
                        )
                        norm_success += run_decoder(
                            logger, codeword, L, error_board, False, False
                        )

                    results[HORI][ERROR_TYPE][L][p][denom][success_rate] = (
                        hori_success / round_count
                    )
                    results[VERTI][ERROR_TYPE][L][p][denom][success_rate] = (
                        verti_success / round_count
                    )
                    results[BOTH][ERROR_TYPE][L][p][denom][success_rate] = (
                        norm_success / round_count
                    )

    return results


def main():
    log_folder_path = "logs"
    logger = new_logger_for_classic_fib_code_decoder(
        log_folder_path, "FibCodeLogs", logging.INFO
    )
    res = test_errors(logger)
    with open("results.txt", "w") as f:
        json.dump(res, f)


if __name__ == "__main__":
    main()
