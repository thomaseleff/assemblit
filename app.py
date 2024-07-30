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
    'API reference': [
        st.Page(page='site/api_reference/1_assemblit.py', title='assemblit', url_path='lib/assemblit'),
        st.Page(page='site/api_reference/1a_app.py', title='    app', url_path='lib/assemblit/app'),
        st.Page(page='site/api_reference/1ai_cli.py', title='        cli', url_path='lib/assemblit/app/cli'),
        st.Page(page='site/api_reference/1b_setup.py', title='    setup', url_path='lib/assemblit/setup'),
        st.Page(page='site/api_reference/1c_blocks.py', title='    blocks', url_path='lib/assemblit/blocks'),
        st.Page(page='site/api_reference/1d_pages.py', title='    pages', url_path='lib/assemblit/pages'),
        st.Page(page='site/api_reference/1e_toolkit.py', title='    toolkit', url_path='lib/assemblit/toolkit'),
        st.Page(page='site/api_reference/1f_auth.py', title='    auth', url_path='lib/assemblit/auth'),
        st.Page(page='site/api_reference/1g_database.py', title='    database', url_path='lib/assemblit/database'),
        st.Page(page='site/api_reference/1h_server.py', title='    server', url_path='lib/assemblit/server'),
        st.Page(page='site/api_reference/1hi_cli.py', title='        cli', url_path='lib/assemblit/server/cli')
    ]
}

app = st.navigation(pages=routes, position='sidebar')
app.run()
