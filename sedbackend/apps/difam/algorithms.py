from typing import List, Any, Dict

import sedbackend.apps.difam.models as models
import sedbackend.apps.core.individuals.models as ind_models
from sedbackend.libs.doe import create_latin_hypercube


def create_hypercube_doe(doe_request: models.DOEGenerationRequest,
                         parameters_dict: Dict[int, ind_models.IndividualParameter]) \
        -> List[List[Any]]:
    """
    Creates a hypercube based on DOEGenerationRequest.
    Returns a tuple. The first element is a list of parameter ids. The second is the hypercube (a list of lists).
    Each nested list represents an experiment. The elements in the nested lists are parameter values for the
    respective experiment. To know which parameter it is, know that the elements in the nested list are in the
    same order as the elements in the parameter id list.
    :param parameters_dict: Dict of parameters mapped ID -> IndividualParameter
    :param doe_request:
    :return: Tuple: (parameter_id_list, hypercube)
    """
    stratifications = doe_request.doe_experiment_count

    range_list = []
    for range_parameter in doe_request.range_parameters:
        # Check if parameter is INT parameter
        parameter = parameters_dict[range_parameter.parameter_id]

        if parameter.type == ind_models.ParameterType.INTEGER:
            # The hypercube generator does not handle integers, only floats.
            # Floats are later rounded down to the nearest float.
            # By adding 0.99 to the upper limit we thus ensure that the upper limit is included,
            # which otherwise would be unlikely.
            range_list.append([range_parameter.lower_value, range_parameter.upper_value + 0.999999])
        elif parameter.type == ind_models.ParameterType.FLOAT:
            # Floats we can handle as usual
            range_list.append([range_parameter.lower_value, range_parameter.upper_value])
        else:
            # We can not handle strings or booleans when generating hypercubes.
            pass


    # Hypercube is a list of list. Each nested list represents an experiment. Each element in the nested list represent
    # the value of a parameter in that experiment. The order of those parameters are the same as they are inserted.
    hypercube = create_latin_hypercube(range_list, stratifications)

    return hypercube
