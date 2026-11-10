---
title: "REST API"
description: "Every ibkr-httpapi REST endpoint under /v1: contracts, quotes, bars, ticks, TA, option chains, combos, exercise, orders, positions, account and history."
nav_order: 5
---

# REST API

Every endpoint lives under `/v1` on the address nginx publishes, `http://localhost:8889/v1` by default. Requests and responses are JSON. The operations come from the OpenAPI spec in [`api/v1.yaml`](https://github.com/psyb0t/ibkr-httpapi/blob/main/api/v1.yaml), and the running app serves its own schema at `/openapi.json` with Swagger UI at `/docs` (both outside `/v1`, both behind the token).

```bash
export IBKR=http://localhost:8889/v1
export API_TOKEN=<your api_token>

curl -s -H "Authorization: Bearer $API_TOKEN" "$IBKR/ping"
```

The examples below leave out the `Authorization` header to stay short. Send it on every request when `api_token` is set.

## Authentication

When `api_token` (or `API_TOKEN`) is set, every request needs `Authorization: Bearer <token>`. That includes `/v1/ping`, `/openapi.json`, `/docs` and the MCP endpoint. A missing or wrong token gets `401` with code `UNAUTHORIZED`. With an empty token there is no auth at all. See [Security](security.md).

## Conventions

### Routes by asset class

| Prefix | Asset class | IBKR `secType` | Path parameter |
| --- | --- | --- | --- |
| `/stocks/{symbol}` | Equities | `STK` | symbol, 1 to 32 characters |
| `/options/{symbol}` | Options on the underlying `symbol` | `OPT` | underlying symbol |
| `/futures/{symbol}` | Futures | `FUT` | root symbol |
| `/cfd/{symbol}` | CFDs | `CFD` | symbol |
| `/forex/{pair}` | Currency pairs | `CASH` | pair such as `EURUSD`, 6 to 12 characters |
| `/crypto/{symbol}` | Crypto | `CRYPTO` | symbol such as `BTC` |

Each class has the same five routes, except that historical ticks exist only for stocks:

| Method and path | Returns |
| --- | --- |
| `GET /<class>/{symbol}` | Contract details. |
| `GET /<class>/{symbol}/tick` | A snapshot quote, with Greeks for options. |
| `GET /<class>/{symbol}/rates` | Historical OHLC bars. |
| `GET /stocks/{symbol}/ticks` | Historical trade or quote ticks. |
| `POST /<class>/{symbol}/rates/ta` | Bars plus technical indicators from wickworks. |

### Contract selection

These query parameters pick the contract on every route of a class. Leaving one out uses `contract_defaults` from [the configuration](configuration.md#contract-defaults).

| Class | Required | Optional |
| --- | --- | --- |
| stocks | | `exchange`, `currency`, `primaryExchange` |
| options | `expiry` (`YYYYMMDD` or `YYYYMM`), `strike`, `right` (`C`, `P`, `CALL` or `PUT`) | `exchange`, `currency`, `multiplier`, `tradingClass` |
| futures | `expiry` (`YYYYMM` or `YYYYMMDD`), `exchange` (`CME`, `NYMEX`, ...) | `currency`, `multiplier`, `tradingClass` |
| cfd | | `exchange`, `currency` |
| forex | | `exchange` |
| crypto | | `exchange`, `currency` |

An option `right` outside those four values is not caught by validation and ends in a `500`.

### Bar sizes and data types

`barSize` takes a short form or IBKR's own string. Leaving it out means one hour.

| Short form | IBKR string |
| --- | --- |
| `1s` `5s` `10s` `15s` `30s` | `1 secs` `5 secs` `10 secs` `15 secs` `30 secs` |
| `1m` `2m` `3m` `5m` `10m` `15m` `20m` `30m` | `1 min` `2 mins` `3 mins` `5 mins` `10 mins` `15 mins` `20 mins` `30 mins` |
| `1h` `2h` `3h` `4h` `8h` | `1 hour` `2 hours` `3 hours` `4 hours` `8 hours` |
| `1d` `1w` `1mo` | `1 day` `1 week` `1 month` |

Anything else gets `400 BAD_REQUEST` with the accepted list in `details.accepted`.

`whatToShow` accepts `TRADES`, `MIDPOINT`, `BID`, `ASK`, `BID_ASK`, `ADJUSTED_LAST`, `HISTORICAL_VOLATILITY` and `OPTION_IMPLIED_VOLATILITY`, in any case. The default is `TRADES`, also for forex `/rates`; IDEALPRO has no trade data, so pass `whatToShow=MIDPOINT` for forex bars. Only forex `/rates/ta` defaults to `MIDPOINT`.

`duration` is IBKR's duration string: an integer, a space and a unit (`S`, `D`, `W`, `M`, `Y`), such as `60 S`, `30 D`, `13 W`, `6 M`, `1 Y`. Encode the space as `+` or `%20` in a URL. `endDateTime` is empty for now or `YYYYMMDD HH:MM:SS` in UTC.

### The refresh parameter

`refresh=true` is accepted on contract details, `/rates`, `/ticks`, `/rates/ta`, `/options/{symbol}/chain`, `/futures/{symbol}/continuous`, `/futures/{symbol}/contracts` and both `/history` routes. It only changes anything where a response can come from disk: contract details, the chain and the two futures lists skip their cached copy and fetch again. Bars, ticks and history always come from IBKR. See [Pacing and history](pacing-and-history.md).

### Errors

Every error has the same body:

```json
{
  "code": "NOT_FOUND",
  "message": "Contract not found or not qualifyable",
  "details": {
    "secType": "STK",
    "symbol": "NOPE"
  }
}
```

`details` is optional. Switch on `code`, not on `message`.

| Status | `code` | When |
| --- | --- | --- |
| 400 | `BAD_REQUEST` | Unsupported bar size or data type, an order missing a required field, an unknown `assetClass`, `action` or exercise action, a chain request for a non-stock underlying without `underlyingConId`. |
| 401 | `UNAUTHORIZED` | Missing or wrong bearer token. |
| 404 | `NOT_FOUND` | IBKR could not qualify the contract, returned no contract details or account summary, or the order is not open. Also an unknown path (with FastAPI's own body). |
| 422 | `VALIDATION_FAILED` | The request did not match the schema. `details.errors` lists each problem. |
| 429 | `RATE_LIMIT_NEAR` | The pacing gate refused the call. See [below](#rate-limits). |
| 500 | `INTERNAL_SERVER_ERROR` | An uncaught exception. The message names the exception class; the traceback is in the api log. |
| 502 | `UPSTREAM_FAILED` | Wickworks answered with an error or was unreachable, or IBKR returned no ticker for a snapshot. |
| 503 | `TA_SIDECAR_UNAVAILABLE` | `wickworks.url` is empty or not `http(s)`. |

When the gateway is disconnected, requests do not fail fast: they wait for the reconnect. See [troubleshooting](troubleshooting.md#requests-hang-and-then-return-504).

### Rate limits

Every call that reaches IBKR passes a pacing gate first. When a limit is close, the API answers `429` before IBKR would have rejected the request:

```json
{
  "code": "RATE_LIMIT_NEAR",
  "message": "Approaching IBKR historical pacing (55/60 per 600s). Backing off to protect API access.",
  "details": {
    "rule": "historical_60_per_600s",
    "used": 55,
    "limit": 60,
    "window_sec": 600,
    "retry_after_sec": 312,
    "tier": "historical"
  }
}
```

Wait `retry_after_sec` and retry. The per-contract variant has `rule: <tier>_per_contract_per_sec`, a `contract` key and `retry_after_sec: 1`. Limits and tiers are on the [pacing page](pacing-and-history.md#pacing).

## System and account

### GET /ping

Gateway connection state.

```bash
curl -s "$IBKR/ping"
```

```json
{
  "status": "ok",
  "connected": true,
  "serverVersion": 178,
  "startTime": "2026-06-19T00:00:00+00:00",
  "uptimeSeconds": 3600.2,
  "msgsSent": 512,
  "msgsRecv": 2048
}
```

`/ping` connects first if it has to, so it only answers once the gateway socket is up.

### GET /accounts

```json
{
  "accounts": [
    "DU1234567"
  ]
}
```

Paper accounts start with `DU`, live ones with `U`.

### GET /account and GET /account/values

Both take an optional `account` query parameter. `/account` is IBKR's account summary (`accountSummaryAsync`), `/account/values` is the longer account values list. A summary with no rows is a `404`.

```json
{
  "accounts": {
    "DU1234567": {
      "NetLiquidation": {
        "value": "1000000.00",
        "currency": "USD",
        "modelCode": ""
      },
      "BuyingPower": {
        "value": "4000000.00",
        "currency": "USD",
        "modelCode": ""
      }
    }
  }
}
```

Values are the strings IBKR sends.

### GET /positions

Optional `account` filter.

```json
{
  "positions": [
    {
      "account": "DU1234567",
      "contract": {
        "conid": 265598,
        "symbol": "AAPL",
        "secType": "STK",
        "exchange": "NASDAQ",
        "currency": "USD"
      },
      "position": 10.0,
      "avgCost": 180.25
    }
  ]
}
```

The `contract` object has more fields than shown here: `primaryExchange`, `lastTradeDateOrContractMonth`, `strike`, `right`, `multiplier`, `tradingClass`, `localSymbol`.

## Market data

### GET /{class}/{symbol}: contract details

Contract selection parameters as above, plus `refresh`. Served from the 7-day contract details cache when present.

```bash
curl -s "$IBKR/stocks/AAPL"
curl -s "$IBKR/options/AAPL?expiry=20260619&strike=200&right=C"
curl -s "$IBKR/futures/ES?expiry=202609&exchange=CME"
curl -s "$IBKR/forex/EURUSD"
```

```json
{
  "contracts": [
    {
      "contract": {
        "conid": 265598,
        "symbol": "AAPL",
        "secType": "STK"
      },
      "marketName": "NMS",
      "minTick": 0.01,
      "orderTypes": [
        "LMT",
        "MKT"
      ],
      "validExchanges": [
        "SMART",
        "NASDAQ"
      ],
      "longName": "APPLE INC",
      "timeZoneId": "US/Eastern",
      "tradingHours": "...",
      "liquidHours": "..."
    }
  ]
}
```

Other fields: `priceMagnifier`, `industry`, `category`, `subcategory`, `evRule`, `evMultiplier`.

### GET /{class}/{symbol}/tick: snapshot quote

Contract selection parameters only. Each call also appends a row to the snapshot history.

```bash
curl -s "$IBKR/stocks/AAPL/tick"
curl -s "$IBKR/options/AAPL/tick?expiry=20260619&strike=200&right=C"
curl -s "$IBKR/futures/ES/tick?expiry=202609&exchange=CME"
curl -s "$IBKR/crypto/BTC/tick?currency=USD"
```

Fields, all nullable: `time`, `bid`, `bidSize`, `ask`, `askSize`, `last`, `lastSize`, `close`, `open`, `high`, `low`, `volume`, `vwap`, `halted`, plus `contract`. Options add `modelGreeks`, `bidGreeks`, `askGreeks` and `lastGreeks`, each with `impliedVol`, `delta`, `gamma`, `theta`, `vega`, `optPrice` and `undPrice`; a Greeks object is `null` when IBKR sent none. Real-time Greeks need an OPRA subscription and `market_data_type: 1`; with delayed data they are often `null`.

### GET /{class}/{symbol}/rates: historical bars

| Parameter | Required | Default | Notes |
| --- | --- | --- | --- |
| `duration` | yes | | IBKR duration string. |
| `barSize` | no | `1h` | See [bar sizes](#bar-sizes-and-data-types). |
| `endDateTime` | no | now | `YYYYMMDD HH:MM:SS` UTC. |
| `whatToShow` | no | `TRADES` | Use `MIDPOINT` for forex. |
| `useRTH` | no | `false` | Regular trading hours only. |
| `refresh` | no | `false` | No effect: bars are always fetched. |

Plus the class's contract selection parameters.

```bash
curl -s "$IBKR/stocks/AAPL/rates?duration=1+Y&barSize=1d&whatToShow=ADJUSTED_LAST"
curl -s "$IBKR/options/AAPL/rates?expiry=20260619&strike=200&right=C&duration=10+D&barSize=1h"
curl -s "$IBKR/futures/ES/rates?expiry=202609&exchange=CME&duration=30+D&barSize=1d"
curl -s "$IBKR/forex/EURUSD/rates?duration=30+D&barSize=1h&whatToShow=MIDPOINT"
```

```json
{
  "symbol": "AAPL",
  "secType": "STK",
  "bars": [
    {
      "time": "2026-06-18T00:00:00",
      "open": 196.1,
      "high": 198.4,
      "low": 195.7,
      "close": 197.9,
      "volume": 51234567.0,
      "average": 197.2,
      "barCount": 312345
    }
  ]
}
```

Forex responses carry `pair` instead of `symbol`; options add `expiry`, `strike` and `right`; futures add `expiry`. Every response is also merged into the bars CSV on disk. That step currently breaks `/rates` and `/rates/ta` with the default config; see [troubleshooting](troubleshooting.md#rates-returns-500-with-internal-error-typeerror).

### GET /stocks/{symbol}/ticks: historical ticks

| Parameter | Default | Notes |
| --- | --- | --- |
| `startDateTime`, `endDateTime` | empty | Window bounds, `YYYYMMDD HH:MM:SS` UTC. IBKR wants one of them. |
| `numberOfTicks` | `1000` | 1 to 1000. |
| `whatToShow` | `TRADES` | `TRADES`, `BID_ASK` or `MIDPOINT`. |
| `useRTH` | `false` | |
| `exchange`, `currency`, `primaryExchange`, `refresh` | | |

```json
{
  "symbol": "AAPL",
  "secType": "STK",
  "ticks": [
    {
      "time": "2026-06-18T14:30:00.123000+00:00",
      "price": 197.5,
      "size": 100.0,
      "bid": null,
      "ask": null,
      "bidSize": null,
      "askSize": null
    }
  ]
}
```

Ticks are not stored on disk.

### POST /{class}/{symbol}/rates/ta: bars with indicators

A POST that reads only. Contract selection parameters (and `refresh`) go in the query string; the bar window and indicator spec go in the body. The bars come through the same path as `/rates`, then the API POSTs them to wickworks.

| Body field | Required | Default | Notes |
| --- | --- | --- | --- |
| `duration` | yes | | IBKR duration string. |
| `barSize` | no | `1h` | |
| `endDateTime` | no | now | |
| `whatToShow` | no | `TRADES` (`MIDPOINT` for forex) | |
| `useRTH` | no | `false` | |
| `indicators` | no | `{}` | Wickworks indicator spec, passed through unchanged. |
| `recentBars` | no | | Passed to wickworks as `recentBars`. |

```bash
curl -s -X POST "$IBKR/stocks/AAPL/rates/ta" \
  -H "Content-Type: application/json" \
  -d '{
    "duration": "200 D",
    "barSize": "1d",
    "whatToShow": "ADJUSTED_LAST",
    "indicators": {
      "rsi": true,
      "macd": true,
      "bbands": {
        "length": 20,
        "std": 2
      }
    }
  }'
```

The response is `{"symbol", "secType", "bars", "ta", "asOf"}`, where `ta` is the `ta` object wickworks returned. Indicator names and parameters are wickworks' own; its [indicator list](https://github.com/psyb0t/docker-wickworks#available-indicators) is the reference. Fetch about twice the slowest indicator's lookback so it has warm-up bars.

`503 TA_SIDECAR_UNAVAILABLE` means no wickworks URL is configured. `502 UPSTREAM_FAILED` carries wickworks' status and the first 500 bytes of its body in `details`.

## Options

### GET /options/{symbol}/chain

Expirations and strikes for each exchange and trading class.

| Parameter | Default | Notes |
| --- | --- | --- |
| `underlyingSecType` | `STK` | For any other type you must pass `underlyingConId`. |
| `futFopExchange` | empty | Exchange for options on futures. |
| `underlyingConId` | | Skips qualifying the underlying. |
| `refresh` | `false` | Bypass the 1-day chain cache. |

```json
{
  "symbol": "AAPL",
  "underlyingConId": 265598,
  "chains": [
    {
      "exchange": "SMART",
      "tradingClass": "AAPL",
      "multiplier": "100",
      "expirations": [
        "20260619",
        "20260717"
      ],
      "strikes": [
        195.0,
        200.0,
        205.0
      ]
    }
  ]
}
```

Each call also appends one row per expiry and strike to the chain history on disk, so a large chain writes many rows.

### POST /options/combo

Places a real multi-leg (BAG) order. Resolve each leg's `conid` first with `GET /options/{symbol}`.

| Field | Required | Default | Notes |
| --- | --- | --- | --- |
| `symbol` | yes | | Underlying. |
| `legs` | yes | | Array of `{conid, ratio, action, exchange}`; `ratio` defaults to 1, `exchange` to `SMART`. |
| `action` | yes | | `BUY` or `SELL` for the whole combo. |
| `quantity` | yes | | Integer. |
| `orderType` | no | `LMT` | `LMT` or `MKT` only. |
| `lmtPrice` | for `LMT` | | |
| `tif` | no | `DAY` | |
| `exchange`, `currency` | no | `SMART`, `USD` | |
| `account` | no | | |

```bash
curl -s -X POST "$IBKR/options/combo" \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "AAPL",
    "legs": [
      {
        "conid": 681000001,
        "ratio": 1,
        "action": "BUY"
      },
      {
        "conid": 681000002,
        "ratio": 1,
        "action": "SELL"
      }
    ],
    "action": "BUY",
    "quantity": 1,
    "orderType": "LMT",
    "lmtPrice": 1.20
  }'
```

Returns a [Trade](#trade-object).

### POST /options/exercise

Exercises or lapses a real option position. The TWS socket API supports this; IBKR's Client Portal REST API does not.

| Field | Required | Default | Notes |
| --- | --- | --- | --- |
| `conid` | yes | | The option contract. |
| `action` | yes | | `EXERCISE` or `LAPSE`. |
| `quantity` | yes | | At least 1. |
| `account` | yes | | |
| `override` | no | `false` | Ask IBKR to override its own exercise decision. |

```bash
curl -s -X POST "$IBKR/options/exercise" \
  -H "Content-Type: application/json" \
  -d '{
    "conid": 681000001,
    "action": "EXERCISE",
    "quantity": 1,
    "account": "DU1234567"
  }'
```

Returns `{"status": "submitted", "contract": {...}, "action": "EXERCISE"}`. A `conid` IBKR cannot qualify is a `404`.

## Futures

### GET /futures/{symbol}/continuous

The continuous contract (`CONTFUT`). Requires `exchange`; takes `currency` (default `USD`) and `refresh`. Cached for the contract details TTL.

### GET /futures/{symbol}/contracts

Every listed expiry. Requires `exchange`; takes `currency`, `includeExpired` (default `false`) and `refresh`. Cached for one day.

Both return the contract details shape, `{"contracts": [...]}`.

## Orders

Every `POST` and `DELETE` here changes a real account.

### GET /orders

Open trades as the gateway has reported them to this API connection: `{"trades": [Trade, ...]}`.

### GET /orders/{orderId}

One open trade, or `404` if the order is not open.

### POST /orders

Places one order on any asset class.

| Field | Required | Default | Notes |
| --- | --- | --- | --- |
| `assetClass` | yes | | `stock`/`stk`, `option`/`opt`, `future`/`fut`, `cfd`, `forex`/`cash`, `crypto`. |
| `symbol` | yes | | For forex, the pair. |
| `action` | yes | | `BUY` or `SELL`. |
| `quantity` | yes | | Greater than 0. |
| `orderType` | no | `MKT` | See below. |
| `lmtPrice` | for `LMT`, `STP_LMT` | | |
| `auxPrice` | for `STP`, `STP_LMT` | | The stop trigger. |
| `tif` | no | `DAY` | Time in force, such as `GTC`. |
| `outsideRth` | no | `false` | |
| `transmit` | no | `true` | `false` stages the order in the gateway without sending it. |
| `expiry`, `strike`, `right` | options | | Futures need `expiry` and `exchange`. |
| `exchange`, `currency`, `multiplier`, `tradingClass`, `primaryExchange` | no | contract defaults | |
| `conid` | no | | When set and positive, the API builds the contract from it and ignores the other contract fields. |
| `account` | no | gateway default | |
| `goodAfterTime`, `goodTillDate`, `ocaGroup`, `parentId` | no | | Passed to the IBKR order. |

Order types: `MKT`, `LMT`, `STP` and `STP_LMT` (also written `STP LMT` or `STPLMT`) are checked for their prices. Any other value is sent to IBKR as the raw `orderType` with whatever `lmtPrice` and `auxPrice` you gave.

```bash
curl -s -X POST "$IBKR/orders" \
  -H "Content-Type: application/json" \
  -d '{
    "assetClass": "stock",
    "symbol": "AAPL",
    "action": "BUY",
    "quantity": 10,
    "orderType": "LMT",
    "lmtPrice": 180.00
  }'

curl -s -X POST "$IBKR/orders" \
  -H "Content-Type: application/json" \
  -d '{
    "assetClass": "future",
    "symbol": "ES",
    "expiry": "202609",
    "exchange": "CME",
    "action": "BUY",
    "quantity": 1,
    "orderType": "LMT",
    "lmtPrice": 5500.00
  }'
```

The API qualifies the contract (a `404` if IBKR does not know it), places the order and returns the [Trade](#trade-object) right away. Read `orderStatus.status`: a rejection by IBKR shows up there, not as an HTTP error. There is no modify endpoint; cancel and place again.

### DELETE /orders/{orderId}

Cancels one open order: `{"status": "cancelling", "orderId": 12345}`, or `404` if it is not open.

### DELETE /orders

IBKR global cancel: every open order on the account, including ones placed elsewhere. Returns `{"status": "global_cancel_requested"}`.

### Trade object

```json
{
  "contract": {
    "conid": 265598,
    "symbol": "AAPL",
    "secType": "STK"
  },
  "order": {
    "orderId": 12,
    "permId": 123456789,
    "clientId": 1,
    "action": "BUY",
    "totalQuantity": 10.0,
    "orderType": "LMT",
    "lmtPrice": 180.0,
    "tif": "DAY",
    "transmit": true
  },
  "orderStatus": {
    "status": "Submitted",
    "filled": 0.0,
    "remaining": 10.0,
    "avgFillPrice": 0.0
  },
  "fills": [],
  "log": []
}
```

`order` also has `auxPrice`, `outsideRth`, `account`, `parentId`, `ocaGroup`, `goodAfterTime` and `goodTillDate`. `orderStatus` also has `permId`, `lastFillPrice`, `whyHeld` and `mktCapPrice`.

## History

### GET /history/executions

Executions IBKR reports for the current day. Optional filters: `account`, `clientId`, `secType`, `symbol`, `exchange`, `side`, `timeAfter` (`YYYYMMDD HH:MM:SS` UTC).

```json
{
  "fills": [
    {
      "contract": {
        "conid": 265598,
        "symbol": "AAPL"
      },
      "execution": {
        "execId": "0000e0d5.65b2c1a1.01.01",
        "side": "BOT",
        "shares": 10.0,
        "price": 180.0
      },
      "commissionReport": {
        "commission": 1.0,
        "currency": "USD"
      },
      "time": "2026-06-18T14:30:01+00:00"
    }
  ]
}
```

New fills are appended to the daily executions file on disk, deduplicated by `execId`.

### GET /history/completed_orders

Completed orders IBKR still holds. `apiOnly=true` limits the list to orders placed through the API. Returns `{"trades": [{"contract", "order", "orderStatus"}, ...]}` and appends new ones to the daily completed orders file.
