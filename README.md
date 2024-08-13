`alpha-release` coming soon!

🦄 `assemblit` is a Python package that provides a framework of 👑 [streamlit](https://streamlit.io/) based web-components for quickly assembling end-to-end analytics-as-a-service (AaaS) web-applications. `assemblit` comes with user-authentication, a lightweight sqlite3-database backend, and workflow orchestration via 🧊 [prefect](https://www.prefect.io).

## Installation
The source code is available on [GitHub](https://github.com/thomaseleff/assemblit).

`assemblit` can be installed via PyPI from the command-line, which allows for developing locally before deploying.

1. Setup a Python developer environment. `assemblit` supports Python versions >= 3.10.
2. From the command-line, run,

   ```
   # Via PyPI
   pip install assemblit
   ```

3. Validate the installation by running,

   ```
   pip show assemblit
   ```

## First steps
Build your first `assemblit` app with the command-line utility.

1. Create a new folder to contain your `assemblit` project.
2. Open a command prompt and navigate into the new folder.
3. From the command-line, run,

   ```
   assemblit build demo
   ```
