# grug brain
# https://www.youtube.com/watch?v=h1cevveAaPs
# https://www.youtube.com/watch?v=rZjpsT7VgNU
import copy
import logging
import math
from argparse import ArgumentError
from functools import reduce
from typing import Set, Tuple

import numpy as np
import rustworkx as rx
from fib_code.decoder_graph import DecoderGraph


class FibCodeMetadata:
    def __init__(self, L):
        self.L = L
        self.no_cols = self.L
        self.no_rows = self.L // 2
        self.no_bits = (self.L**2) // 2  # no bits
        self.fundamental_hori_probe_indx = self.no_bits - (self.L // 2) - 1
        self.fundamental_verti_probe_indx = self.no_bits - 1


class ClassicFibDecoder:
    """
    self.board =
    [L*(L//2 - 1)....          ((L**2)//2) - 1]
     .
     .
     .
     2L
     L
     0 1 2 3 ....                                L - 1]
    """

    def __init__(
        self,
        original_errorword: np.array,
        logger: logging.Logger,
        halt: int = 9,
        name: str = "",
        probe_fundamental_indices=None,
    ):
        """ """

        logger.debug(f"Starting new run... {original_errorword}")

        self.L = len(original_errorword[0])  # len
        assert math.log2(self.L) % 1 == 0, "L must be some 2**n where n is an int >= 1"
        self.no_cols = self.L
        self.no_rows = self.L // 2
        self.no_bits = (self.L**2) // 2  # no bits
        self.halt = halt
        self.name = name

        self.logger = logger
        # fund_sym
        self.original_errorword = original_errorword

        self.board = copy.deepcopy(self.original_errorword)
        self.board.shape = self.no_bits
        self.fundamental_symmetry = self._generate_init_symmetry()
        self.fundamental_symmetry.shape = (self.no_rows, self.no_cols)
        (
            self.fundamental_stabilizer_parity_check_matrix,
            self.fundamental_parity_rows_to_faces,
        ) = self.generate_check_matrix_from_faces(self.fundamental_symmetry)
        self.fundamental_symmetry.shape = self.no_bits

        self.fundamental_single_error_syndromes = (
            self.generate_all_possible_error_syndromes(
                self.fundamental_stabilizer_parity_check_matrix
            )
        )
        self.Hx = self._generate_plus_x_trans_matrix()
        self.Hy = self._generate_plus_y_trans_matrix()

        self.fundamental_stab_faces = copy.deepcopy(self.fundamental_symmetry)
        self.fundamental_hori_probe_indx = self.no_bits - (self.L // 2) - 1
        self.fundamental_verti_probe_indx = self.no_bits - 1
        self.fundamental_stab_faces.shape = (self.L // 2, self.L)  # TODO should work
        if probe_fundamental_indices is None:
            probe_fundamental_indices = [
                self.fundamental_hori_probe_indx,
                self.fundamental_verti_probe_indx,
            ]
        self.probe_fundamental_indices = probe_fundamental_indices
        (
            self.fundamental_check_matrix,
            self.board2stab,
        ) = self.generate_check_matrix_from_faces(self.fundamental_stab_faces)
        fund_error_pairs = self.generate_all_possible_error_syndromes(
            self.fundamental_check_matrix
        )
        self.fund_matching_graph, self.fundstab2node = self.error_pairs2graph(
            fund_error_pairs
        )

        # Develop a generic decoder w/ fundamental_hori_probe_indx & fundamental_verti_probe_indx as anchors for indexing
        self.decoder = DecoderGraph(
            self.fund_matching_graph,
            self.probe_fundamental_indices,
            self.fundamental_hori_probe_indx,
            self.fundamental_verti_probe_indx,
            self.fundstab2node,
        )
        self.all_stab_faces = np.ones((self.L // 2, self.L), dtype=int)
        (
            self.all_stabs_check_mat,
            self.all_stabs_parity_rows_to_faces,
        ) = self.generate_check_matrix_from_faces(self.all_stab_faces)

        self.logger.debug(f" original_errorword is  {self.original_errorword}")
        self.logger.debug(f" error board is code {self.board}")
        self.logger.debug(f" initial symmetry is: {self.fundamental_symmetry}")
        self.logger.debug(
            f"fundamental_stabilizer_parity_check_matrix is : {self.fundamental_stabilizer_parity_check_matrix}"
        )
        self.logger.debug(
            f"fundamental_single_error_syndromes is : {self.fundamental_single_error_syndromes}"
        )
        self.logger.debug(f" Hx {self.Hx}")
        self.logger.debug(f" Hy is code {self.Hy}")

    def bit_to_rc(self, bit: int) -> int:
        """
         This functions maps from bit index (0 to   (L**2)//2) - 1) to row, column mapping
        # DOESNT yet handle bits that are too big


        in bit notation we think of all the bits being in a line:
        So we have bit 0, bit 1, ... all the way until the last bit ((L**2)//2) - 1
        [0, 1, 2,  ...................  ((L**2)//2) - 1 ]

        However, we can picture these as being on the
        L//2 by L  board.

        In numpy, if we reshape the  ((L**2)//2) - 1  to a L//2 by L array,
        then bit 0 will get mapped to the
        0th row, 0th column.
        This is called row, column notation
        Bit 1 will get mapped to the 0th row, 1st column.
        ...
        L//2 gets mapped to the 1st row, 0th column
        etc.

        I show here:

        [  [0 1 2  3 ...............................    (L//2) -1]
            L//2
                .
                .
                .
                [(L - 1) * (L//2)  ....................    ((L**2)//2) - 1 ]
            ]

        """
        row_len = self.L

        rindx = bit // row_len
        cindx = bit % row_len
        return (rindx, cindx)

    def rc_to_bit(self, row: int, col: int) -> int:
        """
        #This functions maps from (row, column) indexing to bit  (0 to   (L**2)//2) - 1) indexing

        in bit notation we think of all the bits being in a line:
        So we have bit 0, bit 1, ... all the way until the last bit ((L**2)//2) - 1
        [0, 1, 2,  ...................  ((L**2)//2) - 1 ]

        However, we can picture these as being on the
        L//2 by L  board.

        In numpy, if we reshape the  ((L**2)//2) - 1  to a L//2 by L array,
        then bit 0 will get mapped to the
        0th row, 0th column.
        This is called row, column notation
        Bit 1 will get mapped to the 0th row, 1st column.
        ...
        L//2 gets mapped to the 1st row, 0th column
        etc.

        I show here:

        [  [0 1 2  3 ...............................    (L//2) -1]
            L//2
                .
                .
                .
                [(L - 1) * (L//2)  ....................    ((L**2)//2) - 1 ]
            ]

        """
        bit = (row * self.L) + col
        return bit

    def _generate_plus_x_trans_matrix(self) -> np.array:
        """generate transition matrix for shifting every bit by x
        "Takes bit to bit + 1 mod rownum aka shifts bit to the right but wraps around its current row
        """
        H = np.zeros((self.no_bits, self.no_bits), dtype=int)
        for b in range(self.no_bits):
            new_bit = self.shift_by_x_scalar(b)
            H[new_bit][b] = 1
        return H

    def _generate_plus_y_trans_matrix(self) -> np.array:
        """generate transition matrix for shifting every bit by y
        "takes bit to bit + L mod L//2 aka shifts bit the row below but very bottom row shifts to be the 0th row
        """
        H = np.zeros((self.no_bits, self.no_bits), dtype=int)
        for b in range(self.no_bits):
            new_bit = self.shift_by_y_scalar(b)
            H[new_bit][b] = 1
        return H

    def shift_by_x(self, bitarr: np.array, power: int = 1):
        """shifts every entry in board matrix right by power w/ wrap around"""
        power = power % self.L
        Hx = np.linalg.matrix_power(self.Hx, power)
        sol = np.matmul(Hx, bitarr)
        sol = sol.astype(int)
        return sol

    def shift_by_y(self, bitarr: np.array, power=1):
        """shifts every entry in board matrix down by power w/ wrap around"""
        power = power % (self.L // 2)
        Hy = np.linalg.matrix_power(self.Hy, power)
        sol = np.matmul(Hy, bitarr)
        sol = sol.astype(int)
        return sol

    def shift_by_y_scalar(self, bit: int, shift_no: int = 1):
        """shifts entry in board matrix down by 1 w/ wrap around"""
        new_bit = bit
        for _ in range(shift_no):
            new_bit = (new_bit + self.L) % self.no_bits
        return new_bit

    def shift_by_x_scalar(self, bit: int, shift_no: int = 1):
        """shifts entry in board matrix right by 1 w/ wrap around"""
        new_bit = bit
        for _ in range(shift_no):
            new_bit = ((new_bit + 1) % self.L) + ((new_bit // self.L) * (self.L))
        return new_bit

    def shift_parity_mat_by_y(self, parity_mat, power=1):
        "EDITS PARITY MAT"
        for row in range(len(parity_mat)):
            parity_mat[row] = self.shift_by_y(parity_mat[row], power=power)
        return parity_mat

    def shift_parity_mat_by_x(self, parity_mat: np.array, power: int = 1) -> np.array:
        """Warning: Edits parity_mat! Shifts each bit in every row by power to the right, with wrap around.
        Note, since this is a parity matrix, every row has (L**2)//2 bits.

        Args:
            parity_mat (np.array): Parity Matrix
            power (int, optional): Number of times to shift each bit. Defaults to 1.

        Returns:
            np.array: Return the shifted array. Since arrays are mutable, this isn't strictly necessary.
        """
        for row in range(len(parity_mat)):
            parity_mat[row] = self.shift_by_x(parity_mat[row], power=power)
        return parity_mat

    def _calc_syndrome(self, check_matr: np.array, board: np.array = None):
        """_summary_

        Args:
            check_matr (np.array): _description_
            board (np.array, optional): _description_. Defaults to None.

        Returns:
            _type_: _description_
        """
        if board is None:
            board = self.board
        sol = np.matmul(check_matr, board) % 2
        sol = sol.astype(int)
        return sol

    def _generate_init_symmetry(self, start_arr: np.array = None):
        if start_arr and sum(start_arr) != 1:
            raise ArgumentError(
                f"Can only have a single 1 in start_arr. All else should be 0 but you have: {start_arr}"
            )
        # fundamental symmetries start from the top instead of the bottom because numpy
        rect_board = np.zeros((self.L // 2, self.L), dtype=int)
        if start_arr is None:
            start_arr = np.zeros(self.L, dtype=int)
            start_arr[(self.L // 2) - 1] = 1
        rect_board[0] = start_arr
        for row in range(1, self.L // 2):
            for bit in range(self.L):
                new_val = (
                    rect_board[row - 1][(bit - 1) % self.L]
                    ^ rect_board[row - 1][(bit) % self.L]
                    ^ rect_board[row - 1][(bit + 1) % self.L]
                )
                rect_board[row][bit] = new_val
        return rect_board

    def generate_check_matrix_from_faces(self, stab_faces: np.array):
        """x
        STABS:           xxx
        """
        # TODO slow because of all the shape changing
        """REQUIRES L//2 x L """
        # create parity check matrix for each
        # np.append([[1, 2, 3], [4, 5, 6]], [[7, 8, 9]], axis=0)

        faces_to_stabs_rows = (
            {}
        )  # {x:y} where row x of the parity check matrix has face centered at bit b
        parity_mat = np.empty((0, self.no_bits), int)

        stab_row = 0
        for row in range(self.no_rows):
            for col in range(self.no_cols):
                if stab_faces[row][col] == 1:
                    a = self.rc_to_bit(row, col)
                    b = self.rc_to_bit((row) % self.no_rows, (col - 1) % self.no_cols)
                    c = self.rc_to_bit((row) % self.no_rows, (col + 1) % self.no_cols)
                    d = self.rc_to_bit(
                        (row - 1) % self.no_rows, col % self.no_cols
                    )  # changed to point the other direction
                    new_stab = np.array([0] * self.no_bits)
                    new_stab[a] = 1
                    new_stab[b] = 1
                    new_stab[c] = 1
                    new_stab[d] = 1
                    parity_mat = np.append(parity_mat, [new_stab], axis=0)
                    faces_to_stabs_rows[stab_row] = b
                    stab_row += 1

        return parity_mat, faces_to_stabs_rows

    def generate_all_possible_error_syndromes(
        self, parity_check_matrix: np.array, no_bits: int = None
    ):
        """Written from frame of reference of fundamental board and uses symmetry defined by parity_check_matrix"""

        # "there's gotta be a smarter way to do this "
        if no_bits is None:
            no_bits = self.no_bits
        error_pairs = set()  # (stab_face1, stab_face2, errorbit)
        single_error = np.zeros(no_bits, dtype=int)

        for b in range(no_bits):
            if no_bits > 10 and b % (no_bits // 10) == 0:
                self.logger.debug(
                    f"on bit: {b} and error set looks like: {error_pairs}"
                )

            ## set up new single error
            # clear prev_bit
            prev_bit = (b - 1) % no_bits
            single_error[prev_bit] = 0
            # set new error
            single_error[b] = 1

            ## what do it light?
            lighted = self._calc_syndrome(parity_check_matrix, single_error)
            stabs = (lighted == 1).nonzero()[0]

            if len(stabs) % 2 != 0:
                emsg = f"Minor panic. Error on  bit {b} causes a BAD syndrome: {stabs} for lighted: {lighted}"
                self.logger.error(
                    emsg
                )  # TODO just do this via inspection on 1s per column in stab parity check matrix
                raise Exception(emsg)

            if len(stabs) > 0:
                for indx in range(0, len(stabs), 2):
                    error_pairs.add((stabs[indx], stabs[indx + 1], b))

        return error_pairs

    def error_pairs2graph(self, error_graphs: Set[Tuple[int, int, int]]):
        stab2node = {}
        graph = rx.PyGraph()

        def add_to_graph(stabid):
            if stabid not in stab2node:
                nodeid = graph.add_node({"element": stabid})
                stab2node[stabid] = nodeid
            return stab2node[stabid]

        for stab0, stab1, fund_e in error_graphs:
            graph_node_n0 = add_to_graph(stab0)
            graph_node_n1 = add_to_graph(stab1)
            graph.add_edge(graph_node_n0, graph_node_n1, {"fault_ids": {fund_e}})

        return graph, stab2node

    def decode_fib_code(self, meta_only=False):
        """Run Decoder on given error board"""

        # generate graphs and mappings
        parity_check_matrix = copy.deepcopy(self.fundamental_check_matrix)
        hori_probe_indx = self.fundamental_hori_probe_indx
        verti_probe_indx = self.fundamental_verti_probe_indx

        cur_all_syndrome = prev_all_syndrome = (
            (self._calc_syndrome(self.all_stabs_check_mat, self.board) == 1).sum(),
        )
        start_flag = True
        meta_round_count = 0
        round_count = 0
        self.fundamental_stab_faces.shape = self.no_bits
        prob_indices = copy.deepcopy(self.probe_fundamental_indices)
        probe_board_corrections = [np.zeros(self.no_bits, dtype=int)] * len(
            prob_indices
        )

        while (
            (cur_all_syndrome < prev_all_syndrome or start_flag)
            and cur_all_syndrome != 0
            and meta_round_count < self.halt
        ):
            self.logger.debug(f"meta_round:{meta_round_count}")
            start_flag = False
            prev_all_syndrome = cur_all_syndrome

            for y_offset in range(self.L // 2):  # will wrap around to all bits
                parity_check_matrix = self.shift_parity_mat_by_y(parity_check_matrix)
                self.fundamental_stab_faces = self.shift_by_y(
                    self.fundamental_stab_faces
                )
                hori_probe_indx = self.shift_by_y_scalar(hori_probe_indx)
                verti_probe_indx = self.shift_by_y_scalar(verti_probe_indx)
                prob_indices = [
                    self.shift_by_y_scalar(probe_indx) for probe_indx in prob_indices
                ]

                for x_offset in range(self.L):
                    parity_check_matrix = self.shift_parity_mat_by_x(
                        parity_check_matrix
                    )
                    self.fundamental_stab_faces = self.shift_by_x(
                        self.fundamental_stab_faces
                    )
                    hori_probe_indx = self.shift_by_x_scalar(hori_probe_indx)
                    verti_probe_indx = self.shift_by_x_scalar(verti_probe_indx)
                    prob_indices = [
                        self.shift_by_x_scalar(probe_indx)
                        for probe_indx in prob_indices
                    ]

                    self.fundamental_stab_faces.shape = (self.L // 2, self.L)
                    self.fundamental_stab_faces.shape = self.no_bits

                    symmetry_indx_syndrome = self._calc_syndrome(parity_check_matrix)

                    correction_at_probs, res = self.decoder.decode_prob(
                        symmetry_indx_syndrome
                    )

                    for probe_no, pc in enumerate(correction_at_probs):
                        current_indx = prob_indices[probe_no]
                        probe_board_corrections[probe_no][current_indx] = pc

                    round_count += 1

                    self.logger.debug(
                        f"begin_fund_stab_faces:\n{self.fundamental_stab_faces}\nend_fund_stab_faces"
                    )
                    self.logger.debug(
                        f"current_parity_check_mat:\n{parity_check_matrix}"
                    )
                    self.logger.debug(f"cur-syndrome-symm:{symmetry_indx_syndrome}")
                    self.logger.debug(f"res-is:{res}")

            self.logger.debug(f"Meta-Round:{meta_round_count}:")

            meta_round_count += 1

            meta_correction = reduce(lambda x, y: x * y, probe_board_corrections)
            minboard, minsyn = [], self.no_bits + 1

            if meta_only:
                minboard = self.board ^ meta_correction
                minsyn = (
                    self._calc_syndrome(self.all_stabs_check_mat, minboard) == 1
                ).sum()
            else:
                probe_board_corrections.append(meta_correction)
                for correction in probe_board_corrections:
                    board = self.board ^ correction
                    syn = (
                        self._calc_syndrome(self.all_stabs_check_mat, board) == 1
                    ).sum()
                    if syn <= minsyn:
                        minboard, minsyn = board, syn
            self.board = minboard

            self.logger.debug(f"updated_board is:\n{self.board}\nend_updated_board")

        self.logger.debug("FINISHED DECODING")
