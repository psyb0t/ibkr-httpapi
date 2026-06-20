# Logging — ibkrapi conventions

- Logger: stdlib `logging` via `from ibkrapi.logger import log`.
  Configured in `ibkrapi/logger.py`.
- Format: structured JSON, one record per line. Fields: `time`, `level`,
  `file`, `line`, `func`, `msg`, plus any contextual kwargs passed via
  `extra={...}`.
- Targets: stdout (captured by docker logs) AND `logs/full.log`
  (mkdir-locked across processes).
- Levels: DEBUG / INFO / WARN / ERROR all in use.
  - DEBUG: every ib_async call, every contract qualification, every
    branch in routers.
  - INFO: connect/disconnect, startup/shutdown, every request (via
    server.py middleware).
  - WARN: reconnect attempts, parse-failure-but-continue.
  - ERROR: unhandled exceptions (caught by server middleware), gateway
    socket loss.
- NEVER log: `API_TOKEN`, IBKR password (`TWS_PASSWORD`), full request
  bodies (may contain order payloads with account numbers).
- Request middleware emits one INFO line per request in + one out, with
  a short req_id correlator (`os.urandom(4).hex()`).
