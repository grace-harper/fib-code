# https://www.youtube.com/watch?v=RHyE_erqAe0,
import copy
import logging
import math
import unittest

import numpy as np
from fib_code.classic_fib_decoder import ClassicFibDecoder
from fib_code.code_generator import generate_init_code_word
from fib_code.error_generator import generate_swath_error


class ClassicFibCodeTest(unittest.TestCase):
    """sanity checks"""

    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)
        self.logger = self.dead_logger()

    def dead_logger(self):
        return logging.getLogger("dummy")

    def test_basic(self):
        f = generate_init_code_word(L=8)

    def test_bit_representation_trans(self):
        decoder = ClassicFibDecoder(generate_init_code_word(32), self.logger)  # L = 32
        trans_tests = [
            [(0, 0), 0],
            [(4, 1), 129],
            [(15, 3), 483],
            [(0, 31), 31],
            [(1, 31), 63],
            [(15, 31), 511],
            [(6, 19), 211],
        ]
        for test in trans_tests:
            rc = test[0]
            sol = test[1]
            assert (
                decoder.rc_to_bit(rc[0], rc[1]) == sol
            ), f"{rc} did not convert to correct bit rep: {sol}"

        for test in trans_tests:
            bit = test[1]
            sol = test[0]
            assert (
                decoder.bit_to_rc(bit) == sol
            ), f"{bit} did not convert to correct rc rep: {sol}"

    def test_x_shift(self):
        for L in [4, 8, 16, 32]:
            decoder = ClassicFibDecoder(generate_init_code_word(L), self.logger)
            input = np.array(list(range((L**2) // 2)))

            # shift_by_x
            # shift by 1
            shiftby1 = np.array(
                [
                    [(L * (row + 1)) - 1] + list(range((L * row), (L * row) + L - 1))
                    for row in range(L // 2)
                ]
            )
            shiftby1.shape = (L**2) // 2

            xtests = [[L, np.array(list(range((L**2) // 2)))], [1, shiftby1]]
            for xt in xtests:
                s = xt[0]
                sol = xt[1]

                ans = decoder.shift_by_x(input, s)
                assert (ans == sol).all(), f"for {s} the result: {ans} is not {sol}"
                assert (
                    ans.shape == sol.shape
                ), f"for ans shape: {s.shape}  is not {sol.shape} on {s}"

    def test_x_shift_multi(self):
        L = 8
        decoder = ClassicFibDecoder(generate_init_code_word(L), self.logger)
        several_valued = np.arange(0, (L**2) // 2)

        sol = np.arange(0, (L**2) // 2)
        sol.shape = (L // 2, L)
        for row in sol:
            prev = row[0]
            for c in range(1, len(row)):
                tmp = row[c]
                row[c] = prev
                prev = tmp
            row[0] = prev

        sol.shape = (L**2) // 2
        ans = decoder.shift_by_x(several_valued)
        assert (ans == sol).all(), f"The result: {ans} is not the expected: {sol}"
        assert (
            ans.shape == sol.shape
        ), f"The result's shape: {ans.shape}  is not the expected shape: {sol.shape}"

    def test_y_shift(self):
        for L in [4, 8, 16, 32]:
            decoder = ClassicFibDecoder(generate_init_code_word(L), self.logger)
            input = np.array(list(range((L**2) // 2)))

            shiftbyminus1 = np.array(
                [
                    np.array(list(range((L * row), ((L * row) + L))))
                    for row in range(1, L // 2)
                ]
            )
            shiftbyminus1 = np.append(
                shiftbyminus1, [list(range(L))]
            )  # put top row at bottom

            shiftby1 = np.array(list(range(L * ((L // 2) - 1), L * (L // 2))))
            shiftby1 = np.append(
                shiftby1,
                np.array(
                    [
                        np.array(list(range((L * row), ((L * row) + L))))
                        for row in range(0, (L // 2) - 1)
                    ]
                ),
            )

            ytests = [
                [-1, shiftbyminus1],
                [1, shiftby1],
                [L // 2, np.array(list(range((L**2) // 2)))],
            ]

            for yt in ytests:
                s = yt[0]
                sol = yt[1]
                ans = decoder.shift_by_y(input, s)
                assert (ans == sol).all(), f"for {s} the ans: {ans} was not {sol} "
                assert (
                    ans.shape == sol.shape
                ), f" for {s} the ans shape: {ans.shape} did not match the sol shape: {sol.shape}"

    def test_y_shift_multi(self):
        L = 8
        decoder = ClassicFibDecoder(generate_init_code_word(L), self.logger)
        several_valued = np.arange(0, (L**2) // 2)
        sol = np.arange(0, ((L**2) // 2) - L)
        new_top_row = np.arange(((L**2) // 2) - L, (L**2) // 2)
        sol = np.concatenate((new_top_row, sol), axis=0)

        ans = decoder.shift_by_y(several_valued)
        assert (ans == sol).all(), f"The result: {ans} is not the expected: {sol}"
        assert (
            ans.shape == sol.shape
        ), f"The result's shape: {ans.shape}  is not the expected shape: {sol.shape}"

    def test_gen_stabs(self):
        fcheck_sol = np.array(
            [
                [1, 1, 1, 0, 0, 1, 0, 0],
                [1, 0, 0, 0, 1, 1, 0, 1],
                [0, 1, 0, 0, 1, 1, 1, 0],
                [0, 0, 1, 0, 0, 1, 1, 1],
            ]
        )

        L = 4
        decoder = ClassicFibDecoder(generate_init_code_word(L), self.logger)
        startarr = [
            0,
        ] * L
        startarr[(L // 2) - 1] = 1
        fund_sym = decoder._generate_init_symmetry(start_arr=startarr)
        fund_sym.shape = (L // 2, L)
        fcheck, _ = decoder.generate_check_matrix_from_faces(fund_sym)

        assert (
            fcheck.shape == fcheck_sol.shape
        ), f"{ fcheck.shape} but should be {fcheck_sol.shape} "
        assert (fcheck == fcheck_sol).all(), f"\n {fcheck}\n should be\n{fcheck_sol}"

        size32 = (32**2) // 2
        L = 32
        startarr = [
            0,
        ] * 32
        startarr[((32 // 2) - 1)] = 1
        decoder = ClassicFibDecoder(generate_init_code_word(L), self.logger)
        fund_sym = decoder._generate_init_symmetry(start_arr=startarr)
        fund_sym.shape = (L // 2, L)
        fcheck, _ = decoder.generate_check_matrix_from_faces(fund_sym)

        expected_shape = (128, size32)
        assert (
            fcheck.shape == expected_shape
        ), f"L=32 fcheckmat is shape {fcheck.shape} but should be  {expected_shape}"

        row0 = np.zeros(size32, dtype=int)
        row0[14:17] = 1  # 1 on 14, 15, 16
        row0[495] = 1  # top one

        row3 = np.zeros(size32, dtype=int)
        row3[47:50] = 1
        row3[16] = 1

        row57 = np.zeros(size32, dtype=int)
        row57[336:339] = 1
        row57[305] = 1

        row107 = np.zeros(size32, dtype=int)
        row107[511] = 1
        row107[480:482] = 1  # 479, 480, 481
        row107[448] = 1

        row127 = np.zeros(size32, dtype=int)
        row127[509:] = 1
        row127[478] = 1

        tests = [(0, row0), (3, row3), (57, row57), (107, row107), (127, row127)]

        for testrow in tests:
            indx = testrow[0]
            crow = testrow[1]

            equalarr = fcheck[indx] == crow
            if not equalarr.all():  # if there exists some False, aka nonmatching pair
                bad_indices = (equalarr == False).nonzero()[0]
                assert (
                    False
                ), f"hello\n  Row {indx} of fcheck is\n {fcheck[indx] }\n but should be \n{crow}\n They fail at\n {bad_indices}"

    # Those graph libraries tho


if __name__ == "__main__":
    unittest.main()
