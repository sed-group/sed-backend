from typing import List, Any, Optional

import numpy.random as random

from .utils import temp_numpy_seed


def create_latin_hypercube(parameters: List[List[Any]], stratifications: int = 10, seed: Optional[int] = None):
    """

    :param seed: random seed. Same value produces the same result. Leave as none to keep randomness.
    :param parameters: Parameter is a list of lists. Each nested list represents a parameter range.
    The nested list should only have two elements, the first one being the lower limit, the second one the upper limit.
    :param stratifications: Amount of experiments. Recommended to be about 10 times the amount of parameters.
    :return:
    """

    with temp_numpy_seed(seed):
        parameter_matrix = []

        for parameter in parameters:
            if len(parameter) != 2:
                raise TypeError('Parameters needs to come in pairs of 2 when using the latin hypercube method')

            lim_upper = parameter[1]
            lim_lower = parameter[0]
            if parameter[0] > parameter[1]:
                lim_upper = parameter[0]
                lim_lower = parameter[1]

            dim_range = lim_upper - lim_lower
            strat_range = dim_range/stratifications

            strats = []
            for i in range (0, stratifications):
                strats.append([lim_lower + strat_range * i, lim_lower + strat_range * (i + 1)])

            # At this point we have the array "strats", which contains the upper limit of each stratification.
            # Now all we need to do is to loop through the strats and provide a sample point in each of them.

            # Shuffle the stratums
            random.shuffle(strats)

            parameter_index = 0
            while len(strats) != 0:

                if len(parameter_matrix) < parameter_index + 1:
                    parameter_matrix.append([])

                strat = strats.pop()
                # Generate a random number within the stratum
                value = strat[0] + random.rand() * (strat[1] - strat[0])
                parameter_matrix[parameter_index].append(value)
                parameter_index += 1

        return parameter_matrix


