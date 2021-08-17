import contextlib
import numpy as np


@contextlib.contextmanager
def temp_numpy_seed(seed):
    """
    Temporarily set the random seed so that randomness can be reproduced
    Setting the seed to None resets the seed
    :param seed:
    :return:
    """
    state = np.random.get_state()
    np.random.seed(seed)
    try:
        yield
    finally:
        # Return to original state
        np.random.set_state(state)
