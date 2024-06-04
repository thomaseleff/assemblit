"""
Information
---------------------------------------------------------------------
Name        : 4_Listing.py
Location    : ~/pages
Author      : Tom Eleff
Published   : 2024-06-04
Revised on  : .

Description
---------------------------------------------------------------------
Run-listing-page of the 'linny' web-application.
"""

from assemblit.pages import run_listing

# Initialize the run-analysis-page content
Listing = run_listing.Content()

# Serve content
Listing.serve()
