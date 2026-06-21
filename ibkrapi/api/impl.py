"""Implementation module for the spec-first FastAPI server.

The generated routers in `ibkrapi/api/_generated/routers/` are thin
delegators — every route handler is one line:

    async def <op>(...): return await impl.<op>(...)

This file owns ALL business logic. It wires generated function
signatures (whose names come from the OpenAPI `operationId`s) to the
existing `marketdata` / `contracts` / `ibclient` helpers.

Every function name MUST match the snake-cased `operationId` from
`api/v1.yaml`. The `make gen-api-check` target verifies that every
generated router function resolves to one in this module.

v0.2.0 added preemptive pacing + transparent disk caching for every
endpoint that returns historical/quasi-static data — see `pacing`,
`cache_bars`, `cache_meta`, `historian`, `exec_history` modules.
Cache writes are best-effort and never block the caller's response.
"""

from __future__ import annotations

from datetime import UTC, datetime

from ib_async import (
    ContFuture,
    Contract,
    ExecutionFilter,
    LimitOrder,
    MarketOrder,
    Order,
    StopLimitOrder,
    StopOrder,
)

from ibkrapi import (
    cache_bars,
    cache_meta,
    exec_history,
    historian,
    marketdata,
    pacing,
)
from ibkrapi import (
    contracts as contract_factories,
)
from ibkrapi.api._generated.models import (
    AccountsList,
    AccountSummary,
    BarsResponse,
    CancelAllResponse,
    CancelOrderResponse,
    ComboOrderRequest,
    CompletedOrdersResponse,
    ContractDetailsList,
    ExecutionsResponse,
    ExerciseRequest,
    ExerciseResponse,
    OptionChain,
    OptionChainEntry,
    OrderRequest,
    PingResponse,
    PositionsList,
    RatesTARequest,
    RatesTAResponse,
    Ticker,
    TicksResponse,
    Trade,
    TradesList,
)
from ibkrapi.errors import CODE_BAD_REQUEST, CODE_NOT_FOUND, APIError
from ibkrapi.ibclient import get_ib
from ibkrapi.logger import log
from ibkrapi.routers._constants import (
    ASSET_CFD,
    ASSET_CRYPTO,
    ASSET_FOREX_ALIASES,
    ASSET_FUTURE_ALIASES,
    ASSET_OPTION_ALIASES,
    ASSET_STOCK_ALIASES,
    COMBO_VALID_ORDER_TYPES,
    ORDER_TYPE_LMT,
    ORDER_TYPE_MKT,
    ORDER_TYPE_STP,
    ORDER_TYPE_STP_LMT_ALIASES,
    SECTYPE_CASH,
    SECTYPE_CFD,
    SECTYPE_CRYPTO,
    SECTYPE_FUT,
    SECTYPE_OPT,
    SECTYPE_STK,
    VALID_ACTIONS,
)
from ibkrapi.serialize import (
    _coerce,
    contract_details_dict,
    contract_dict,
    position_dict,
    trade_dict,
)

# Asset-class → contract-factory mapping used by `place_order`.
_ORDER_ASSET_BUILDERS = {
    "stock": contract_factories.stock,
    "stk": contract_factories.stock,
    "option": contract_factories.option,
    "opt": contract_factories.option,
    "future": contract_factories.future,
    "fut": contract_factories.future,
    "cfd": contract_factories.cfd,
    "forex": contract_factories.forex,
    "cash": contract_factories.forex,
    "crypto": contract_factories.crypto,
}


# ─── Pacing + cache helpers ─────────────────────────────────────────


async def _cached_bars(
    contract,
    *,
    asset_class: str,
    symbol: str,
    underlying: str | None = None,
    duration: str,
    bar_size: str | None,
    end_dt: str | None,
    what: str | None,
    rth: bool,
    refresh: bool = False,
) -> list[dict]:
    """Historical bars wrapped with pacing + transparent disk cache.

    Cache key = (asset_class, symbol, bar_size). Bars merged + persisted
    on every call so the goldmine grows over time. Pacing tier =
    `historical` (gated against IBKR's 60/10min cap). `refresh=True`
    bypasses the cache read but still writes the fresh result back."""
    key = pacing.contract_key(contract)

    async def _fetch() -> list[dict]:
        async with pacing.guard("historical", key):
            return await marketdata.historical_bars(
                contract,
                duration=duration,
                bar_size=bar_size,
                end_datetime=end_dt,
                what_to_show=what,
                use_rth=rth,
            )

    bars, _ = await cache_bars.get_or_fetch(
        asset_class=asset_class,
        symbol=symbol,
        bar_size=bar_size,
        underlying=underlying,
        requested_bars=None,
        fetch_full=_fetch,
        refresh=refresh,
    )
    return bars


