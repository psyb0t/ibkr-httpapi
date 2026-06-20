from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.tick import Tick


T = TypeVar("T", bound="TicksResponse")


@_attrs_define
class TicksResponse:
    """
    Attributes:
        ticks (list[Tick]):
        symbol (None | str | Unset):
        sec_type (None | str | Unset):
    """

    ticks: list[Tick]
    symbol: None | str | Unset = UNSET
    sec_type: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        ticks = []
        for ticks_item_data in self.ticks:
            ticks_item = ticks_item_data.to_dict()
            ticks.append(ticks_item)

        symbol: None | str | Unset
        if isinstance(self.symbol, Unset):
            symbol = UNSET
        else:
            symbol = self.symbol

        sec_type: None | str | Unset
        if isinstance(self.sec_type, Unset):
            sec_type = UNSET
        else:
            sec_type = self.sec_type

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "ticks": ticks,
            }
        )
        if symbol is not UNSET:
            field_dict["symbol"] = symbol
        if sec_type is not UNSET:
            field_dict["secType"] = sec_type

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.tick import Tick

        d = dict(src_dict)
        ticks = []
        _ticks = d.pop("ticks")
        for ticks_item_data in _ticks:
            ticks_item = Tick.from_dict(ticks_item_data)

            ticks.append(ticks_item)

        def _parse_symbol(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        symbol = _parse_symbol(d.pop("symbol", UNSET))

        def _parse_sec_type(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        sec_type = _parse_sec_type(d.pop("secType", UNSET))

        ticks_response = cls(
            ticks=ticks,
            symbol=symbol,
            sec_type=sec_type,
        )

        ticks_response.additional_properties = d
        return ticks_response

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
