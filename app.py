""" Entrypoint

``` python
assemblit run app.py
```
"""

import streamlit as st

routes = {
    '': [
        st.Page(page='site/welcome.py', title='Home', url_path='home', default=True),
    ],
    'Documentation': [
        st.Page(page='site/documentation/getting_started.py', title='Getting started', url_path='documentation/getting-started'),
        # st.Page(page='site/documentation/getting_started.py', title='Develop', url_path='documentation/develop'),
        # st.Page(page='site/documentation/getting_started.py', title='    AaaS', url_path='documentation/develop/aaas'),
        # st.Page(page='site/documentation/getting_started.py', title='    Wiki', url_path='documentation/develop/wiki'),
        # st.Page(page='site/documentation/getting_started.py', title='Deploy', url_path='documentation/deploy'),
        # st.Page(page='site/documentation/getting_started.py', title='    Docker', url_path='documentation/deploy/docker')
    ],
    'CLI reference': [
        st.Page(page='site/cli_reference/1_assemblit.py', title='assemblit', url_path='lib/assemblit/app/cli'),
        st.Page(page='site/cli_reference/2_orchestrator.py', title='orchestrator', url_path='lib/assemblit/orchestrator/cli')
    ],
    'API reference': [
        st.Page(page='site/api_reference/1_assemblit.py', title='assemblit', url_path='lib/assemblit'),
        st.Page(page='site/api_reference/1a_setup.py', title='    setup', url_path='lib/assemblit/setup'),
        st.Page(page='site/api_reference/1b_blocks.py', title='    blocks', url_path='lib/assemblit/blocks'),
        st.Page(page='site/api_reference/1c_pages.py', title='    pages', url_path='lib/assemblit/pages'),
        st.Page(page='site/api_reference/1d_toolkit.py', title='    toolkit', url_path='lib/assemblit/toolkit')
    ]
}

app = st.navigation(pages=routes, position='sidebar')
app.run()