async def _paced_ticks(
    contract,
    *,
    start_dt: str | None,
    end_dt: str | None,
    n: int,
    what: str | None,
    rth: bool,
) -> list[dict]:
    key = pacing.contract_key(contract)
    async with pacing.guard("historical", key):
        return await marketdata.historical_ticks(
            contract,
            start_datetime=start_dt,
            end_datetime=end_dt,
            number_of_ticks=n,
            what_to_show=what,
            use_rth=rth,
        )


async def _gated_tick(
    contract,
    *,
    asset_class: str,
    symbol: str,
    underlying: str | None = None,
) -> dict:
    """Snapshot tick under market_data pacing + historian piggyback."""
    key = pacing.contract_key(contract)
    async with pacing.guard("market_data", key):
        td = await marketdata.snapshot_tick(contract)
    await historian.record_tick(asset_class, symbol, td, underlying=underlying)
    return td


async def _cached_details(
    contract, *, scope: str = "contract_details", refresh: bool = False
) -> list[dict]:
    """Long-TTL JSON cache for contract metadata."""
    key = pacing.contract_key(contract)

    async def _fetch() -> list[dict]:
        async with pacing.guard("market_data", key):
            return await marketdata.contract_details(contract)

    details, _ = await cache_meta.get_or_fetch(scope, key, _fetch, refresh=refresh)
    return details


async def _paced_rates_ta(
    contract,
    body: RatesTARequest,
    *,
    asset_class: str,
    symbol: str,
    underlying: str | None = None,
    default_what: str | None = None,
    refresh: bool = False,
) -> dict:
    """Bars-via-cache + wickworks TA enrichment.

    v0.3.0 composes `cache_bars.get_or_fetch` with the standalone
    `marketdata.ta_enrich` so /rates/ta hits the same disk cache the
    plain /rates endpoint does. Bars grow the goldmine on every TA
    request too."""
    bars = await _cached_bars(
        contract,
        asset_class=asset_class,
        symbol=symbol,
        underlying=underlying,
        duration=body.duration,
        bar_size=body.barSize,
        end_dt=body.endDateTime,
        what=body.whatToShow or default_what,
        rth=bool(body.useRTH),
        refresh=refresh,
    )
    # ta_enrich is sync (it does a blocking urllib POST to wickworks
    # under the historical pacing tier — keep both phases gated together
    # for one-call accounting).
    key = pacing.contract_key(contract)
    async with pacing.guard("historical", key):
        return marketdata.ta_enrich(
            contract, bars, indicators=body.indicators or {}, recent_bars=body.recentBars
        )


# ─── system ────────────────────────────────────────────────────────


async def get_ping() -> PingResponse:
    ib = await get_ib()
    connected = ib.isConnected()
    stats = ib.client.connectionStats() if connected else None
    return PingResponse(
        status="ok",
        connected=connected,
        serverVersion=ib.client.serverVersion() if connected else None,
        startTime=(
            datetime.fromtimestamp(stats.startTime, tz=UTC).isoformat()
            if stats and stats.startTime
            else None
        ),
        uptimeSeconds=stats.duration if stats else None,
        msgsSent=stats.numMsgSent if stats else None,
        msgsRecv=stats.numMsgRecv if stats else None,
    )


async def list_accounts() -> AccountsList:
    ib = await get_ib()
    return AccountsList(accounts=list(ib.managedAccounts() or []))


async def get_account_summary(account: str | None) -> AccountSummary:
    ib = await get_ib()
    rows = await ib.accountSummaryAsync(account or "")
    if not rows:
        raise APIError(404, "No account summary returned", code=CODE_NOT_FOUND)
    by_account: dict[str, dict] = {}
    for row in rows:
        slot = by_account.setdefault(row.account, {})
        slot[row.tag] = {
            "value": row.value,
            "currency": row.currency,
            "modelCode": row.modelCode,
        }
    return AccountSummary(accounts=by_account)


async def get_account_values(account: str | None) -> AccountSummary:
    ib = await get_ib()
    values = ib.accountValues(account or "")
    by_account: dict[str, dict] = {}
    for v in values:
        slot = by_account.setdefault(v.account, {})
        slot[v.tag] = {"value": v.value, "currency": v.currency, "modelCode": v.modelCode}
    return AccountSummary(accounts=by_account)


