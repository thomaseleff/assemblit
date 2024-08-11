""" localhost:{ASSEMBLIT_CLIENT_PORT}/Studies """

from assemblit.pages import session_selector
from assemblit.blocks.structures import Setting, Selector

# Initialize the session-selector page content
Sessions = session_selector.Content(
    header='Studies',
    tagline='Select a study for the session.',
    settings=[
        Setting(
            type='text-input',
            dtype='str',
            parameter='study_name',
            name='Study Name',
            description='Input the name of a new study.'
        ),
        Setting(
            type='text-input',
            dtype='str',
            parameter='country',
            name='Country name',
            description='Input the name of the corresponding country.'
        )
    ],
    selector=Selector(parameter='study_name')
)

# Serve content
Sessions.serve()
