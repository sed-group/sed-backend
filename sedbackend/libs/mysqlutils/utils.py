from typing import List


def exclude_cols(column_list: List[str], exclude_list: List[str]):
    """
    Takes a list of strings, and excludes all entries in the exlclude list.
    Returns a copy of the list, but without the excluded entries.
    Does not change the inserted list.
    :return:
    """
    column_list_copy = column_list[:]

    for exclude_col in exclude_list:
        if exclude_col in column_list:
            column_list_copy.remove(exclude_col)
        else:
            raise ValueError("Excluded column could not be found in column list.")

    return column_list_copy
