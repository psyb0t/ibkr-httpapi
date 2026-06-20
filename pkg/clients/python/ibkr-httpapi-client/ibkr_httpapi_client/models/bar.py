from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="Bar")


@_attrs_define
class Bar:
    """
    Attributes:
        time (str):
        open_ (float):
        high (float):
        low (float):
        close (float):
        volume (float | None | Unset):
        average (float | None | Unset):
        bar_count (int | None | Unset):
    """

    time: str
    open_: float
    high: float
    low: float
    close: float
    volume: float | None | Unset = UNSET
    average: float | None | Unset = UNSET
    bar_count: int | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        time = self.time

        open_ = self.open_

        high = self.high

        low = self.low

        close = self.close

        volume: float | None | Unset
        if isinstance(self.volume, Unset):
            volume = UNSET
        else:
            volume = self.volume

        average: float | None | Unset
        if isinstance(self.average, Unset):
            average = UNSET
        else:
            average = self.average

        bar_count: int | None | Unset
        if isinstance(self.bar_count, Unset):
            bar_count = UNSET
        else:
            bar_count = self.bar_count

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "time": time,
                "open": open_,
                "high": high,
                "low": low,
                "close": close,
            }
        )
        if volume is not UNSET:
            field_dict["volume"] = volume
        if average is not UNSET:
            field_dict["average"] = average
        if bar_count is not UNSET:
            field_dict["barCount"] = bar_count

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        time = d.pop("time")

        open_ = d.pop("open")

        high = d.pop("high")

        low = d.pop("low")

        close = d.pop("close")

        def _parse_volume(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        volume = _parse_volume(d.pop("volume", UNSET))

        def _parse_average(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        average = _parse_average(d.pop("average", UNSET))

        def _parse_bar_count(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        bar_count = _parse_bar_count(d.pop("barCount", UNSET))

        bar = cls(
            time=time,
            open_=open_,
            high=high,
            low=low,
            close=close,
            volume=volume,
            average=average,
            bar_count=bar_count,
        )

        bar.additional_properties = d
        return bar

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
