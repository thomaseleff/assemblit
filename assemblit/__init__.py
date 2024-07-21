"""
🦄 `assemblit` is a Python package that provides a framework of 👑 [streamlit](https://streamlit.io/)
based web-components for quickly assembling end-to-end analytics-as-a-service (AaaS)
web-applications. `assemblit` comes with user-authentication, a lightweight sqlite3-database
backend, and workflow orchestration via 🧊 [prefect](https://www.prefect.io).

**alpha-release** coming soon!
"""

import assemblit.data_toolkit as data_toolkit
import assemblit.web as web

__all__ = ['data_toolkit', 'web']
