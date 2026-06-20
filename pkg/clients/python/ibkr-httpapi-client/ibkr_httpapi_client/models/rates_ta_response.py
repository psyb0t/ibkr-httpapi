from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.bar import Bar
    from ..models.rates_ta_response_ta_type_0 import RatesTAResponseTaType0


T = TypeVar("T", bound="RatesTAResponse")


@_attrs_define
class RatesTAResponse:
    """
    Attributes:
        bars (list[Bar]):
        symbol (None | str | Unset):
        sec_type (None | str | Unset):
        ta (None | RatesTAResponseTaType0 | Unset):
        as_of (None | str | Unset):
    """

    bars: list[Bar]
    symbol: None | str | Unset = UNSET
    sec_type: None | str | Unset = UNSET
    ta: None | RatesTAResponseTaType0 | Unset = UNSET
    as_of: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.rates_ta_response_ta_type_0 import RatesTAResponseTaType0

        bars = []
        for bars_item_data in self.bars:
            bars_item = bars_item_data.to_dict()
            bars.append(bars_item)

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

        ta: dict[str, Any] | None | Unset
        if isinstance(self.ta, Unset):
            ta = UNSET
        elif isinstance(self.ta, RatesTAResponseTaType0):
            ta = self.ta.to_dict()
        else:
            ta = self.ta

        as_of: None | str | Unset
        if isinstance(self.as_of, Unset):
            as_of = UNSET
        else:
            as_of = self.as_of

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "bars": bars,
            }
        )
        if symbol is not UNSET:
            field_dict["symbol"] = symbol
        if sec_type is not UNSET:
            field_dict["secType"] = sec_type
        if ta is not UNSET:
            field_dict["ta"] = ta
        if as_of is not UNSET:
            field_dict["asOf"] = as_of

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.bar import Bar
        from ..models.rates_ta_response_ta_type_0 import RatesTAResponseTaType0

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

        def _parse_sec_type(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        sec_type = _parse_sec_type(d.pop("secType", UNSET))

        def _parse_ta(data: object) -> None | RatesTAResponseTaType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                ta_type_0 = RatesTAResponseTaType0.from_dict(data)

                return ta_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | RatesTAResponseTaType0 | Unset, data)

        ta = _parse_ta(d.pop("ta", UNSET))

        def _parse_as_of(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        as_of = _parse_as_of(d.pop("asOf", UNSET))

        rates_ta_response = cls(
            bars=bars,
            symbol=symbol,
            sec_type=sec_type,
            ta=ta,
            as_of=as_of,
        )

        rates_ta_response.additional_properties = d
        return rates_ta_response

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
