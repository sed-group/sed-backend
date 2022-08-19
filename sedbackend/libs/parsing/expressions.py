import re



def replace_all(pattern, replacement, string):
    """
    Replaces all *exact* matches of pattern in str with replacement. 

    :param pattern: The exact pattern
    :param replacement:
    :param str: The string in which to replace

    :return string:
    """
    new_string = re.sub(r'\b' + pattern + r'\b', str(replacement), string)
    return new_string


def get_prefix_ids(prefix, string):
    """
    Finds all matching ids with the given prefix. 

    :param prefix: The prefix that will be searched for
    :param string:

    :return List[int]: A list of all matching ids in the string that have the prefix "prefix"
    """

    ids = re.findall(r'\b' + prefix + r'[0-9]+', string)
    
    num_ids = []
    for str_id in ids:
        id = ''.join([n for n in str_id if n.isdigit()])
        num_ids.append(id)
    
    return num_ids

