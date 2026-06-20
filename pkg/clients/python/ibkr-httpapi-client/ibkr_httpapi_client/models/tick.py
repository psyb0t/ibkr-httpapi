from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="Tick")


@_attrs_define
class Tick:
    """
    Attributes:
        time (str):
        price (float | None | Unset):
        size (float | None | Unset):
        bid (float | None | Unset):
        ask (float | None | Unset):
        bid_size (float | None | Unset):
        ask_size (float | None | Unset):
    """

    time: str
    price: float | None | Unset = UNSET
    size: float | None | Unset = UNSET
    bid: float | None | Unset = UNSET
    ask: float | None | Unset = UNSET
    bid_size: float | None | Unset = UNSET
    ask_size: float | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        time = self.time

        price: float | None | Unset
        if isinstance(self.price, Unset):
            price = UNSET
        else:
            price = self.price

        size: float | None | Unset
        if isinstance(self.size, Unset):
            size = UNSET
        else:
            size = self.size

        bid: float | None | Unset
        if isinstance(self.bid, Unset):
            bid = UNSET
        else:
            bid = self.bid

        ask: float | None | Unset
        if isinstance(self.ask, Unset):
            ask = UNSET
        else:
            ask = self.ask

        bid_size: float | None | Unset
        if isinstance(self.bid_size, Unset):
            bid_size = UNSET
        else:
            bid_size = self.bid_size

        ask_size: float | None | Unset
        if isinstance(self.ask_size, Unset):
            ask_size = UNSET
        else:
            ask_size = self.ask_size

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "time": time,
            }
        )
        if price is not UNSET:
            field_dict["price"] = price
        if size is not UNSET:
            field_dict["size"] = size
        if bid is not UNSET:
            field_dict["bid"] = bid
        if ask is not UNSET:
            field_dict["ask"] = ask
        if bid_size is not UNSET:
            field_dict["bidSize"] = bid_size
        if ask_size is not UNSET:
            field_dict["askSize"] = ask_size

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        time = d.pop("time")

        def _parse_price(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        price = _parse_price(d.pop("price", UNSET))

        def _parse_size(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        size = _parse_size(d.pop("size", UNSET))

        def _parse_bid(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        bid = _parse_bid(d.pop("bid", UNSET))

        def _parse_ask(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        ask = _parse_ask(d.pop("ask", UNSET))

        def _parse_bid_size(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        bid_size = _parse_bid_size(d.pop("bidSize", UNSET))

        def _parse_ask_size(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        ask_size = _parse_ask_size(d.pop("askSize", UNSET))

        tick = cls(
            time=time,
            price=price,
            size=size,
            bid=bid,
            ask=ask,
            bid_size=bid_size,
            ask_size=ask_size,
        )

        tick.additional_properties = d
        return tick

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
