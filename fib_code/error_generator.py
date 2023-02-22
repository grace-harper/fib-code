import numpy as np


def generate_vertical_racetrack_error(codeword: np.ndarray, probability_of_error: int):
    return generate_racetrack_error(codeword, probability_of_error, is_vertical=True)


def generate_horizontal_racetrack_error(
    codeword: np.ndarray, probability_of_error: int
):
    return generate_racetrack_error(codeword, probability_of_error, is_vertical=False)


def generate_racetrack_error(
    codeword: np.ndarray, probability_of_error: int, is_vertical: bool = True
):

    error_mask = np.zeros(codeword.shape, dtype=int)

    num_rows = len(codeword)
    num_col = len(codeword[0])

    if is_vertical:
        for column in range(num_col):
            if np.random.choice(
                [True, False], p=[probability_of_error, 1 - probability_of_error]
            ):
                error_mask[:, column] = 1

    else:
        for row in range(num_rows):
            if np.random.choice(
                [True, False], p=[probability_of_error, 1 - probability_of_error]
            ):
                error_mask[row, :] = 1

    return error_mask ^ codeword, error_mask


def generate_swath_error(
    codeword: np.ndarray,
    width: int,
    offset: int = 0,
    probability_of_error: float = 1,
    is_vertical: bool = True,
):
    """Expects ALL codewords to be numpy array of shape: (L//2, L)
    To generate iid error, simply set width to L and is_vertical to True


    Args:
        codeword (np.ndarray): _description_
        width (int): _description_
        offset (int, optional): _description_. Defaults to 0.
        probability_of_error (float, optional): _description_. Defaults to 1.
        is_vertical (bool, optional): _description_. Defaults to True.

    Raises:
        Exception: _description_

    Returns:
        _type_: _description_
    """

    if probability_of_error <= 0:
        raise Exception("Can't create errors with zero probability")
    error_mask = np.zeros(codeword.shape, dtype=int)

    num_rows = len(codeword)
    num_col = len(codeword[0])
    if is_vertical:
        if probability_of_error == 1:
            error_mask[:, offset : width + offset] = 1
        else:
            for i in range(num_rows):
                for j in range(width):
                    error_mask[i][(j + offset) % num_col] = np.random.choice(
                        [0, 1], p=[1 - probability_of_error, probability_of_error]
                    )

    else:
        height = width
        if probability_of_error == 1:
            error_mask[offset : offset + height, :] = 1
        else:
            for i in range(width):
                for j in range(num_col):
                    error_mask[(i + offset) % num_rows][j] = np.random.choice(
                        [0, 1], p=[1 - probability_of_error, probability_of_error]
                    )

    return error_mask ^ codeword, error_mask