async def list_positions(account: str | None) -> PositionsList:
    ib = await get_ib()
    all_positions = ib.positions(account or "")
    return PositionsList(positions=[position_dict(p) for p in all_positions])


# ─── stocks ────────────────────────────────────────────────────────


def _stock(symbol, exchange, currency, primary_exchange):
    return contract_factories.stock(
        symbol,
        exchange=exchange,
        currency=currency,
        primary_exchange=primary_exchange,
    )


async def get_stock_contract(
    symbol, exchange, currency, primary_exchange, refresh=False
) -> ContractDetailsList:
    contract = _stock(symbol, exchange, currency, primary_exchange)
    return ContractDetailsList(contracts=await _cached_details(contract, refresh=refresh))


async def get_stock_tick(symbol, exchange, currency, primary_exchange) -> Ticker:
    contract = _stock(symbol, exchange, currency, primary_exchange)
    return Ticker(**await _gated_tick(contract, asset_class="stocks", symbol=symbol))


async def get_stock_rates(
    symbol,
    duration,
    bar_size,
    end_date_time,
    what_to_show,
    use_r_t_h,
    exchange,
    currency,
    primary_exchange,
    refresh=False,
) -> BarsResponse:
    contract = _stock(symbol, exchange, currency, primary_exchange)
    bars = await _cached_bars(
        contract,
        asset_class="stocks",
        symbol=symbol,
        duration=duration,
        bar_size=bar_size,
        end_dt=end_date_time,
        what=what_to_show,
        rth=bool(use_r_t_h),
        refresh=refresh,
    )
    return BarsResponse(symbol=symbol, secType=SECTYPE_STK, bars=bars)


async def get_stock_ticks(
    symbol,
    start_date_time,
    end_date_time,
    number_of_ticks,
    what_to_show,
    use_r_t_h,
    exchange,
    currency,
    primary_exchange,
    refresh=False,
) -> TicksResponse:
    contract = _stock(symbol, exchange, currency, primary_exchange)
    ticks = await _paced_ticks(
        contract,
        start_dt=start_date_time,
        end_dt=end_date_time,
        n=number_of_ticks,
        what=what_to_show,
        rth=bool(use_r_t_h),
    )
    return TicksResponse(symbol=symbol, secType=SECTYPE_STK, ticks=ticks)


async def get_stock_rates_t_a(
    symbol,
    exchange,
    currency,
    primary_exchange,
    body: RatesTARequest,
    refresh=False,
) -> RatesTAResponse:
    contract = _stock(symbol, exchange, currency, primary_exchange)
    return RatesTAResponse(
        **await _paced_rates_ta(
            contract, body, asset_class="stocks", symbol=symbol, refresh=refresh
        )
    )


# ─── options ───────────────────────────────────────────────────────


def _option(symbol, expiry, strike, right, exchange, currency, multiplier, trading_class):
    return contract_factories.option(
        symbol,
        expiry=expiry,
        strike=strike,
        right=right,
        exchange=exchange,
        currency=currency,
        multiplier=multiplier,
        trading_class=trading_class,
    )


async def get_option_chain(
    symbol,
    underlying_sec_type,
    fut_fop_exchange,
    underlying_con_id,
    refresh=False,
) -> OptionChain:
    ib = await get_ib()
    if underlying_con_id is None:
        underlying = (
            contract_factories.stock(symbol) if underlying_sec_type == SECTYPE_STK else None
        )
        if underlying is None:
            raise APIError(
                400,
                "Provide underlyingConId for non-STK underlyings",
                code=CODE_BAD_REQUEST,
            )
        async with pacing.guard("market_data", f"qualify:{symbol}"):
            qualified = await ib.qualifyContractsAsync(underlying)
        first = qualified[0] if qualified else None
        if not isinstance(first, Contract):
            raise APIError(
                404, "Underlying not found", code=CODE_NOT_FOUND, details={"symbol": symbol}
            )
        underlying_con_id = first.conId

    cache_key = f"{symbol}:{underlying_sec_type}:{fut_fop_exchange or '*'}:{underlying_con_id}"

    async def _fetch_chain() -> list[dict]:
        async with pacing.guard("market_data", f"chain:{cache_key}"):
            chains = await ib.reqSecDefOptParamsAsync(
                underlyingSymbol=symbol,
                futFopExchange=fut_fop_exchange or "",
                underlyingSecType=underlying_sec_type,
                underlyingConId=underlying_con_id,
            )
        return [
            {
                "exchange": c.exchange,
                "tradingClass": c.tradingClass,
                "multiplier": c.multiplier,
                "expirations": sorted(c.expirations),
                "strikes": sorted(c.strikes),
            }
            for c in (chains or [])
        ]

    entries, _ = await cache_meta.get_or_fetch(
        "chain_strike_list", cache_key, _fetch_chain, refresh=refresh
    )
    # Piggyback: append a snapshot row per strike to the chain history.
    await historian.record_chain(symbol, entries)
    return OptionChain(
        symbol=symbol,
        underlyingConId=underlying_con_id,
        chains=[OptionChainEntry(**e) for e in entries],
    )


