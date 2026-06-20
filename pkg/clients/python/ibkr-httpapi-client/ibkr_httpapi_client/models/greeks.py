from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="Greeks")


@_attrs_define
class Greeks:
    """
    Attributes:
        delta (float | None | Unset):
        gamma (float | None | Unset):
        theta (float | None | Unset):
        vega (float | None | Unset):
        implied_vol (float | None | Unset):
        opt_price (float | None | Unset):
        und_price (float | None | Unset):
    """

    delta: float | None | Unset = UNSET
    gamma: float | None | Unset = UNSET
    theta: float | None | Unset = UNSET
    vega: float | None | Unset = UNSET
    implied_vol: float | None | Unset = UNSET
    opt_price: float | None | Unset = UNSET
    und_price: float | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        delta: float | None | Unset
        if isinstance(self.delta, Unset):
            delta = UNSET
        else:
            delta = self.delta

        gamma: float | None | Unset
        if isinstance(self.gamma, Unset):
            gamma = UNSET
        else:
            gamma = self.gamma

        theta: float | None | Unset
        if isinstance(self.theta, Unset):
            theta = UNSET
        else:
            theta = self.theta

        vega: float | None | Unset
        if isinstance(self.vega, Unset):
            vega = UNSET
        else:
            vega = self.vega

        implied_vol: float | None | Unset
        if isinstance(self.implied_vol, Unset):
            implied_vol = UNSET
        else:
            implied_vol = self.implied_vol

        opt_price: float | None | Unset
        if isinstance(self.opt_price, Unset):
            opt_price = UNSET
        else:
            opt_price = self.opt_price

        und_price: float | None | Unset
        if isinstance(self.und_price, Unset):
            und_price = UNSET
        else:
            und_price = self.und_price

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if delta is not UNSET:
            field_dict["delta"] = delta
        if gamma is not UNSET:
            field_dict["gamma"] = gamma
        if theta is not UNSET:
            field_dict["theta"] = theta
        if vega is not UNSET:
            field_dict["vega"] = vega
        if implied_vol is not UNSET:
            field_dict["impliedVol"] = implied_vol
        if opt_price is not UNSET:
            field_dict["optPrice"] = opt_price
        if und_price is not UNSET:
            field_dict["undPrice"] = und_price

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)

        def _parse_delta(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        delta = _parse_delta(d.pop("delta", UNSET))

        def _parse_gamma(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        gamma = _parse_gamma(d.pop("gamma", UNSET))

        def _parse_theta(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        theta = _parse_theta(d.pop("theta", UNSET))

        def _parse_vega(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        vega = _parse_vega(d.pop("vega", UNSET))

        def _parse_implied_vol(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        implied_vol = _parse_implied_vol(d.pop("impliedVol", UNSET))

        def _parse_opt_price(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        opt_price = _parse_opt_price(d.pop("optPrice", UNSET))

        def _parse_und_price(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        und_price = _parse_und_price(d.pop("undPrice", UNSET))

        greeks = cls(
            delta=delta,
            gamma=gamma,
            theta=theta,
            vega=vega,
            implied_vol=implied_vol,
            opt_price=opt_price,
            und_price=und_price,
        )

        greeks.additional_properties = d
        return greeks

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
