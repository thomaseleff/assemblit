🚨 *`linny` is currently under active development, some functionality may not work as expected.*

## Workflow
Running and managing 🚀 `linny` workflows is simple, with four basic stages.

```
+---------------+ +---------------+ +---------------+ +---------------+
| 1.            | | 2.            | | 3.            | | 4.            |
|               | |               | |               | |               |
|   Set up a    +->   Upload &    +->   Configure   +->    Run an     |
|     Study     | | validate data | |  the workflow | |   analysis    |
|               | |               | |               | |               |
+---------------+ +---------------+ +---------------+ +---------------+
```

### 1. Set up a Study

   A **Study** sets the scope for a particular session within `linny`. You can configure and manage any number of studies within the **Studies** module. All uploaded data, configured workflow parameters and workflow runs are associated with the selected scope for that session. Use the 🔍 icon in the upper right-hand corner to inspect the selected **Study** throughout the application.

### 2. Upload & validate data

   You can upload, validate, review and analyze any number of input datafiles within `linny`. The **Date** module enforces schema rules for all uploads and builds a simple data review. The data review contains,

   - A **Preview** of the first 5 obserations of a newly uploaded datafile.
   - An interactive **Review** for exploring timeseries and descriptive summaries of any uploaded datafile and for finalizing a dataset for the selected **Study**.

### 3. Configure the workflow

   The `linny` analysis workflow accepts a number of parameters that are essential to the analysis. The **Workflow** module allows for setting parameter values for your next workflow run. The following parameters are available,

   - *Response metric name* - The response metric of the model.
   - *Apply pruning* - If `True`, coefficients are coerced to the expected sign.
   - *Number of fourier terms for seasonality* - The number of fourier terms to apply for the effects of seasonal changes in the response metric.

   The parameters are passed into the model analysis entrypoint as workflow run request parameters.

### 4. Run an analysis

   The **Analysis** module allows for submitting `linny` workflow runs. The workflow runs are submitted to the `prefect` orchestration server with the current **Workflow** parameter configuration. The status of any currently executing workflow runs and a record of all previous runs are available within the **Listing** page. The inputs and outputs for each run can be found within the following relative local directories of the root folder,

   - Inputs
     - Countains the input datafile selected within the **Analysis** module for the workflow run as well as the run request parameters from the **Workflow** module.
     - Path: `./analysis/{run_id}/inputs`

   - Outputs
     - Countains the output datafiles generated as a part of the workflow run.
     - Path: `./analysis/{run_id}/outputs`
