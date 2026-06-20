from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="OrderStatus")


@_attrs_define
class OrderStatus:
    """
    Attributes:
        status (str | Unset):
        filled (float | Unset):
        remaining (float | Unset):
        avg_fill_price (float | Unset):
        perm_id (int | Unset):
        last_fill_price (float | Unset):
        why_held (str | Unset):
        mkt_cap_price (float | Unset):
    """

    status: str | Unset = UNSET
    filled: float | Unset = UNSET
    remaining: float | Unset = UNSET
    avg_fill_price: float | Unset = UNSET
    perm_id: int | Unset = UNSET
    last_fill_price: float | Unset = UNSET
    why_held: str | Unset = UNSET
    mkt_cap_price: float | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        status = self.status

        filled = self.filled

        remaining = self.remaining

        avg_fill_price = self.avg_fill_price

        perm_id = self.perm_id

        last_fill_price = self.last_fill_price

        why_held = self.why_held

        mkt_cap_price = self.mkt_cap_price

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if status is not UNSET:
            field_dict["status"] = status
        if filled is not UNSET:
            field_dict["filled"] = filled
        if remaining is not UNSET:
            field_dict["remaining"] = remaining
        if avg_fill_price is not UNSET:
            field_dict["avgFillPrice"] = avg_fill_price
        if perm_id is not UNSET:
            field_dict["permId"] = perm_id
        if last_fill_price is not UNSET:
            field_dict["lastFillPrice"] = last_fill_price
        if why_held is not UNSET:
            field_dict["whyHeld"] = why_held
        if mkt_cap_price is not UNSET:
            field_dict["mktCapPrice"] = mkt_cap_price

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        status = d.pop("status", UNSET)

        filled = d.pop("filled", UNSET)

        remaining = d.pop("remaining", UNSET)

        avg_fill_price = d.pop("avgFillPrice", UNSET)

        perm_id = d.pop("permId", UNSET)

        last_fill_price = d.pop("lastFillPrice", UNSET)

        why_held = d.pop("whyHeld", UNSET)

        mkt_cap_price = d.pop("mktCapPrice", UNSET)

        order_status = cls(
            status=status,
            filled=filled,
            remaining=remaining,
            avg_fill_price=avg_fill_price,
            perm_id=perm_id,
            last_fill_price=last_fill_price,
            why_held=why_held,
            mkt_cap_price=mkt_cap_price,
        )

        order_status.additional_properties = d
        return order_status

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
