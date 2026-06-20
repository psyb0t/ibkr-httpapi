from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.bar import Bar


T = TypeVar("T", bound="BarsResponse")


@_attrs_define
class BarsResponse:
    """
    Attributes:
        bars (list[Bar]):
        symbol (None | str | Unset):
        pair (None | str | Unset):
        sec_type (None | str | Unset):
        expiry (None | str | Unset):
        strike (float | None | Unset):
        right (None | str | Unset):
    """

    bars: list[Bar]
    symbol: None | str | Unset = UNSET
    pair: None | str | Unset = UNSET
    sec_type: None | str | Unset = UNSET
    expiry: None | str | Unset = UNSET
    strike: float | None | Unset = UNSET
    right: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        bars = []
        for bars_item_data in self.bars:
            bars_item = bars_item_data.to_dict()
            bars.append(bars_item)

        symbol: None | str | Unset
        if isinstance(self.symbol, Unset):
            symbol = UNSET
        else:
            symbol = self.symbol

        pair: None | str | Unset
        if isinstance(self.pair, Unset):
            pair = UNSET
        else:
            pair = self.pair

        sec_type: None | str | Unset
        if isinstance(self.sec_type, Unset):
            sec_type = UNSET
        else:
            sec_type = self.sec_type

        expiry: None | str | Unset
        if isinstance(self.expiry, Unset):
            expiry = UNSET
        else:
            expiry = self.expiry

        strike: float | None | Unset
        if isinstance(self.strike, Unset):
            strike = UNSET
        else:
            strike = self.strike

        right: None | str | Unset
        if isinstance(self.right, Unset):
            right = UNSET
        else:
            right = self.right

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "bars": bars,
            }
        )
        if symbol is not UNSET:
            field_dict["symbol"] = symbol
        if pair is not UNSET:
            field_dict["pair"] = pair
        if sec_type is not UNSET:
            field_dict["secType"] = sec_type
        if expiry is not UNSET:
            field_dict["expiry"] = expiry
        if strike is not UNSET:
            field_dict["strike"] = strike
        if right is not UNSET:
            field_dict["right"] = right

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.bar import Bar

        d = dict(src_dict)
        bars = []
        _bars = d.pop("bars")
        for bars_item_data in _bars:
            bars_item = Bar.from_dict(bars_item_data)

            bars.append(bars_item)

        def _parse_symbol(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        symbol = _parse_symbol(d.pop("symbol", UNSET))

        def _parse_pair(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        pair = _parse_pair(d.pop("pair", UNSET))

        def _parse_sec_type(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        sec_type = _parse_sec_type(d.pop("secType", UNSET))

        def _parse_expiry(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        expiry = _parse_expiry(d.pop("expiry", UNSET))

        def _parse_strike(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        strike = _parse_strike(d.pop("strike", UNSET))

        def _parse_right(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        right = _parse_right(d.pop("right", UNSET))

        bars_response = cls(
            bars=bars,
            symbol=symbol,
            pair=pair,
            sec_type=sec_type,
            expiry=expiry,
            strike=strike,
            right=right,
        )

        bars_response.additional_properties = d
        return bars_response

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
