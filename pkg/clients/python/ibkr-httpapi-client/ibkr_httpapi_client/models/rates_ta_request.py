from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.rates_ta_request_indicators import RatesTARequestIndicators


T = TypeVar("T", bound="RatesTARequest")


@_attrs_define
class RatesTARequest:
    """
    Attributes:
        duration (str): IBKR duration string (e.g. '30 D', '1 Y')
        bar_size (None | str | Unset):
        end_date_time (None | str | Unset):
        what_to_show (None | str | Unset):
        use_rth (bool | Unset):  Default: False.
        indicators (RatesTARequestIndicators | Unset):
        recent_bars (int | None | Unset):
    """

    duration: str
    bar_size: None | str | Unset = UNSET
    end_date_time: None | str | Unset = UNSET
    what_to_show: None | str | Unset = UNSET
    use_rth: bool | Unset = False
    indicators: RatesTARequestIndicators | Unset = UNSET
    recent_bars: int | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        duration = self.duration

        bar_size: None | str | Unset
        if isinstance(self.bar_size, Unset):
            bar_size = UNSET
        else:
            bar_size = self.bar_size

        end_date_time: None | str | Unset
        if isinstance(self.end_date_time, Unset):
            end_date_time = UNSET
        else:
            end_date_time = self.end_date_time

        what_to_show: None | str | Unset
        if isinstance(self.what_to_show, Unset):
            what_to_show = UNSET
        else:
            what_to_show = self.what_to_show

        use_rth = self.use_rth

        indicators: dict[str, Any] | Unset = UNSET
        if not isinstance(self.indicators, Unset):
            indicators = self.indicators.to_dict()

        recent_bars: int | None | Unset
        if isinstance(self.recent_bars, Unset):
            recent_bars = UNSET
        else:
            recent_bars = self.recent_bars

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "duration": duration,
            }
        )
        if bar_size is not UNSET:
            field_dict["barSize"] = bar_size
        if end_date_time is not UNSET:
            field_dict["endDateTime"] = end_date_time
        if what_to_show is not UNSET:
            field_dict["whatToShow"] = what_to_show
        if use_rth is not UNSET:
            field_dict["useRTH"] = use_rth
        if indicators is not UNSET:
            field_dict["indicators"] = indicators
        if recent_bars is not UNSET:
            field_dict["recentBars"] = recent_bars

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.rates_ta_request_indicators import RatesTARequestIndicators

        d = dict(src_dict)
        duration = d.pop("duration")

        def _parse_bar_size(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        bar_size = _parse_bar_size(d.pop("barSize", UNSET))

        def _parse_end_date_time(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        end_date_time = _parse_end_date_time(d.pop("endDateTime", UNSET))

        def _parse_what_to_show(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        what_to_show = _parse_what_to_show(d.pop("whatToShow", UNSET))

        use_rth = d.pop("useRTH", UNSET)

        _indicators = d.pop("indicators", UNSET)
        indicators: RatesTARequestIndicators | Unset
        if isinstance(_indicators, Unset):
            indicators = UNSET
        else:
            indicators = RatesTARequestIndicators.from_dict(_indicators)

        def _parse_recent_bars(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        recent_bars = _parse_recent_bars(d.pop("recentBars", UNSET))

        rates_ta_request = cls(
            duration=duration,
            bar_size=bar_size,
            end_date_time=end_date_time,
            what_to_show=what_to_show,
            use_rth=use_rth,
            indicators=indicators,
            recent_bars=recent_bars,
        )

        rates_ta_request.additional_properties = d
        return rates_ta_request

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
