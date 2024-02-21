"""
Information
---------------------------------------------------------------------
Name        : 3_Workflow.py
Location    : ~/
Author      : Tom Eleff
Published   : 2024-02-21
Revised on  : .

Description
---------------------------------------------------------------------
Workflow-settings-page of the getstreamy web-application.
"""

import getstreamy.pages.workflow_settings as workflow_settings

# Initialize the workflow-settings-page content
Workflow = workflow_settings.Content(
    content_info='Navigate to the **Studies** page to load a session.',
    settings=[
        {
            "sort": 0,
            "type": "text-input",
            "dtype": "str",
            "parameter": "Y",
            "name": "Response metric name",
            "value": "",
            "kwargs": False,
            "description": """
                Input the name of the Response metric to model.
            """
        },
        {
            "sort": 1,
            "type": "toggle",
            "dtype": "bool",
            "parameter": "tune_this_time",
            "name": "Estimate tuning hyper-parameters",
            "value": True,
            "kwargs": False,
            "description": """
                If ```False```,
                the saved hyper-parameters will be used.
            """
        },
        {
            "sort": 2,
            "type": "text-input",
            "dtype": "str",
            "parameter": "saved_hypers_filename",
            "name": "Saved hyper-parameters filename",
            "value": "",
            "kwargs": False,
            "description": """
                Input the name of the hyper-parameters source file
                when _Estimate tuning hyper-parameters_ = ```False```
            """
        },
        {
            "sort": 3,
            "type": "toggle",
            "dtype": "bool",
            "parameter": "search_seasonality",
            "name": "Select optimal seasonality controls",
            "value": True,
            "kwargs": False,
            "description": """
                If ```True```,
                the optimal seasonal controls are automatically selected.
            """
        },
        {
            "sort": 4,
            "type": "slider",
            "dtype": "int",
            "parameter": "fft_terms",
            "name": "Number of fourier terms for seasonality",
            "value": 2,
            "kwargs": {
                "min_value": 0,
                "max_value": 5,
                "step": 1
            },
            "description": """
                Select the number of fourier terms.
                ```2``` is roughly semi-annual & trimesters,
                ```3``` is semi-annual, trimesters and quarters.
            """
        },
        {
            "sort": 5,
            "type": "text-input",
            "dtype": "str",
            "parameter": "interaction_fft",
            "name": "Seasonality interaction dimensions",
            "value": "",
            "kwargs": None,
            "description": """
                Input the dimension names to evaluate
                as seasonality interactions.
            """
        },
        {
            "sort": 6,
            "type": "toggle",
            "dtype": "bool",
            "parameter": "search_randoms",
            "name": "Evaluate multiple random effects",
            "value": False,
            "kwargs": False,
            "description": """
                If ```True```, multiple random effects will be evaluated.
            """
        },
        {
            "sort": 7,
            "type": "text-input",
            "dtype": "str",
            "parameter": "list_rand_ints",
            "name": "List random effects intercepts",
            "value": "",
            "kwargs": None,
            "description": """
                Input the dimension names that should have random effects.
            """
        },
        {
            "sort": 8,
            "type": "text-input",
            "dtype": "str",
            "parameter": "list_rand_slopes",
            "name": "List factors for random slopes",
            "value": "",
            "kwargs": None,
            "description": """
                Input the factor names that should have random slopes.
            """
        }
    ]
)

# Serve content
Workflow.serve()
