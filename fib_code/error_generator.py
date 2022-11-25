import numpy as np


def generate_swath_error(
    codeword_array: np.ndarray,
    width: int,
    offset: int = 0,
    probability_of_error: float = 1,
    is_vertical: bool = True,
):
    """Expects ALL codewords to be numpy array of shape: (L//2, L)
    To generate iid error, simply set width to L and is_vertical to True


    Args:
        codeword_array (np.ndarray): _description_
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
    error_mask = np.zeros(codeword_array.shape, dtype=int)

    num_rows = len(codeword_array)
    num_col = len(codeword_array[0])
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

    return error_mask ^ codeword_array, error_mask
