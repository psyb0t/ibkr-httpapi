# Stack choices

- **Python 3.12**, asyncio everywhere. Images use `python:3.12-slim-bookworm` pinned by digest.
- **FastAPI + uvicorn** for HTTP, not Flask or waitress. `ib_async` is asyncio-native and shares the event loop with the handlers; a sync framework would need `asyncio.run_coroutine_threadsafe` on every call.
- **`ib_async`** (2.x) over the TWS API socket, not `ib_insync` (dead upstream) and not the Client Portal Web API (`ibind`, `ibeam`). One shared `IB()` instance from `ibkrapi.ibclient.get_ib()`. Option exercise exists only on the socket API, which is one reason for this choice.
- **Pydantic v2** models, generated from `api/v1.yaml`. Not marshmallow.
- **YAML config** read by hand in `ibkrapi/config.py` into module constants, with CLI flag and environment overrides. Not pydantic-settings.
- **`urllib.request`** for the outbound wickworks call (stdlib, no requests or httpx). `httpx` appears only in `ibkrapi/mcp_server.py` for its in-process ASGI transport, which comes with the `mcp` package.
- **MCP** through the official `mcp` SDK's `FastMCP`, stateless streamable HTTP, mounted on the same FastAPI app.
