---
title: "Pacing and history"
description: "How the pacing gate keeps requests under IBKR's limits with 429 RATE_LIMIT_NEAR, and what the bars, snapshot, chain, metadata and execution stores write to disk."
nav_order: 7
---

# Pacing and history

IBKR rejects requests that break its pacing rules, and repeated violations can cost you API access. ibkr-httpapi puts a gate in front of every IBKR call that refuses the request itself, with `429 RATE_LIMIT_NEAR`, before IBKR would. It also writes most of what you fetch to disk under `data/history/`, so polling the API builds up your own market data archive over time.

The code is in [`ibkrapi/pacing.py`](https://github.com/psyb0t/ibkr-httpapi/blob/main/ibkrapi/pacing.py), [`cache_bars.py`](https://github.com/psyb0t/ibkr-httpapi/blob/main/ibkrapi/cache_bars.py), [`cache_meta.py`](https://github.com/psyb0t/ibkr-httpapi/blob/main/ibkrapi/cache_meta.py), [`historian.py`](https://github.com/psyb0t/ibkr-httpapi/blob/main/ibkrapi/historian.py) and [`exec_history.py`](https://github.com/psyb0t/ibkr-httpapi/blob/main/ibkrapi/exec_history.py).

## Pacing

Each IBKR call belongs to one of three tiers:

| Tier | Calls | Default window | Hard cap | Per contract per second | Concurrent |
| --- | --- | --- | --- | --- | --- |
| `historical` | historical bars, historical ticks, the wickworks step of `/rates/ta` | 600 s | 55 (IBKR's limit is 60) | 2 | 3 |
| `market_data` | snapshot ticks, contract details, chains, executions, completed orders, contract qualification for exercise | 60 s | 2200 | 5 | 10 |
| `orders` | qualify and place an order, place a combo, exercise, cancel, global cancel | 60 s | 275 | 2 | 3 |

Before a call goes out, the gate checks, in order:

1. the tier's sliding window: at `per_window_hard` calls it answers `429`; at `per_window_soft` it logs a `pacing_soft_cap` warning and lets the call through;
2. the per-contract window: at `per_contract_per_sec` calls on the same contract in the last second it answers `429` with `retry_after_sec: 1`;
3. a lock per contract, so two calls on the same contract run one after the other;
4. a semaphore per tier, so at most `concurrent` calls run at once.

The window counts calls that got through, in this process, since it started. A restart resets it. Several API containers on one gateway login each keep their own count, so the real total can exceed the limits. Tune the numbers under `pacing` in `config.yaml` ([reference](configuration.md#pacing)).

A `/rates/ta` call counts against `historical` twice: once for the bars and once for the wickworks request.

## What lands on disk

Everything goes under `history_cache.path`, `/app/data/history` in the container and `./data/history` on the host. Turn each store off with its `enabled` key.

```text
data/history/
├── stocks/AAPL_D1.csv                    bars, one file per symbol and bar size
├── options/AAPL/AAPL_20260619C00200000_H1.csv
├── snapshots/stocks/AAPL.csv             one row per /tick call
├── snapshots/options/AAPL/AAPL_20260619C00200000.csv
├── chains/AAPL/20260619.csv              one row per strike per /chain call
├── meta/<scope>/<key>.json               contract details, futures lists, chains
└── exec/
    ├── executions/2026-06-18.jsonl
    └── completed_orders/2026-06-18.jsonl
```

File names keep only letters, digits, `.`, `_` and `-`; anything else becomes `_`.

### Bars

Every `/rates` and `/rates/ta` response is merged into a CSV per asset class, symbol and bar size:

```text
time,open,high,low,close,tickVolume
1718668800,196.1,198.4,195.7,197.9,51234567
```

`time` is Unix seconds. New bars are merged by time, the file stays sorted, nothing is ever deleted. The newest bar is dropped from the file while its period is still open, unless `history_cache.persist_open_bar` is `true`. Bar size names follow the MT5 style used by wickworks: `1d` becomes `D1`, `1h` becomes `H1`, `15m` becomes `M15`.

This store is an archive, not a read cache. Every `/rates` request still asks IBKR for the full window and returns what IBKR sent; the file only grows from it. A write error in this store fails the request, unlike the stores below.

Known problem: the store does arithmetic on the `time` of freshly fetched bars as if it were Unix seconds, but those bars carry ISO time strings, so any `/rates` or `/rates/ta` call that gets at least one bar back fails with `500` and `Internal error: TypeError`. Until that is fixed, set `history_cache.enabled: false`. See [troubleshooting](troubleshooting.md#rates-returns-500-with-internal-error-typeerror).

### Tick snapshots

Each `/tick` call appends one row:

```text
time,bid,ask,last,bidSize,askSize,lastSize,volume,iv,delta,gamma,theta,vega,underlyingPrice
```

The Greeks columns come from `modelGreeks` and stay empty for anything that is not an option or when IBKR sent no Greeks. Options are filed under their underlying with a name built from the symbol, expiry, right and strike times 1000.

### Option chains

Each `/options/{symbol}/chain` call appends one row per expiry and strike to `chains/<UNDERLYING>/<EXPIRY>.csv`:

```text
time,exchange,tradingClass,multiplier,strike
```

A chain with 40 expiries and 200 strikes writes 8000 rows per call. Even a call served from the metadata cache writes them.

### Metadata cache

This one does serve reads. Contract details, futures contract lists and option chain strike lists are stored as JSON with a timestamp and a TTL, and a request within the TTL is answered from disk without touching IBKR.

| Scope | Used by | Default TTL |
| --- | --- | --- |
| `contract_details` | `GET /<class>/{symbol}`, `/futures/{symbol}/continuous` | 7 days |
| `futures_expiries` | `/futures/{symbol}/contracts` | 1 day |
| `chain_strike_list` | `/options/{symbol}/chain` | 1 day |

`refresh=true` skips the stored copy, fetches again and rewrites the file. Concurrent misses for the same key wait for one fetch.

### Executions and completed orders

`/history/executions` and `/history/completed_orders` always ask IBKR, then append records they have not seen to a JSONL file per day (UTC): executions are deduplicated by `execId`, completed orders by `permId` and `orderId`. IBKR only reports the current day's executions, so this file is the only lasting record you get through the API.

### Failure behaviour

The snapshot, chain and execution writers log a warning and let the request succeed when a write fails. The bars store does not. The metadata cache treats an unreadable file as a miss.

## Market data licensing

IBKR's market data terms restrict redistribution. Using the archive for your own backtests, research and models is the intended use. Publishing or selling raw bars from it likely breaks the exchange and OPRA redistribution licenses attached to your subscriptions.
