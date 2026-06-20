# HTTP — ibkrapi conventions

- **Routing**: `/<asset_class>/<symbol>/...` plus cross-cutting
  `/orders`, `/positions`, `/account`, `/accounts`, `/history/*`,
  `/ping`. One `APIRouter` per asset class in `ibkrapi/routers/`.
- **Auth**: bearer token via `Authorization: Bearer <token>`. Token
  loaded from `config.yaml.api_token` or `API_TOKEN` env. Empty token
  = open access. Compare in constant time with `hmac.compare_digest`.
- **Error envelope**: `{"code": "UPPER_SNAKE_CASE", "message": "human
  readable", "details": {...optional...}}` returned by
  `ibkrapi.errors.error_response()`. NEVER bare `{"error": "..."}`.
  Codes defined in `ibkrapi/errors.py`.
- **Request bodies**: every POST defines a Pydantic v2 `BaseModel`.
  Query params are explicit FastAPI `Query(...)` declarations, NOT
  `**kwargs` (FastAPI doesn't introspect kwargs into query params).
- **Response shape**: top-level dict, never bare list. Bars/ticks
  always under a named key (`"bars": [...]`, `"ticks": [...]`).
- **Pagination**: not yet — IBKR returns capped result sets and
  ib_async streams them. Add `limit`/`offset` envelope per global rule
  42 when an endpoint outgrows that.
- **Status codes**: 400 for bad input, 401 for missing/bad token, 404
  for unknown contract/order/job, 502 for upstream (IB Gateway /
  wickworks) failures, 503 for "service is up but dependency down"
  (e.g. gateway disconnected).