async def get_option_contract(
    symbol,
    expiry,
    strike,
    right,
    exchange,
    currency,
    multiplier,
    trading_class,
    refresh=False,
) -> ContractDetailsList:
    contract = _option(symbol, expiry, strike, right, exchange, currency, multiplier, trading_class)
    return ContractDetailsList(contracts=await _cached_details(contract, refresh=refresh))


async def get_option_tick(
    symbol, expiry, strike, right, exchange, currency, multiplier, trading_class
) -> Ticker:
    contract = _option(symbol, expiry, strike, right, exchange, currency, multiplier, trading_class)
    # Per-contract snapshot history under data/history/snapshots/options/<UNDERLYING>/<OCC>.csv
    occ = f"{symbol}_{expiry}{(right or '').upper()}{round(float(strike) * 1000):08d}"
    return Ticker(
        **await _gated_tick(contract, asset_class="options", symbol=occ, underlying=symbol)
    )


async def get_option_rates(
    symbol,
    expiry,
    strike,
    right,
    duration,
    bar_size,
    end_date_time,
    what_to_show,
    use_r_t_h,
    exchange,
    currency,
    multiplier,
    trading_class,
    refresh=False,
) -> BarsResponse:
    contract = _option(symbol, expiry, strike, right, exchange, currency, multiplier, trading_class)
    occ = f"{symbol}_{expiry}{(right or '').upper()}{round(float(strike) * 1000):08d}"
    bars = await _cached_bars(
        contract,
        asset_class="options",
        symbol=occ,
        underlying=symbol,
        duration=duration,
        bar_size=bar_size,
        end_dt=end_date_time,
        what=what_to_show,
        rth=bool(use_r_t_h),
        refresh=refresh,
    )
    return BarsResponse(
        symbol=symbol, secType=SECTYPE_OPT, expiry=expiry, strike=strike, right=right, bars=bars
    )


async def get_option_rates_t_a(
    symbol,
    expiry,
    strike,
    right,
    exchange,
    currency,
    multiplier,
    trading_class,
    body: RatesTARequest,
    refresh=False,
) -> RatesTAResponse:
    contract = _option(symbol, expiry, strike, right, exchange, currency, multiplier, trading_class)
    occ = f"{symbol}_{expiry}{(right or '').upper()}{round(float(strike) * 1000):08d}"
    return RatesTAResponse(
        **await _paced_rates_ta(
            contract, body, asset_class="options", symbol=occ, underlying=symbol, refresh=refresh
        )
    )


async def place_option_combo(body: ComboOrderRequest) -> Trade:
    ib = await get_ib()
    bag = contract_factories.combo(
        body.symbol,
        legs=[leg.model_dump() for leg in body.legs],
        exchange=body.exchange or "",
        currency=body.currency or "USD",
    )
    order_type = (body.orderType or "").upper()
    if order_type not in COMBO_VALID_ORDER_TYPES:
        raise APIError(
            400,
            f"Unsupported orderType: {body.orderType}",
            code=CODE_BAD_REQUEST,
            details={"accepted": list(COMBO_VALID_ORDER_TYPES)},
        )
    if order_type == ORDER_TYPE_MKT:
        order = MarketOrder((body.action or "").upper(), body.quantity, tif=body.tif)
    else:  # LMT — guard above ensured one of MKT/LMT
        if body.lmtPrice is None:
            raise APIError(400, "lmtPrice required for LMT", code=CODE_BAD_REQUEST)
        order = LimitOrder((body.action or "").upper(), body.quantity, body.lmtPrice, tif=body.tif)
    if body.account:
        order.account = body.account
    log.info("combo_order_submit", symbol=body.symbol, action=body.action, qty=body.quantity)
    async with pacing.guard("orders", f"OPT:{body.symbol}"):
        trade = ib.placeOrder(bag, order)
    return Trade(**trade_dict(trade))


