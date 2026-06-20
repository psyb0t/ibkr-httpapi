"""Asset-class → ib_async Contract factories.

URL-keyed `/<asset_class>/<symbol>/...` routes hit these factories to
build a properly-typed Contract. Each factory accepts the URL symbol +
any query/body params needed to disambiguate (e.g. options need expiry +
strike + right).

Project-wide defaults from `config.contract_defaults` fill in exchange
and currency when the caller doesn't override.
"""

from __future__ import annotations

from ib_async import (
    CFD,
    Bag,
    ComboLeg,
    Contract,
    Crypto,
    Forex,
    Future,
    Index,
    Option,
    Stock,
)

from ibkrapi.config import CONTRACT_DEFAULTS


def _defaults(asset_class: str) -> dict:
    return CONTRACT_DEFAULTS.get(asset_class) or {}


def stock(
    symbol: str,
    exchange: str | None = None,
    currency: str | None = None,
    primary_exchange: str | None = None,
) -> Stock:
    d = _defaults("stocks")
    return Stock(
        symbol=symbol,
        exchange=exchange or d.get("exchange") or "SMART",
        currency=currency or d.get("currency") or "USD",
        primaryExchange=primary_exchange or "",
    )


def option(
    symbol: str,
    expiry: str,
    strike: float,
    right: str,
    exchange: str | None = None,
    currency: str | None = None,
    multiplier: str | None = None,
    trading_class: str | None = None,
) -> Option:
    """expiry: YYYYMMDD or YYYYMM. right: 'C' or 'P'."""
    d = _defaults("options")
    right_norm = right.upper()
    if right_norm not in ("C", "P", "CALL", "PUT"):
        raise ValueError(f"option right must be C/P/CALL/PUT, got {right!r}")
    return Option(
        symbol=symbol,
        lastTradeDateOrContractMonth=expiry,
        strike=float(strike),
        right=right_norm[0],
        exchange=exchange or d.get("exchange") or "SMART",
        currency=currency or d.get("currency") or "USD",
        multiplier=multiplier or d.get("multiplier") or "100",
        tradingClass=trading_class or "",
    )


def future(
    symbol: str,
    expiry: str,
    exchange: str,
    currency: str | None = None,
    multiplier: str | None = None,
    trading_class: str | None = None,
    include_expired: bool = False,
) -> Future:
    """expiry: YYYYMMDD or YYYYMM. exchange MUST be explicit (CME, NYMEX, ...)."""
    d = _defaults("futures")
    return Future(
        symbol=symbol,
        lastTradeDateOrContractMonth=expiry,
        exchange=exchange or d.get("exchange") or "",
        currency=currency or d.get("currency") or "USD",
        multiplier=multiplier or "",
        tradingClass=trading_class or "",
        includeExpired=include_expired,
    )


def cfd(
    symbol: str,
    exchange: str | None = None,
    currency: str | None = None,
) -> CFD:
    d = _defaults("cfd")
    return CFD(
        symbol=symbol,
        exchange=exchange or d.get("exchange") or "SMART",
        currency=currency or d.get("currency") or "USD",
    )


def forex(pair: str, exchange: str | None = None) -> Forex:
    """pair: 6-letter like EURUSD; 7-letter like EURUSD.r is broker-specific."""
    d = _defaults("forex")
    return Forex(pair=pair, exchange=exchange or d.get("exchange") or "IDEALPRO")


def crypto(
    symbol: str,
    exchange: str | None = None,
    currency: str | None = None,
) -> Crypto:
    d = _defaults("crypto")
    return Crypto(
        symbol=symbol,
        exchange=exchange or d.get("exchange") or "PAXOS",
        currency=currency or d.get("currency") or "USD",
    )


def index(
    symbol: str,
    exchange: str | None = None,
    currency: str | None = None,
) -> Index:
    d = _defaults("index")
    return Index(
        symbol=symbol,
        exchange=exchange or d.get("exchange") or "CBOE",
        currency=currency or d.get("currency") or "USD",
    )


def combo(
    symbol: str,
    legs: list[dict],
    exchange: str = "SMART",
    currency: str = "USD",
) -> Bag:
    """Multi-leg combo (spread/condor/butterfly/calendar).

    Each leg dict: {conid, ratio, action (BUY/SELL), exchange (default SMART)}.
    Use the conid returned by qualifyContractsAsync on each leg.
    """
    bag = Bag(symbol=symbol, exchange=exchange, currency=currency)
    bag.comboLegs = [
        ComboLeg(
            conId=int(leg["conid"]),
            ratio=int(leg.get("ratio", 1)),
            action=str(leg["action"]).upper(),
            exchange=leg.get("exchange") or exchange,
        )
        for leg in legs
    ]
    return bag


def by_conid(conid: int) -> Contract:
    """Construct a bare Contract from a numeric conid.

    qualifyContractsAsync will fill in the rest. Useful when the client
    already knows the contract from a prior chain lookup.
    """
    return Contract(conId=int(conid))
