# test iid
import logging

import numpy as np

from fib_code.classic_fib_decoder import ClassicFibDecoder
from fib_code.code_generator import generate_init_code_word
from fib_code.error_generator import generate_swath_error
from fib_code.utils.logging_utils import new_logger_for_classic_fib_code_decoder

""" 
L=8: [ #(error_prob, fail_rate, num_shots) ]
L=16:[]

[
    [8, (),()],
    [16,()],
    ...
]

"""

all_L = [4]

# threshold_logger = new_logger_for_classic_fib_code_decoder(0, f"ThresholdLog", logging.INFO) # too many logs rip x_x
res_file = "results.txt"

results = []
num_shots = 1000
for L in all_L:
    l_row = []
    for p in np.linspace(0.01, 0.2, 10):
        if L == 32 and p < 0.06:
            continue
        success_no = 0
        for round in range(num_shots):
            codeword = generate_init_code_word(
                L
            )  # generate an initial codeword. The default one bit at bottom center and cellular automata rules upward
            error_board, error_mask = generate_swath_error(
                codeword, L, probability_of_error=p
            )  # setting width to L and vertical=True makes iid noise
            f = ClassicFibDecoder(error_board)  # give this class the errored codeword
            f.decode_fib_code()
            f.board.shape = (L // 2, L)
            if (f.board == codeword).all():
                success_no += 1
        p_info = (p, success_no / num_shots)
        l_row.append(p_info)
        print(p_info)

    with open(res_file, "a") as f:
        f.write("\n")
        f.write(str(L))
        f.write(str(l_row))
    results.append(l_row)
