""" linny.assemblit.org/Listing """

from assemblit.pages import run_listing

# Initialize the run-analysis-page content
Listing = run_listing.Content(
    header='Listing',
    tagling='Browse submitted analysis runs.',
    content_info='Navigate to the **Studies** page and select a session.'
)

# Serve content
Listing.serve()