async def exercise_option(body: ExerciseRequest) -> ExerciseResponse:
    ib = await get_ib()
    action_map = {"EXERCISE": 1, "LAPSE": 2}
    action_code = action_map.get((body.action or "").upper())
    if action_code is None:
        raise APIError(
            400,
            "action must be EXERCISE or LAPSE",
            code=CODE_BAD_REQUEST,
            details={"accepted": list(action_map)},
        )
    contract = contract_factories.by_conid(body.conid)
    async with pacing.guard("market_data", f"conid:{body.conid}"):
        qualified = await ib.qualifyContractsAsync(contract)
    qualified_contract = qualified[0] if qualified else None
    if not isinstance(qualified_contract, Contract):
        raise APIError(
            404,
            f"conid {body.conid} not qualifyable",
            code=CODE_NOT_FOUND,
            details={"conid": body.conid},
        )
    log.info(
        "option_exercise_submit",
        conid=body.conid,
        action=body.action,
        qty=body.quantity,
        account=body.account,
    )
    async with pacing.guard("orders", f"exercise:{body.conid}"):
        ib.exerciseOptions(
            qualified_contract,
            exerciseAction=action_code,
            exerciseQuantity=body.quantity,
            account=body.account,
            override=1 if body.override else 0,
        )
    return ExerciseResponse(
        status="submitted",
        contract=contract_dict(qualified_contract),
        action=body.action,
    )


# ─── futures ───────────────────────────────────────────────────────


def _future(symbol, expiry, exchange, currency, multiplier, trading_class, include_expired=False):
    return contract_factories.future(
        symbol,
        expiry=expiry,
        exchange=exchange,
        currency=currency,
        multiplier=multiplier,
        trading_class=trading_class,
        include_expired=include_expired,
    )


async def get_continuous_future(symbol, exchange, currency, refresh=False) -> ContractDetailsList:
    contract = ContFuture(symbol=symbol, exchange=exchange, currency=currency or "USD")
    ib = await get_ib()

    async def _fetch() -> list[dict]:
        async with pacing.guard("market_data", f"contfut:{symbol}:{exchange}"):
            details = await ib.reqContractDetailsAsync(contract)
        return [contract_details_dict(d) for d in (details or [])]

    cached, _ = await cache_meta.get_or_fetch(
        "contract_details",
        f"CONTFUT:{symbol}:{exchange}:{currency or 'USD'}",
        _fetch,
        refresh=refresh,
    )
    return ContractDetailsList(contracts=cached)


async def list_future_contracts(
    symbol, exchange, currency, include_expired, refresh=False
) -> ContractDetailsList:
    contract = _future(symbol, "", exchange, currency, None, None, include_expired=include_expired)

    async def _fetch() -> list[dict]:
        async with pacing.guard("market_data", f"futlist:{symbol}:{exchange}"):
            return await marketdata.contract_details(contract)

    cached, _ = await cache_meta.get_or_fetch(
        "futures_expiries",
        f"FUT:{symbol}:{exchange}:{currency or '*'}:{include_expired}",
        _fetch,
        refresh=refresh,
    )
    return ContractDetailsList(contracts=cached)


async def get_future_contract(
    symbol,
    expiry,
    exchange,
    currency,
    multiplier,
    trading_class,
    refresh=False,
) -> ContractDetailsList:
    contract = _future(symbol, expiry, exchange, currency, multiplier, trading_class)
    return ContractDetailsList(contracts=await _cached_details(contract, refresh=refresh))


async def get_future_tick(symbol, expiry, exchange, currency, multiplier, trading_class) -> Ticker:
    contract = _future(symbol, expiry, exchange, currency, multiplier, trading_class)
    return Ticker(
        **await _gated_tick(
            contract, asset_class="futures", symbol=f"{symbol}_{expiry}" if expiry else symbol
        )
    )


async def get_future_rates(
    symbol,
    duration,
    expiry,
    exchange,
    bar_size,
    end_date_time,
    what_to_show,
    use_r_t_h,
    currency,
    multiplier,
    trading_class,
    refresh=False,
) -> BarsResponse:
    contract = _future(symbol, expiry, exchange, currency, multiplier, trading_class)
    bars = await _cached_bars(
        contract,
        asset_class="futures",
        symbol=f"{symbol}_{expiry}" if expiry else symbol,
        duration=duration,
        bar_size=bar_size,
        end_dt=end_date_time,
        what=what_to_show,
        rth=bool(use_r_t_h),
        refresh=refresh,
    )
    return BarsResponse(symbol=symbol, secType=SECTYPE_FUT, expiry=expiry, bars=bars)


