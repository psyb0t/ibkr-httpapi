from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="OptionChainEntry")


@_attrs_define
class OptionChainEntry:
    """
    Attributes:
        exchange (str | Unset):
        trading_class (str | Unset):
        multiplier (str | Unset):
        expirations (list[str] | Unset):
        strikes (list[float] | Unset):
    """

    exchange: str | Unset = UNSET
    trading_class: str | Unset = UNSET
    multiplier: str | Unset = UNSET
    expirations: list[str] | Unset = UNSET
    strikes: list[float] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        exchange = self.exchange

        trading_class = self.trading_class

        multiplier = self.multiplier

        expirations: list[str] | Unset = UNSET
        if not isinstance(self.expirations, Unset):
            expirations = self.expirations

        strikes: list[float] | Unset = UNSET
        if not isinstance(self.strikes, Unset):
            strikes = self.strikes

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if exchange is not UNSET:
            field_dict["exchange"] = exchange
        if trading_class is not UNSET:
            field_dict["tradingClass"] = trading_class
        if multiplier is not UNSET:
            field_dict["multiplier"] = multiplier
        if expirations is not UNSET:
            field_dict["expirations"] = expirations
        if strikes is not UNSET:
            field_dict["strikes"] = strikes

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        exchange = d.pop("exchange", UNSET)

        trading_class = d.pop("tradingClass", UNSET)

        multiplier = d.pop("multiplier", UNSET)

        expirations = cast(list[str], d.pop("expirations", UNSET))

        strikes = cast(list[float], d.pop("strikes", UNSET))

        option_chain_entry = cls(
            exchange=exchange,
            trading_class=trading_class,
            multiplier=multiplier,
            expirations=expirations,
            strikes=strikes,
        )

        option_chain_entry.additional_properties = d
        return option_chain_entry

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
