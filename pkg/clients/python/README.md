# ibkr-httpapi — Python client

Typed Python client generated from `api/v1.yaml` via `openapi-python-client`.

## Install (from this repo, via git path)

```bash
pip install "git+https://github.com/psyb0t/ibkr-httpapi.git#subdirectory=pkg/clients/python/ibkr-httpapi-client"
```

Or with a specific ref:

```bash
pip install "git+https://github.com/psyb0t/ibkr-httpapi.git@v0.1.0#subdirectory=pkg/clients/python/ibkr-httpapi-client"
```

## Use

```python
import os
from ibkr_httpapi_client import AuthenticatedClient
from ibkr_httpapi_client.api.stocks import get_stock_tick

client = AuthenticatedClient(
    base_url="http://localhost:8889/v1",
    token=os.environ["IBKR_API_TOKEN"],
)
ticker = get_stock_tick.sync(client=client, symbol="AAPL")
print(f"AAPL last={ticker.last}")
```

## Regenerate

In the project root (where `api/v1.yaml` lives):

```bash
make generate-client-python
```

Everything under `ibkr-httpapi-client/` is generated — never hand-edit. Edit the spec and rerun the make target.
