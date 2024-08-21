""" Tests the `assemblit.pages` subpackage """

import os
import socket
from streamlit.testing.v1 import AppTest
import subprocess
from assemblit.toolkit import _yaml, content
from assemblit._app import layer


PATH = os.path.join(
    os.path.dirname(__file__),
    'resources',
    'app'
)
TIMEOUT = 30


def test_assemblit_build_demo_success():

    # Create application directory
    if not os.path.isdir(PATH):
        os.mkdir(PATH)

    app = subprocess.Popen('assemblit build demo', shell=True, cwd=PATH)

    # Check if the default localhost:port is open
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(TIMEOUT)

    if sock.connect_ex(('localhost', 8501)) == 0:
        app.terminate()
        app.wait()
        sock.close()
        assert True
    else:
        raise AssertionError(
            '{localhost:8501} is not open or the socket connection timed-out.'
        )


def test_assemblit_demo_success():

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