async def get_future_rates_t_a(
    symbol,
    expiry,
    exchange,
    currency,
    multiplier,
    trading_class,
    body: RatesTARequest,
    refresh=False,
) -> RatesTAResponse:
    contract = _future(symbol, expiry, exchange, currency, multiplier, trading_class)
    return RatesTAResponse(
        **await _paced_rates_ta(
            contract,
            body,
            asset_class="futures",
            symbol=f"{symbol}_{expiry}" if expiry else symbol,
            refresh=refresh,
        )
    )


# ─── cfd ───────────────────────────────────────────────────────────


def _cfd(symbol, exchange, currency):
    return contract_factories.cfd(symbol, exchange=exchange, currency=currency)


async def get_c_f_d_contract(symbol, exchange, currency, refresh=False) -> ContractDetailsList:
    return ContractDetailsList(
        contracts=await _cached_details(_cfd(symbol, exchange, currency), refresh=refresh)
    )


async def get_c_f_d_tick(symbol, exchange, currency) -> Ticker:
    return Ticker(
        **await _gated_tick(_cfd(symbol, exchange, currency), asset_class="cfd", symbol=symbol)
    )


async def get_c_f_d_rates(
    symbol,
    duration,
    bar_size,
    end_date_time,
    what_to_show,
    use_r_t_h,
    exchange,
    currency,
    refresh=False,
) -> BarsResponse:
    bars = await _cached_bars(
        _cfd(symbol, exchange, currency),
        asset_class="cfd",
        symbol=symbol,
        duration=duration,
        bar_size=bar_size,
        end_dt=end_date_time,
        what=what_to_show,
        rth=bool(use_r_t_h),
        refresh=refresh,
    )
    return BarsResponse(symbol=symbol, secType=SECTYPE_CFD, bars=bars)


async def get_c_f_d_rates_t_a(
    symbol, exchange, currency, body: RatesTARequest, refresh=False
) -> RatesTAResponse:
    return RatesTAResponse(
        **await _paced_rates_ta(
            _cfd(symbol, exchange, currency),
            body,
            asset_class="cfd",
            symbol=symbol,
            refresh=refresh,
        )
    )


# ─── forex ─────────────────────────────────────────────────────────


def _forex(pair, exchange):
    return contract_factories.forex(pair, exchange=exchange)


async def get_forex_contract(pair, exchange, refresh=False) -> ContractDetailsList:
    return ContractDetailsList(
        contracts=await _cached_details(_forex(pair, exchange), refresh=refresh)
    )


async def get_forex_tick(pair, exchange) -> Ticker:
    return Ticker(**await _gated_tick(_forex(pair, exchange), asset_class="forex", symbol=pair))


async def get_forex_rates(
    pair,
    duration,
    bar_size,
    end_date_time,
    what_to_show,
    use_r_t_h,
    exchange,
    refresh=False,
) -> BarsResponse:
    bars = await _cached_bars(
        _forex(pair, exchange),
        asset_class="forex",
        symbol=pair,
        duration=duration,
        bar_size=bar_size,
        end_dt=end_date_time,
        what=what_to_show,
        rth=bool(use_r_t_h),
        refresh=refresh,
    )
    return BarsResponse(pair=pair, secType=SECTYPE_CASH, bars=bars)


async def get_forex_rates_t_a(
    pair, exchange, body: RatesTARequest, refresh=False
) -> RatesTAResponse:
    return RatesTAResponse(
        **await _paced_rates_ta(
            _forex(pair, exchange),
            body,
            asset_class="forex",
            symbol=pair,
            default_what="MIDPOINT",
            refresh=refresh,
        )
    )


# ─── crypto ────────────────────────────────────────────────────────


def _crypto(symbol, exchange, currency):
    return contract_factories.crypto(symbol, exchange=exchange, currency=currency)


async def get_crypto_contract(symbol, exchange, currency, refresh=False) -> ContractDetailsList:
    return ContractDetailsList(
        contracts=await _cached_details(_crypto(symbol, exchange, currency), refresh=refresh)
    )


async def get_crypto_tick(symbol, exchange, currency) -> Ticker:
    return Ticker(
        **await _gated_tick(
            _crypto(symbol, exchange, currency), asset_class="crypto", symbol=symbol
        )
    )


