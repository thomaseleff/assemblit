""" linny.assemblit.org/Data """

import os
import pandas as pd
from assemblit import setup
from assemblit.pages import data_ingestion

# Initialize the data-ingestion-page content
Data = data_ingestion.Content(
    header='Data',
    tagline='Upload, review and finalize the model input data for the session.',
    content_info='Navigate to the **Studies** page and select a session.',
    data_dictionary=pd.read_csv(
        os.path.join(
            setup.ROOT_DIR,
            'contract',
            'data_dictionary.csv'
        ),
        sep=','
    ),
    data_example=pd.read_csv(
        os.path.join(
            setup.ROOT_DIR,
            'contract',
            'data_example.csv'
        ),
        sep=','
    )
)

# Serve content
Data.serve()
