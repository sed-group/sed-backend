import re


def replace_all(pattern, replacement, string):
    """
    Replaces all *exact* matches of pattern in str with replacement. 

    :param pattern: The exact pattern
    :param replacement:
    :param string: The string in which to replace

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


def get_prefix_variables(prefix, string):
    """
    Finds all matching variables with the given prefix.

    :param prefix: The prefix that will be searched for in
    :param string:

    :return List[str]: A list of all matching variables in the string that have the prefix "prefix"
    """

    regex_pattern = fr'\"{prefix}\((.*?)\)\"'
    matches = re.findall(regex_pattern, string)

    return matches


def get_prefix_names(prefix, string):
    """
    Finds all matching names with the given prefix.

    :param prefix: The prefix that will be searched for in
    :param string:

    :return List[str]: A list of all matching names in the string that have the prefix "prefix"
    """

    matches = get_prefix_variables(prefix, string)
    results = []
    for match in matches:
        # Find the last occurrence of square brackets in the match
        last_bracket_index = match.rfind('[')
        if last_bracket_index != -1:
            # Remove the square brackets and their contents only if they're the last ones
            if ']' in match[last_bracket_index:]:
                match = match[:last_bracket_index].strip()
        results.append(match)

    return results


def replace_prefix_variables(prefix: str, variable: str, replacement: str, string: str):
    """
    Replaces all *exact* matches of pattern in str with replacement.

    :param prefix: The prefix that will be searched for in
    :param variable: The name that will be searched for in
    :param replacement:
    :param string: The string in which to replace

    :return string:
    """
    new_string = re.sub(rf"\"{re.escape(prefix)}\({re.escape(variable)}\)\"", replacement, string)
    return new_string


# Author: ChatGPT
def remove_strings_replace_zero(input_str):

    """
    Removes all strings and replaces all variables with a 0.

    :param input_str: The string to remove strings and replace variables with a 0

    :return string: The string with all strings removed and all variables replaced with a 0
    """

    # Replace all strings with a 0
    regex_pattern = r'\".*?\"'
    output_str = re.sub(regex_pattern, '0', input_str)

    return output_str
