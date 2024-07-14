"""
Information
---------------------------------------------------------------------
Name        : 4_Analysis.py
Location    : ~/pages

Description
---------------------------------------------------------------------
Run-analysis-page of the 'linny' web-application.
"""

from assemblit.pages import run_analysis

# Initialize the run-analysis-page content
Analysis = run_analysis.Content()

# Serve content
Analysis.serve()
