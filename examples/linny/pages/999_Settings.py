""" linny.assemblit.org/Settings """

from assemblit.pages import account_settings

# Initialize the account-settings-page content
Settings = account_settings.Content()

# Serve content
Settings.serve()
