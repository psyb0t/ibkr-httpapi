"""Dataclass → dict converters for ib_async types.

ib_async objects are dataclasses with nested dataclasses (Contract,
Order, OrderStatus, Fill, ...). We never want to ship them raw to
clients — they contain SDK plumbing fields. These helpers extract the
caller-relevant subset and return plain dicts the FastAPI JSON encoder
can handle.
"""

from __future__ import annotations

import math
from dataclasses import asdict, is_dataclass
from datetime import datetime
from typing import Any


def _scrub(value: Any) -> Any:
    """ib_async signals 'no quote yet' with NaN / +-Inf floats. JSON
    spec doesn't allow either — return None so FastAPI emits `null`."""
    if isinstance(value, float) and not math.isfinite(value):
        return None
    return value


def _coerce(value: Any) -> Any:
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, float):
        return _scrub(value)
    if is_dataclass(value) and not isinstance(value, type):
        return {k: _coerce(v) for k, v in asdict(value).items()}
    if isinstance(value, (list, tuple)):
        return [_coerce(v) for v in value]
    if isinstance(value, dict):
        return {k: _coerce(v) for k, v in value.items()}
    return value


def contract_dict(contract) -> dict:
    return {
        "conid": contract.conId,
        "symbol": contract.symbol,
        "secType": contract.secType,
        "exchange": contract.exchange,
        "primaryExchange": getattr(contract, "primaryExchange", ""),
        "currency": contract.currency,
        "lastTradeDateOrContractMonth": getattr(contract, "lastTradeDateOrContractMonth", ""),
        "strike": getattr(contract, "strike", 0.0),
        "right": getattr(contract, "right", ""),
        "multiplier": getattr(contract, "multiplier", ""),
        "tradingClass": getattr(contract, "tradingClass", ""),
        "localSymbol": getattr(contract, "localSymbol", ""),
    }


def contract_details_dict(details) -> dict:
    contract = details.contract
    return {
        "contract": contract_dict(contract),
        "marketName": details.marketName,
        "minTick": details.minTick,
        "orderTypes": (details.orderTypes or "").split(",") if details.orderTypes else [],
        "validExchanges": (details.validExchanges or "").split(",")
        if details.validExchanges
        else [],
        "priceMagnifier": details.priceMagnifier,
        "longName": details.longName,
        "industry": details.industry,
        "category": details.category,
        "subcategory": details.subcategory,
        "timeZoneId": details.timeZoneId,
        "tradingHours": details.tradingHours,
        "liquidHours": details.liquidHours,
        "evRule": details.evRule,
        "evMultiplier": details.evMultiplier,
    }


def ticker_dict(ticker) -> dict:
    out = {
        "contract": contract_dict(ticker.contract),
        "time": ticker.time.isoformat() if ticker.time else None,
        "bid": _scrub(ticker.bid),
        "bidSize": _scrub(ticker.bidSize),
        "ask": _scrub(ticker.ask),
        "askSize": _scrub(ticker.askSize),
        "last": _scrub(ticker.last),
        "lastSize": _scrub(ticker.lastSize),
        "close": _scrub(ticker.close),
        "open": _scrub(ticker.open),
        "high": _scrub(ticker.high),
        "low": _scrub(ticker.low),
        "volume": _scrub(ticker.volume),
        "vwap": _scrub(ticker.vwap),
        "halted": _scrub(ticker.halted),
    }
    if getattr(ticker, "modelGreeks", None):
        out["modelGreeks"] = _coerce(ticker.modelGreeks)
    if getattr(ticker, "bidGreeks", None):
        out["bidGreeks"] = _coerce(ticker.bidGreeks)
    if getattr(ticker, "askGreeks", None):
        out["askGreeks"] = _coerce(ticker.askGreeks)
    if getattr(ticker, "lastGreeks", None):
        out["lastGreeks"] = _coerce(ticker.lastGreeks)
    return out


def bar_dict(bar) -> dict:
    return {
        "time": bar.date.isoformat() if hasattr(bar.date, "isoformat") else str(bar.date),
        "open": bar.open,
        "high": bar.high,
        "low": bar.low,
        "close": bar.close,
        "volume": bar.volume,
        "average": getattr(bar, "average", None),
        "barCount": getattr(bar, "barCount", None),
    }


def tick_dict(tick) -> dict:
    return {
        "time": tick.time.isoformat() if hasattr(tick.time, "isoformat") else str(tick.time),
        "price": getattr(tick, "price", None),
        "size": getattr(tick, "size", None),
        "bid": getattr(tick, "priceBid", None),
        "ask": getattr(tick, "priceAsk", None),
        "bidSize": getattr(tick, "sizeBid", None),
        "askSize": getattr(tick, "sizeAsk", None),
    }


def order_dict(order) -> dict:
    return {
        "orderId": order.orderId,
        "permId": order.permId,
        "clientId": order.clientId,
        "action": order.action,
        "totalQuantity": order.totalQuantity,
        "orderType": order.orderType,
        "lmtPrice": order.lmtPrice,
        "auxPrice": order.auxPrice,
        "tif": order.tif,
        "outsideRth": order.outsideRth,
        "transmit": order.transmit,
        "account": order.account,
        "parentId": order.parentId,
        "ocaGroup": order.ocaGroup,
        "goodAfterTime": order.goodAfterTime,
        "goodTillDate": order.goodTillDate,
    }


def order_status_dict(status) -> dict:
    return {
        "status": status.status,
        "filled": status.filled,
        "remaining": status.remaining,
        "avgFillPrice": status.avgFillPrice,
        "permId": status.permId,
        "lastFillPrice": status.lastFillPrice,
        "whyHeld": status.whyHeld,
        "mktCapPrice": status.mktCapPrice,
    }


def trade_dict(trade) -> dict:
    return {
        "contract": contract_dict(trade.contract),
        "order": order_dict(trade.order),
        "orderStatus": order_status_dict(trade.orderStatus),
        "fills": [_coerce(fill) for fill in trade.fills],
        "log": [_coerce(entry) for entry in trade.log],
    }


def position_dict(position) -> dict:
    return {
        "account": position.account,
        "contract": contract_dict(position.contract),
        "position": position.position,
        "avgCost": position.avgCost,
    }
