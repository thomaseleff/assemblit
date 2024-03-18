"""
Information
---------------------------------------------------------------------
Name        : utils.py
Location    : ~/
Author      : Tom Eleff
Published   : 2023-07-11
Revised on  : 2024-03-17

Description
---------------------------------------------------------------------
Contains utility functions for managing configuration, validation,
data-types and user-logging.
"""

import json
import os
import time
import ast
import datetime as dt
from typing import Callable


# Function(s) related to managing configuration-files
def read_config(
    configLoc: str
) -> dict:
    """ Reads `configLoc` and returns a dictionary object.

    Parameters
    ----------
    configLoc : `str`
        Path to ~/config.json that contains the parameters essential to the application.
    """

    config = {}

    try:
        with open(
            configLoc,
            mode='r'
        ) as file:
            try:
                config = json.load(file)
            except json.decoder.JSONDecodeError:
                config = False
                raise IOError(
                    'ERROR: ~/%s is invalid.' % (os.path.basename(configLoc))
                )
    except FileNotFoundError:
        config = False
        raise FileNotFoundError(
            'ERROR: %s does not exist.' % (configLoc)
        )

    return config


def validate_config(
    config: dict,
    dtype: dict
):
    """ Validates `config` against the dtypes in `dtype`.

    Parameters
    ----------
    config : `dict`
        Dictionary object that contains the parameters essential to the application.
    dtype : `dict`
        Dictionary object that contains the expected `config` value dtypes.
    """

    confErrors = {}
    err = False

    for section in config.keys():
        if section not in dtype.keys():
            dtype[section] = {}
            confErrors[section] = {}
        else:
            confErrors[section] = {}

        for key, value in config[section].items():
            if key not in dtype[section].keys():
                confErrors[section][key] = 'No dtype found in ~/dtypes.json.'
                err = True
            else:
                if type(value).__name__ != dtype[section][key]:
                    confErrors[section][key] = (
                        'Invalid dtype. Expected <' +
                        dtype[section][key] + '>.'
                    )
                    err = True
                else:
                    pass

    len0 = max(
        [len(section) for section in confErrors.keys()]
    )
    if err:
        for section in confErrors.keys():
            if len(confErrors[section].keys()) > 0:

                print(
                    'ERROR: The following errors occurred when' +
                    ' validating the [%s] parameters.\n' %
                    (section)
                )

                len1 = max(
                    [len(key) for key in confErrors[section].keys()]
                )
                len2 = max(
                    [len(value) for value in confErrors[section].values()]
                )

                print(
                    "{:<8} {:<{len0}} {:<{len1}} {:<{len2}}".format(
                        '',
                        'Section',
                        'Key',
                        'Error',
                        len0=len0+4,
                        len1=len1+4,
                        len2=len2+4
                    )
                )
                print(
                    "{:<8} {:<{len0}} {:<{len1}} {:<{len2}}".format(
                        '',
                        '-------',
                        '---',
                        '-----',
                        len0=len0+4,
                        len1=len1+4,
                        len2=len2+4
                    )
                )

                for key, value in confErrors[section].items():
                    print(
                        ("{:<8} {:<{len0}} {:<{len1}} {:<{len2}}").format(
                            '',
                            section,
                            key,
                            value,
                            len0=len0+4,
                            len1=len1+4,
                            len2=len2+4
                        )
                    )
                print(
                    '\n'
                )
            else:
                pass
        raise TypeError(
            'ERROR: Validation failed.'
        )
    else:
        print(
            'NOTE: Validation completed successfully.'
        )


def write_config(
    configLoc: str,
    config: dict
):
    """ Writes the `config` dictionary object to `configLoc`.

    Parameters
    ----------
    configLoc : `str`
        Path to output `config`
    config : `dict`
        Dictionary object that contains the parameters essential to the application.
    """

    try:
        with open(
            configLoc,
            mode='w+'
        ) as file:
            json.dump(
                config,
                file,
                indent=4
            )
    except FileNotFoundError:
        raise FileNotFoundError(
            'ERROR: %s does not exist.' % (configLoc)
        )


def generate_output_directory(
    config: dict
):
    """ Recursively generates an output directory.

    Parameters
    ----------
    config : `dict`
        Dictionary object containing the output directory structure.
    """

    if 'outputs' in config.keys():

        if config['outputs']['root'] not in os.listdir(
            config['outputs']['path']
        ):

            # Create root output directory
            os.mkdir(
                os.path.join(
                    config['outputs']['path'],
                    config['outputs']['root']
                )
            )

            # Create output sub-directories
            if 'subFolders' in config['outputs'].keys():
                for folder in config['outputs']['subFolders']:
                    os.mkdir(
                        os.path.join(
                            config['outputs']['path'],
                            config['outputs']['root'],
                            folder
                        )
                    )
        else:
            pass

    else:
        raise KeyError(
            "ERROR: <config> does not contain the key, 'outputs'."
        )


# Decorator function(s)
def run_time(
    func: Callable
) -> Callable:
    """ Prints the run time of the {func} passed.

    Parameters
    ----------
    func : `func`
        Function object
    """

    def wrapper(*args, **kwargs):
        t1 = time.time()
        result = func(*args, **kwargs)
        t2 = time.time()
        td = dt.timedelta(seconds=(t2-t1))
        print("Function '%s()' executed in %s hh:mm:ss" % (
                func.__name__,
                td
            )
        )

        return result

    return wrapper


# Data-type parsing function(s)
def as_type(
    value: str,
    return_dtype: str = 'str'
) -> str | int | float | bool | list | dict:
    """ Returns `value` as `return_dtype`.

    Parameters
    ----------
    value : `str`
        String of the value to convert to `return_dtype`.
    return_dtype : `str`
        Name of the datatype (`str`, `int`, `float`, `bool`, `list`, `dict`) of
            the returned value. If the returned value cannot be converted
            to `return_dtype` then a `TypeError` is raised. If the name of the
            `return_dtype` is invalid, then a `NameError` is returned.
    """

    try:
        if return_dtype.strip().upper() == 'STR':
            return str(value)

        elif return_dtype.strip().upper() == 'INT':
            return int(value)

        elif return_dtype.strip().upper() == 'FLOAT':
            return float(value)

        elif return_dtype.strip().upper() == 'BOOL':

            try:
                return ast.literal_eval(value)
            except (SyntaxError, ValueError):
                raise TypeError(
                    ' '.join([
                        "{%s} value" % (
                            value
                        ),
                        "cannot be converted to {%s}." % (
                            return_dtype
                        )
                    ])
                )

        elif (
            (return_dtype.strip().upper() == 'LIST')
            or (return_dtype.strip().upper() == 'DICT')
        ):
            try:
                return json.loads(value)
            except json.decoder.JSONDecodeError:
                raise TypeError(
                    ' '.join([
                        "{%s} value" % (
                            value
                        ),
                        "cannot be converted to {%s}." % (
                            return_dtype
                        )
                    ])
                )
        else:
            raise NameError(
                'Invalid return datatype {%s}.' % (
                    return_dtype
                )
            )
    except ValueError:
        raise TypeError(
            ' '.join([
                "{%s} value" % (
                    value
                ),
                "cannot be converted to {%s}." % (
                    return_dtype
                )
            ])
        )
