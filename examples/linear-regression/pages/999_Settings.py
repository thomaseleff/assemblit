"""
Information
---------------------------------------------------------------------
Name        : 999_Settings.py
Location    : ~/pages
Author      : Tom Eleff
Published   : 2024-02-21
Revised on  : .

Description
---------------------------------------------------------------------
Account-settings-page of the 'linny' web-application.
"""

from assemblit.pages import account_settings

# Initialize the account-settings-page content
Settings = account_settings.Content()

# Serve content
Settings.serve()
