""" Tests the `assemblit._app` subpackage """

import os
import shutil
import pytest
from pytensils import utils
from streamlit.testing.v1 import AppTest
from assemblit.toolkit import _yaml, content
from assemblit._app import layer


PATH = os.path.join(
    os.path.dirname(__file__),
    'resources',
    'app'
)
TIMEOUT = 30


def test_assemblit_build_demo_success():

    # Manage the web-application directory
    if os.path.isdir(PATH):
        shutil.rmtree(PATH)
        os.mkdir(PATH)
    else:
        os.mkdir(PATH)

    # Build
    demo = layer.build(
        app_type='demo',
        path=PATH
    )

    assert os.path.isdir(os.path.join(PATH, '.assemblit'))
    assert os.path.isfile(os.path.join(PATH, '.assemblit', 'config.yaml'))
    assert os.path.isfile(os.path.join(PATH, 'app.py'))
    assert os.path.isfile(os.path.join(PATH, 'README.md'))
    assert demo.ASSEMBLIT_ENV == 'DEV'
    assert demo.ASSEMBLIT_VERSION == 'main'
    assert demo.ASSEMBLIT_DEBUG
    assert demo.ASSEMBLIT_NAME == 'demo'
    assert demo.ASSEMBLIT_HOME_PAGE_NAME == 'app'
    assert demo.ASSEMBLIT_GITHUB_REPOSITORY_URL == 'https://github.com/thomaseleff/assemblit'
    assert demo.ASSEMBLIT_GITHUB_BRANCH_NAME == 'main'
    assert utils.as_type(demo.ASSEMBLIT_CLIENT_PORT, 'int') == 8501
    assert demo.ASSEMBLIT_DIR == PATH


def test_assemblit_build_demo_notimplementederror():
    with pytest.raises(NotImplementedError):
        layer.build(
            app_type='app-type-not-implemented',
            path=PATH
        )


def test_assemblit_demo_app_run_success():

    # Load the web-application configuration
    config = _yaml.load_configuration(path=os.path.abspath(PATH))
    config['assemblit']['app']['env']['ASSEMBLIT_DEBUG'] = False

    # Create the web-application environment
    _ = layer.create_app(config=config)

    # Run the web-application via AppTest
    app = AppTest.from_file(os.path.join(PATH, 'app.py'), default_timeout=TIMEOUT).run()

    assert app.markdown[0].value == '# 🎉 Success!'
    assert app.markdown[1].value == content.clean_text(
        """
        Assemblit is helping data analysts and scientists rapidly scale notebooks
        into analytics-as-a-service (AaaS) web-applications.
        """
    )