async def get_crypto_rates(
    symbol,
    duration,
    bar_size,
    end_date_time,
    what_to_show,
    use_r_t_h,
    exchange,
    currency,
    refresh=False,
) -> BarsResponse:
    bars = await _cached_bars(
        _crypto(symbol, exchange, currency),
        asset_class="crypto",
        symbol=symbol,
        duration=duration,
        bar_size=bar_size,
        end_dt=end_date_time,
        what=what_to_show,
        rth=bool(use_r_t_h),
        refresh=refresh,
    )
    return BarsResponse(symbol=symbol, secType=SECTYPE_CRYPTO, bars=bars)


async def get_crypto_rates_t_a(
    symbol, exchange, currency, body: RatesTARequest, refresh=False
) -> RatesTAResponse:
    return RatesTAResponse(
        **await _paced_rates_ta(
            _crypto(symbol, exchange, currency),
            body,
            asset_class="crypto",
            symbol=symbol,
            refresh=refresh,
        )
    )


# ─── orders ────────────────────────────────────────────────────────


def _build_contract_from_request(req: OrderRequest):
    if req.conid is not None and req.conid > 0:
        return contract_factories.by_conid(req.conid)
    asset = req.assetClass.lower()
    builder = _ORDER_ASSET_BUILDERS.get(asset)
    if builder is None:
        raise APIError(
            400,
            f"Unknown assetClass: {req.assetClass}",
            code=CODE_BAD_REQUEST,
            details={"accepted": sorted(_ORDER_ASSET_BUILDERS)},
        )
    if asset in ASSET_OPTION_ALIASES:
        for name in ("expiry", "strike", "right"):
            if getattr(req, name) in (None, ""):
                raise APIError(400, f"Option order requires {name}", code=CODE_BAD_REQUEST)
        return builder(
            req.symbol,
            expiry=req.expiry,
            strike=req.strike,
            right=req.right,
            exchange=req.exchange,
            currency=req.currency,
            multiplier=req.multiplier,
            trading_class=req.tradingClass,
        )
    if asset in ASSET_FUTURE_ALIASES:
        if not req.expiry:
            raise APIError(400, "Future order requires expiry", code=CODE_BAD_REQUEST)
        if not req.exchange:
            raise APIError(400, "Future order requires exchange", code=CODE_BAD_REQUEST)
        return builder(
            req.symbol,
            expiry=req.expiry,
            exchange=req.exchange,
            currency=req.currency,
            multiplier=req.multiplier,
            trading_class=req.tradingClass,
        )
    if asset in ASSET_STOCK_ALIASES:
        return builder(
            req.symbol,
            exchange=req.exchange,
            currency=req.currency,
            primary_exchange=req.primaryExchange,
        )
    if asset == ASSET_CFD:
        return builder(req.symbol, exchange=req.exchange, currency=req.currency)
    if asset in ASSET_FOREX_ALIASES:
        return builder(req.symbol, exchange=req.exchange)
    if asset == ASSET_CRYPTO:
        return builder(req.symbol, exchange=req.exchange, currency=req.currency)
    raise APIError(400, f"Builder for {req.assetClass} not wired", code=CODE_BAD_REQUEST)


def _build_order(req: OrderRequest):
    action = req.action.upper()
    if action not in VALID_ACTIONS:
        raise APIError(400, f"action must be one of {VALID_ACTIONS}", code=CODE_BAD_REQUEST)
    qty = req.quantity
    ot = req.orderType.upper()
    if ot == ORDER_TYPE_MKT:
        order = MarketOrder(action, qty, tif=req.tif)
    elif ot == ORDER_TYPE_LMT:
        if req.lmtPrice is None:
            raise APIError(400, "lmtPrice required for LMT", code=CODE_BAD_REQUEST)
        order = LimitOrder(action, qty, req.lmtPrice, tif=req.tif)
    elif ot == ORDER_TYPE_STP:
        if req.auxPrice is None:
            raise APIError(400, "auxPrice (stop price) required for STP", code=CODE_BAD_REQUEST)
        order = StopOrder(action, qty, req.auxPrice, tif=req.tif)
    elif ot in ORDER_TYPE_STP_LMT_ALIASES:
        if req.lmtPrice is None or req.auxPrice is None:
            raise APIError(
                400,
                "STP_LMT requires both lmtPrice and auxPrice",
                code=CODE_BAD_REQUEST,
            )
        order = StopLimitOrder(action, qty, req.lmtPrice, req.auxPrice, tif=req.tif)
    else:
        # Unknown order type — pass through as raw Order. Caller's risk.
        order = Order(action=action, totalQuantity=qty, orderType=ot, tif=req.tif)
        if req.lmtPrice is not None:
            order.lmtPrice = req.lmtPrice
        if req.auxPrice is not None:
            order.auxPrice = req.auxPrice
    order.outsideRth = req.outsideRth
    order.transmit = req.transmit
    if req.account:
        order.account = req.account
    if req.goodAfterTime:
        order.goodAfterTime = req.goodAfterTime
    if req.goodTillDate:
        order.goodTillDate = req.goodTillDate
    if req.ocaGroup:
        order.ocaGroup = req.ocaGroup
    if req.parentId is not None:
        order.parentId = req.parentId
    return order


