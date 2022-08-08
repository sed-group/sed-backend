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


