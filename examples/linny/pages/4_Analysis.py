""" localhost:{ASSEMBLIT_CLIENT_PORT}/Analysis """

from assemblit.pages import run_analysis

# Initialize the run-analysis-page content
Analysis = run_analysis.Content(
    header='Analysis',
    tagline='Configure and submit a model analysis.',
    content_info='Navigate to the **Studies** page and select a session.'
)

# Serve content
Analysis.serve()
