# Logging conventions

- Logger: `from ibkrapi.logger import log`, a `LoggerAdapter` over the stdlib `ibkrapi` logger, configured in `ibkrapi/logger.py`. Pass structured fields as keyword arguments: `log.info("order_submit", symbol=..., qty=...)`.
- Format: one JSON object per line with `time`, `level`, `file`, `line`, `func`, `identity` (`<gateway host>:<port>#<client id>`), `msg`, an `exc` traceback when there is one, plus every keyword field.
- Targets: stdout (what `docker compose logs` shows) and `logs/full.log`. File writes take a `mkdir`-based lock so several processes can share one log directory.
- Level: `LOG_LEVEL` environment variable, default `INFO`.
- What each level carries:
  - DEBUG: ib_async calls and contract qualification in `marketdata.py`, wickworks calls.
  - INFO: startup config dump, gateway connect, cache writes, pacing setup, order submits, one `request_in` and one `request_out` line per HTTP request (with a `req_id` from `os.urandom(4).hex()`).
  - WARNING: connect retries, pacing soft and hard caps, cache and historian write failures, wickworks errors, global cancel.
  - ERROR: `request_crash` from the middleware with the traceback.
- The startup line logs only whether `API_TOKEN` is set and its length. Full request bodies are not logged: they can carry account numbers.
