import copy
import logging
import sys

from fib_code.classic_fib_decoder import ClassicFibDecoder
from fib_code.code_generator import generate_init_code_word
from fib_code.error_generator import generate_swath_error
from fib_code.utils.logging_utils import new_logger_for_classic_fib_code_decoder


def test_errors(  # pylint: disable=
    hori_logger: logging.Logger,
    verti_logger: logging.Logger,
    normal_logger: logging.Logger,
    meta_logger: logging.Logger,
    L_pattern=None,
    p_pattern=None,
    denom_pattern=None,
    run_count=10,
    is_vertical=True,
):
    if not L_pattern:
        L_pattern = [16]

    if not p_pattern:
        p_pattern = [0.15]

    if not denom_pattern:
        denom_pattern = [3]
    verti_success = 0
    hori_success = 0
    norm_success = 0
    tot = 0
    for L in L_pattern:
        for p in p_pattern:
            for denom in denom_pattern:
                for i in range(run_count):
                    meta_logger.info(
                        f"running: L: {L} w p: {p} denom: {denom} on i: {i}"
                    )

                    codeword = generate_init_code_word(
                        L
                    )  # generate an initial codeword. The default one bit at bottom center and cellular automata rules upward
                    verti_error_board, verti_error_mask = generate_swath_error(
                        codeword,
                        L // denom,
                        probability_of_error=p,
                        is_vertical=is_vertical,
                    )  # Add errors to your code!
                    hori_error_copy = copy.deepcopy(verti_error_board)
                    verti_error_copy = copy.deepcopy(verti_error_board)
                    normal_error_copy = copy.deepcopy(verti_error_board)
                    hori_decoder = ClassicFibDecoder(hori_error_copy, hori_logger)
                    verti_decoder = ClassicFibDecoder(verti_error_copy, verti_logger)
                    normal_decoder = ClassicFibDecoder(normal_error_copy, normal_logger)

                    hori_decoder.decode_fib_code(only_hori=True)
                    verti_decoder.decode_fib_code(only_verti=True)
                    normal_decoder.decode_fib_code()

                    hori_decoder.board.shape = (L // 2, L)
                    verti_decoder.board.shape = (L // 2, L)
                    normal_decoder.board.shape = (L // 2, L)
                    if (hori_decoder.board == codeword).all():
                        hori_success += 1
                    if (verti_decoder.board == codeword).all():
                        verti_success += 1
                    if (normal_decoder.board == codeword).all():
                        norm_success += 1

                    tot += 1
    return hori_success, verti_success, norm_success, tot


if __name__ == "__main__":
    log_file_path = "logs"
    hori_code_logger_name = "hori_code"
    hori_logger = new_logger_for_classic_fib_code_decoder(
        log_file_path, hori_code_logger_name, logging.DEBUG
    )

    verti_code_logger_name = "verti_code"
    verti_logger = new_logger_for_classic_fib_code_decoder(
        log_file_path, verti_code_logger_name, logging.DEBUG
    )

    normal_code_logger_name = f"normal_code"
    normal_logger = new_logger_for_classic_fib_code_decoder(
        log_file_path, normal_code_logger_name, logging.DEBUG
    )

    meta_logger_name = f"meta_logger"
    meta_logger = new_logger_for_classic_fib_code_decoder(
        log_file_path, meta_logger_name, logging.DEBUG
    )

    vswath_hori, vswath_verti, vswath_norm, vswath_tot = test_errors(
        hori_logger,
        verti_logger,
        normal_logger,
        meta_logger,
        is_vertical=True,
    )
    verti_inf = f"On Vertical swath:\n hori success: {vswath_hori/vswath_tot} and verti success: {vswath_verti/vswath_tot} and normal: {vswath_norm/vswath_tot}"
    print(verti_inf)
    meta_logger.info(f"VERTICAL\n:{verti_inf}")

    hswath_hori, hswath_verti, hswath_norm, hswath_tot = test_errors(
        hori_logger,
        verti_logger,
        normal_logger,
        meta_logger,
        is_vertical=False,
    )
    hori_inf = f"On Hori swath:\n hori success: {hswath_hori/hswath_tot} and verti success: {hswath_verti/hswath_tot} and normal: {hswath_norm/hswath_tot}"
    print(hori_inf)
    meta_logger.info(f"HORIZONTAL\n:{hori_inf}")
