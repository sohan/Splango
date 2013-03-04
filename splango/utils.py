"""Utilities for project Splango.

"""


def replace_insensitive(string, target, replacement):
    """Similar to string.replace() but is case insensitive

    Code borrowed from ``debug_toolbar`` and
    http://forums.devshed.com/python-programming-11/case-insensitive-string-replace-490921.html

    """
    no_case = string.lower()
    index = no_case.rfind(target.lower())
    if index >= 0:
        return string[:index] + replacement + string[index + len(target):]
    else:  # no results so return the original string
        return string
