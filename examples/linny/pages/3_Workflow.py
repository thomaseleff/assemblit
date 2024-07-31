""" linny.assemblit.org/Workflow """

from assemblit.pages import workflow_settings
from assemblit.blocks.structures import Setting

# Initialize the workflow-settings-page content
Workflow = workflow_settings.Content(
    header='Workflow',
    tagline='Configure the parameters essential to the model workflow.',
    content_info='Navigate to the **Studies** page and select a session.',
    settings=[
        Setting(
            type='text-input',
            dtype='str',
            parameter='y',
            name='Response metric name',
            description='Input the name of the response metric to model.'
        ),
        Setting(
            type='toggle',
            dtype='bool',
            parameter='apply_pruning',
            name='Apply pruning',
            description='If `True`, coerce coefficients to the expected sign.'
        ),
        Setting(
            type='slider',
            dtype='int',
            parameter='num_seasonality_terms',
            name='Number of fourier terms for seasonality.',
            value=2,
            kwargs={
                'min_value': 0,
                'max_value': 4,
                'step': 1
            },
            description='Select the number of fourier terms for seasonality.'
        )
    ]
)

# Serve content
Workflow.serve()