async def list_orders() -> TradesList:
    ib = await get_ib()
    return TradesList(trades=[trade_dict(t) for t in ib.openTrades()])


async def place_order(body: OrderRequest) -> Trade:
    ib = await get_ib()
    contract = _build_contract_from_request(body)
    key = f"{body.assetClass}:{body.symbol}"
    async with pacing.guard("orders", key):
        qualified = await ib.qualifyContractsAsync(contract)
    first = qualified[0] if qualified else None
    if not isinstance(first, Contract):
        raise APIError(
            404,
            "Contract not qualifyable",
            code=CODE_NOT_FOUND,
            details={"assetClass": body.assetClass, "symbol": body.symbol},
        )
    order = _build_order(body)
    log.info(
        "order_submit",
        assetClass=body.assetClass,
        symbol=body.symbol,
        action=body.action,
        qty=body.quantity,
        orderType=body.orderType,
    )
    async with pacing.guard("orders", key):
        trade = ib.placeOrder(first, order)
    return Trade(**trade_dict(trade))


async def get_order(order_id: int) -> Trade:
    ib = await get_ib()
    for trade in ib.openTrades():
        if trade.order.orderId == order_id:
            return Trade(**trade_dict(trade))
    raise APIError(
        404, "Order not found in open trades", code=CODE_NOT_FOUND, details={"orderId": order_id}
    )


async def cancel_order(order_id: int) -> CancelOrderResponse:
    ib = await get_ib()
    for trade in ib.openTrades():
        if trade.order.orderId == order_id:
            log.info("order_cancel", orderId=order_id)
            async with pacing.guard("orders", f"cancel:{order_id}"):
                ib.cancelOrder(trade.order)
            return CancelOrderResponse(status="cancelling", orderId=order_id)
    raise APIError(404, "Order not open", code=CODE_NOT_FOUND, details={"orderId": order_id})


async def cancel_all_orders() -> CancelAllResponse:
    ib = await get_ib()
    log.warning("global_cancel_requested")
    async with pacing.guard("orders", "global_cancel"):
        ib.reqGlobalCancel()
    return CancelAllResponse(status="global_cancel_requested")


# ─── history ───────────────────────────────────────────────────────


async def get_executions(
    account,
    client_id,
    sec_type,
    symbol,
    exchange,
    side,
    time_after,
    refresh=False,
) -> ExecutionsResponse:
    ib = await get_ib()
    async with pacing.guard("market_data", f"executions:{account or '*'}"):
        fills = await ib.reqExecutionsAsync(
            ExecutionFilter(
                clientId=client_id or 0,
                acctCode=account or "",
                time=time_after or "",
                symbol=symbol or "",
                secType=sec_type or "",
                exchange=exchange or "",
                side=side or "",
            )
        )
    fill_dicts = [
        {
            "contract": contract_dict(f.contract),
            "execution": _coerce(f.execution),
            "commissionReport": (_coerce(f.commissionReport) if f.commissionReport else None),
            "time": (f.time.isoformat() if isinstance(f.time, datetime) else str(f.time)),
        }
        for f in (fills or [])
    ]
    # Append-only ledger — grow the goldmine on every call.
    await exec_history.record_executions(fill_dicts)
    return ExecutionsResponse(fills=fill_dicts)


async def get_completed_orders(api_only: bool, refresh=False) -> CompletedOrdersResponse:
    ib = await get_ib()
    async with pacing.guard("market_data", f"completed:{api_only}"):
        completed = await ib.reqCompletedOrdersAsync(apiOnly=api_only)
    trade_dicts = [
        {
            "contract": contract_dict(t.contract),
            "order": _coerce(t.order),
            "orderStatus": _coerce(t.orderStatus),
        }
        for t in (completed or [])
    ]
    await exec_history.record_completed_orders(trade_dicts)
    return CompletedOrdersResponse(trades=trade_dicts)
