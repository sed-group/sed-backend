from typing import Tuple, List, Any

import apps.difam.models as models
from libs.doe import create_latin_hypercube


def create_hypercube_doe(doe_request: models.DOEGenerationRequest) -> Tuple[List[int], List[List[Any]]]:
    """
    Creates a hypercube based on DOEGenerationRequest.
    Returns a tuple. The first element is a list of parameter ids. The second is the hypercube (a list of lists).
    Each nested list represents an experiment. The elements in the nested lists are parameter values for the
    respective experiment. To know which parameter it is, know that the elements in the nested list are in the
    same order as the elements in the parameter id list.
    :param doe_request:
    :return: Tuple: (parameter_id_list, hypercube)
    """
    stratifications = doe_request.doe_experiment_count

    # This is probably not necessary, but it ensures that the parameter order is known for future reference.
    doe_request.range_parameters.sort(key=lambda r_param: r_param.parameter_id)

    parameter_id_list = []
    range_list = []
    for range_parameter in doe_request.range_parameters:
        range_list.append([range_parameter.lower_value, range_parameter.upper_value])
        parameter_id_list.append(range_parameter.parameter_id)

    # Hypercube is a list of list. Each nested list represents an experiment. Each element in the nested list represent
    # the value of a parameter in that experiment. The order of those parameters are known, as they are the same as
    # what is inserted in the "range_list", and thus the same as what is in the parameter_id_list.
    hypercube = create_latin_hypercube(range_list, stratifications)

    return parameter_id_list, hypercube
