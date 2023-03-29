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


def get_prefix_names(prefix, string):
    """
    Finds all matching names with the given prefix.

    :param prefix: The prefix that will be searched for in
    :param string:

    :return List[str]: A list of all matching names in the string that have the prefix "prefix"
    """

    regex_pattern = prefix + r"\((\w+)\s+\[.+?\]\)"
    names = re.findall(regex_pattern, string)

    return names


def replace_prefix_names(prefix: str, name: str, replacement: str, string: str):
    """
    Replaces all *exact* matches of pattern in str with replacement.

    :param prefix: The prefix that will be searched for in
    :param name: The name that will be searched for in
    :param replacement:
    :param string: The string in which to replace

    :return string:
    """
    new_string = re.sub(rf"\"{prefix}\({name}\s+\[.+?\]\)\"", replacement, string)
    return new_string
