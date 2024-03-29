"""
Information
---------------------------------------------------------------------
Name        : 4_Run analysis.py
Location    : ~/pages
Author      : Tom Eleff
Published   : 2024-02-21
Revised on  : .

Description
---------------------------------------------------------------------
Run-analysis-page of the getstreamy web-application.
"""

from assemblit.pages import run_analysis

# Initialize the run-analysis-page content
Analysis = run_analysis.Content()

# Serve content
Analysis.serve()
