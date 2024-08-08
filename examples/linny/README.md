# Linear regression analysis
A linear regression analysis with a linear regression assumption evaluator, orchestrated by `prefect`.


``` bash
prefect config set PREFECT_LOGGING_LEVEL="DEBUG"
prefect config set PREFECT_API_URL="http://127.0.0.1:4200/api"
prefect server start
prefect deployment run 'linear-regression-flow/linear-regression-deployment' --params '{"user": "Marvin", "answer": 42}'
```

``` bash
curl -X GET http://127.0.0.1:4200/api/flow_runs/52558f9d-f7b0-4710-8801-50b636eeba64  # Returns flow-run info
```

For docker...
``` bash
prefect work-pool create subprocess-pool --type process --set-as-default
prefect worker start --pool subprocess-pool
```