"""
Information
---------------------------------------------------------------------
Name        : 4_Listing.py
Location    : ~/pages

Description
---------------------------------------------------------------------
Run-listing-page of the 'linny' web-application.
"""

from assemblit.pages import run_listing

# Initialize the run-analysis-page content
Listing = run_listing.Content()

# Serve content
Listing.serve()
