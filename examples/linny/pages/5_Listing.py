""" localhost:{ASSEMBLIT_CLIENT_PORT}/Listing """

from assemblit.pages import run_listing

# Initialize the run-analysis-page content
Listing = run_listing.Content(
    header='Listing',
    tagline='Browse submitted analysis runs.',
    content_info='Navigate to the **Studies** page and select a session.'
)

# Serve content
Listing.serve()
