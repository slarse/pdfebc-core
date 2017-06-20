# -*- coding: utf-8 -*-
"""Module containing miscellaneous util functions for pdfebc.

The SMTP server and port are configured in the config.cnf file, see the config_utils module
for more information.

.. module:: utils
    :platform: Unix
    :synopsis: Miscellaneous utility functions for pdfebc.

.. moduleauthor:: Simon Larsén <slarse@kth.se>
"""

def if_callable_call_with_formatted_string(callback, formattable_string, *args):
    """If the callback is callable, format the string with the args and make a call.
    Otherwise, do nothing.

    Args:
        callback (function): May or may not be callable.
        formattable_string (str): A string with '{}'s inserted.
        *args: A variable amount of arguments for the string formatting. Must correspond to the
        amount of '{}'s in 'formattable_string'.
    Raises:
        ValueError
    """
    try:
        formatted_string = formattable_string.format(*args)
    except IndexError:
        raise ValueError("Mismatch metween amount of insertion points in the formattable string\n"
                         "and the amount of args given.")
    if callable(callback):
        callback(formatted_string)
