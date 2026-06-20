from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="Contract")


@_attrs_define
class Contract:
    """
    Attributes:
        conid (int):
        symbol (str):
        sec_type (str):
        exchange (str):
        currency (str):
        primary_exchange (str | Unset):
        last_trade_date_or_contract_month (str | Unset):
        strike (float | Unset):
        right (str | Unset):
        multiplier (str | Unset):
        trading_class (str | Unset):
        local_symbol (str | Unset):
    """

    conid: int
    symbol: str
    sec_type: str
    exchange: str
    currency: str
    primary_exchange: str | Unset = UNSET
    last_trade_date_or_contract_month: str | Unset = UNSET
    strike: float | Unset = UNSET
    right: str | Unset = UNSET
    multiplier: str | Unset = UNSET
    trading_class: str | Unset = UNSET
    local_symbol: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        conid = self.conid

        symbol = self.symbol

        sec_type = self.sec_type

        exchange = self.exchange

        currency = self.currency

        primary_exchange = self.primary_exchange

        last_trade_date_or_contract_month = self.last_trade_date_or_contract_month

        strike = self.strike

        right = self.right

        multiplier = self.multiplier

        trading_class = self.trading_class

        local_symbol = self.local_symbol

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "conid": conid,
                "symbol": symbol,
                "secType": sec_type,
                "exchange": exchange,
                "currency": currency,
            }
        )
        if primary_exchange is not UNSET:
            field_dict["primaryExchange"] = primary_exchange
        if last_trade_date_or_contract_month is not UNSET:
            field_dict["lastTradeDateOrContractMonth"] = last_trade_date_or_contract_month
        if strike is not UNSET:
            field_dict["strike"] = strike
        if right is not UNSET:
            field_dict["right"] = right
        if multiplier is not UNSET:
            field_dict["multiplier"] = multiplier
        if trading_class is not UNSET:
            field_dict["tradingClass"] = trading_class
        if local_symbol is not UNSET:
            field_dict["localSymbol"] = local_symbol

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        conid = d.pop("conid")

        symbol = d.pop("symbol")

        sec_type = d.pop("secType")

        exchange = d.pop("exchange")

        currency = d.pop("currency")

        primary_exchange = d.pop("primaryExchange", UNSET)

        last_trade_date_or_contract_month = d.pop("lastTradeDateOrContractMonth", UNSET)

        strike = d.pop("strike", UNSET)

        right = d.pop("right", UNSET)

        multiplier = d.pop("multiplier", UNSET)

        trading_class = d.pop("tradingClass", UNSET)

        local_symbol = d.pop("localSymbol", UNSET)

        contract = cls(
            conid=conid,
            symbol=symbol,
            sec_type=sec_type,
            exchange=exchange,
            currency=currency,
            primary_exchange=primary_exchange,
            last_trade_date_or_contract_month=last_trade_date_or_contract_month,
            strike=strike,
            right=right,
            multiplier=multiplier,
            trading_class=trading_class,
            local_symbol=local_symbol,
        )

        contract.additional_properties = d
        return contract

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
