"""
Information
---------------------------------------------------------------------
Name        : 2_Data.py
Location    : ~/pages
Author      : Tom Eleff
Published   : 2024-02-21
Revised on  : .

Description
---------------------------------------------------------------------
Data-ingestion-page of the getstreamy web-application.
"""

import os
import pandas as pd
from assemblit import setup
from assemblit.pages import data_ingestion

# Initialize the data-ingestion-page content
Data = data_ingestion.Content(
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
