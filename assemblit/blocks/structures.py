""" Data objects for assembling web-pages """

from __future__ import annotations
from dataclasses import dataclass
from typing import Literal, Union
import pandera
import datetime
import json

_DTYPE_MAP = {
    'bool': bool,
    'str': str,
    'int': int,
    'float': float,
    'datetime': datetime.datetime,
    'timedelta': datetime.timedelta
}


@dataclass
class Setting():
    """ A `class` that represents a settings parameter.

    Attributes
    ----------
    type : `Literal['text-input', 'toggle', 'slider', 'selectbox', 'multiselect']`
        The `streamlit` widget to use to represent the parameter.
    dtype : `Literal['bool', 'str', 'int', 'float', 'datetime', 'timedelta']`
        The data-type of the parameter value.
    parameter : `str`
        The name used to represent the parameter in the database and the session-state.
    name : `str`
        The display name used to represent the parameter.
    value : `Union[str, None]`
        The default value of the parameter.
    kwargs : `Union[dict, None]`
        Additional key-word arguments for the `streamlit` widget.
    description : `Union[str, None]`
        The short summary of the parameter or instructions on setting the parameter value.
    """

    type: Literal['text-input', 'toggle', 'slider', 'selectbox', 'multiselect']
    dtype: Literal['bool', 'str', 'int', 'float', 'datetime', 'timedelta']
    parameter: str
    name: str
    value: Union[str, None] = None
    kwargs: Union[dict, None] = None
    description: Union[str, None] = None

    def from_dict(dict_object: dict) -> Setting:
        """ Returns a `Setting` object from a `dict`.

        Parameters
        ----------
        dict_object : `dict`
            The dictionary object to convert to a `Setting` object.
        """

        # Assert object type
        if not isinstance(dict_object, dict):
            raise TypeError('Object must be a `dict`.')

        # Assert keys
        missing_keys = [key for key in [
            'type', 'dtype', 'parameter', 'name'
        ] if key not in dict_object]
        if missing_keys:
            raise KeyError(
                'Missing keys. The `dict` object is missing the following required keys [%s].' % (
                    ','.join(["'%s'" % (key) for key in missing_keys])
                )
            )

        # Assert value is the correct dtype or is none
        if 'value' in dict_object:
            if dict_object['value']:
                if not isinstance(dict_object['value'], _DTYPE_MAP[dict_object['dtype']]):
                    raise TypeError(
                        "Invalid value. Parameter '%s' requires a(n) '%s' value." % (
                            dict_object['name'],
                            dict_object['dtype']
                        )
                    )

        # Assert that the slider setting type has kwargs
        if str(dict_object['type']).strip().lower() == 'slider':

            if 'kwargs' not in dict_object:
                raise ValueError('Missing kwargs. Slider `Setting` objects require kwargs as a `dict`.')

            if (
                dict_object['kwargs'] is None
                or dict_object['kwargs'] == ''
                or not isinstance(dict_object['kwargs'], dict)
            ):
                raise ValueError('Missing kwargs. Slider `Setting` objects require kwargs as a `dict`.')

        return Setting(**dict_object)

    def to_dict(self):
        """ Returns the `Setting` object as a `dict`. """
        return {
            'type': self.type,
            'dtype': self.dtype,
            'parameter': self.parameter,
            'name': self.name,
            'value': self.value,
            'kwargs': self.kwargs,
            'description': self.description
        }

    def to_pandera(self) -> pandera.Column:
        """ Returns the `Setting` object as a `pandera.Column`. """
        return pandera.Column(
            dtype=self.dtype,
            name=self.parameter,
            title=self.name,
            default=self.value,
            nullable=self.value is None or self.value == '',
            required=not (self.value is None or self.value == '')
        )

    def to_selector(self) -> Selector:
        """ Returns a `Selector` object from the `Setting` object.
        """
        return Selector(
            parameter=self.parameter,
            name=self.name,
            description=self.description
        )

    def __repr__(self):
        """ Returns the `Setting` object as a json-formatted `str`. """
        return json.dumps(self.to_dict(), indent=2)


@dataclass
class Selector():
    """ A `class` that represents a selector parameter.

    Attributes
    ----------
    parameter : `str`
        The name used to represent the parameter in the database and the session-state.
    name : `Union[str, None]`
        The display name used to represent the parameter.
    description : `Union[str, None]`
        The short summary of the parameter or instructions on setting the parameter value.
    """

    parameter: str
    name: Union[str, None] = None
    description: Union[str, None] = None

    def from_dict(dict_object: dict) -> Selector:
        """ Returns a `Selector` object from a `dict`.

        Parameters
        ----------
        dict_object : `dict`
            The dictionary object to convert to a `Selector` object.
        """

        # Assert object type
        if not isinstance(dict_object, dict):
            raise TypeError('Object must be a `dict`.')

        # Assert keys
        missing_keys = [key for key in [
            'parameter'
        ] if key not in dict_object]
        if missing_keys:
            raise KeyError(
                'Missing keys. The `dict` object is missing the following required keys [%s].' % (
                    ','.join(["'%s'" % (key) for key in missing_keys])
                )
            )

        return Selector(**dict_object)

    def to_dict(self):
        """ Returns the `Selector` object as a `dict`.
        """
        return {
            'parameter': self.parameter,
            'name': self.name,
            'description': self.description
        }

    def __repr__(self):
        """ Returns the `Selector` object as a json-formatted `str`.
        """
        return json.dumps(self.to_dict(), indent=2)
