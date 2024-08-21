""" Tests the `assemblit.blocks` subpackage """

import pytest
import pandera
import json
from assemblit import blocks


@pytest.fixture
def SETTING_FIXTURE() -> blocks.structures.Setting:
    return blocks.structures.Setting(
        type='text-input',
        dtype='str',
        parameter='test_parameter',
        name='Test parameter',
        value='A',
        kwargs=None,
        description='The `Test parameter` setting object.'
    )


@pytest.fixture
def SELECTOR_FIXTURE() -> blocks.structures.Selector:
    return blocks.structures.Selector(
        parameter='test_parameter',
        name='Test parameter',
        description='The `Test parameter` selector object.'
    )


def test_setting_init_success(SETTING_FIXTURE: blocks.structures.Setting):
    assert SETTING_FIXTURE.type == 'text-input'
    assert SETTING_FIXTURE.dtype == 'str'
    assert SETTING_FIXTURE.parameter == 'test_parameter'
    assert SETTING_FIXTURE.name == 'Test parameter'
    assert SETTING_FIXTURE.value == 'A'
    assert not SETTING_FIXTURE.kwargs
    assert SETTING_FIXTURE.description == 'The `Test parameter` setting object.'


def test_setting_from_dict_success():
    setting: blocks.structures.Setting = blocks.structures.Setting.from_dict(
        dict_object={
            'type': 'text-input',
            'dtype': 'str',
            'parameter': 'test_parameter',
            'name': 'Test parameter',
            'value': 'A',
            'description': 'The `Test parameter` setting object.'
        }
    )
    assert setting.type == 'text-input'
    assert setting.dtype == 'str'
    assert setting.parameter == 'test_parameter'
    assert setting.name == 'Test parameter'
    assert setting.value == 'A'
    assert not setting.kwargs
    assert setting.description == 'The `Test parameter` setting object.'


def test_setting_from_dict_parameter_typeerror():
    with pytest.raises(TypeError):
        blocks.structures.Setting.from_dict(
            dict_object=[]
        )


def test_setting_from_dict_keyerror():
    with pytest.raises(KeyError):
        blocks.structures.Setting.from_dict(
            dict_object={
                'type': 'text-input',
                'dtype': 'str',
                'parameter': 'test_parameter'
            }
        )


def test_setting_from_dict_value_typeerror():
    with pytest.raises(TypeError):
        blocks.structures.Setting.from_dict(
            dict_object={
                'type': 'text-input',
                'dtype': 'str',
                'parameter': 'test_parameter',
                'name': 'Test parameter',
                'value': 1,
                'description': 'The `Test parameter` setting object.'
            }
        )


def test_setting_from_dict_missing_kwargs_valueerror():
    with pytest.raises(ValueError):
        blocks.structures.Setting.from_dict(
            dict_object={
                'type': 'slider',
                'dtype': 'int',
                'parameter': 'test_parameter',
                'name': 'Test parameter',
                'value': 1,
                'description': 'The `Test parameter` setting object.'
            }
        )


def test_setting_from_dict_invalid_kwargs_valueerror():
    with pytest.raises(ValueError):
        blocks.structures.Setting.from_dict(
            dict_object={
                'type': 'slider',
                'dtype': 'int',
                'parameter': 'test_parameter',
                'name': 'Test parameter',
                'value': 1,
                'kwargs': [],
                'description': 'The `Test parameter` setting object.'
            }
        )


def test_setting_to_dict_success():
    dict_object = {
        'type': 'text-input',
        'dtype': 'str',
        'parameter': 'test_parameter',
        'name': 'Test parameter',
        'value': 'A',
        'kwargs': None,
        'description': 'The `Test parameter` setting object.'
    }
    setting: blocks.structures.Setting = blocks.structures.Setting.from_dict(
        dict_object=dict_object
    )
    assert isinstance(setting.to_dict(), dict)
    assert setting.to_dict() == dict_object


def test_setting_to_pandera_success(SETTING_FIXTURE: blocks.structures.Setting):
    assert isinstance(SETTING_FIXTURE.to_pandera(), pandera.Column)


def test_setting_to_selector_success(SETTING_FIXTURE: blocks.structures.Setting):
    selector: blocks.structures.Selector = SETTING_FIXTURE.to_selector()
    assert isinstance(selector, blocks.structures.Selector)
    assert SETTING_FIXTURE.parameter == selector.parameter
    assert SETTING_FIXTURE.name == selector.name
    assert SETTING_FIXTURE.description == selector.description


def test_setting_repr_success(SETTING_FIXTURE: blocks.structures.Setting):
    assert json.dumps(SETTING_FIXTURE.to_dict(), indent=2) == repr(SETTING_FIXTURE)


def test_selector_init_success(SELECTOR_FIXTURE: blocks.structures.Selector):
    assert SELECTOR_FIXTURE.parameter == 'test_parameter'
    assert SELECTOR_FIXTURE.name == 'Test parameter'
    assert SELECTOR_FIXTURE.description == 'The `Test parameter` selector object.'


def test_selector_from_dict_success():
    selector: blocks.structures.Selector = blocks.structures.Selector.from_dict(
        dict_object={
            'parameter': 'test_parameter',
            'name': 'Test parameter',
            'description': 'The `Test parameter` selector object.'
        }
    )
    assert selector.parameter == 'test_parameter'
    assert selector.name == 'Test parameter'
    assert selector.description == 'The `Test parameter` selector object.'


def test_selector_from_dict_parameter_typeerror():
    with pytest.raises(TypeError):
        blocks.structures.Selector.from_dict(
            dict_object=[]
        )


def test_selector_from_dict_keyerror():
    with pytest.raises(KeyError):
        blocks.structures.Selector.from_dict(
            dict_object={
                'type': 'text-input',
                'dtype': 'str'
            }
        )


def test_selector_to_dict_success():
    dict_object = {
        'parameter': 'test_parameter',
        'name': 'Test parameter',
        'description': 'The `Test parameter` selector object.'
    }
    selector: blocks.structures.Selector = blocks.structures.Selector.from_dict(
        dict_object=dict_object
    )
    assert isinstance(selector.to_dict(), dict)
    assert selector.to_dict() == dict_object


def test_selector_repr_success(SELECTOR_FIXTURE: blocks.structures.Selector):
    assert json.dumps(SELECTOR_FIXTURE.to_dict(), indent=2) == repr(SELECTOR_FIXTURE)
