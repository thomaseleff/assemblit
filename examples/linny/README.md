🚨 *`linny` is currently under active development, some functionality may not work as expected.*

## Installation
To self-host 🚀 `linny` locally, clone the Github repository to access the source files.

1. Create a new folder to contain the cloned Github repository.
2. Navigate into the new folder and open a git bash terminal.
3. From the git bash terminal, run,

   ```
   git clone -b main https://github.com/thomaseleff/assemblit.git
   ```

4. Follow the installation instructions to install `assemblit`.
5. Open a command prompt and navigate into the root directory, `./assemblit/examples/linny`.
6. From the command-line, run the following command to run the web-application,

   ```
   assemblit run Home.py
   ```

7. Open another command prompt and navigate into the same root directory.
8. From the command-line, run the following command to start the `prefect` orchestration server,

   ```
   orchestrator start .
   ```

8. Sign-up with your email in the browser and start running and evaluating linear-regression models!
