# Stack — locked-in conventions for ibkr-httpapi

- **Python 3.12**, asyncio everywhere.
- **FastAPI + uvicorn** for HTTP. NOT Flask. NOT waitress. `ib_async` is
  asyncio-native and shares the loop with the request handlers; Flask
  would force `asyncio.run_coroutine_threadsafe` everywhere.
- **`ib_async`** (v2.x), NOT `ib_insync` (dead upstream) and NOT the
  Client Portal Web API path (`ibind` + `ibeam`). Single shared `IB()`
  instance from `ibkrapi.ibclient.get_ib()`.
- **Pydantic v2** for request body validation. NOT marshmallow.
- **YAML config** parsed by hand in `ibkrapi/config.py` (matches
  mt5-httpapi's gonfiguration-style layout). NOT pydantic-settings.
- **`urllib.request`** for the wickworks HTTP call (stdlib, no
  requests/httpx). Matches mt5-httpapi.
