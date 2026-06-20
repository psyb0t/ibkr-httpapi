from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ComboLegSpec")


@_attrs_define
class ComboLegSpec:
    """
    Attributes:
        conid (int):
        action (str): BUY / SELL
        ratio (int | Unset):  Default: 1.
        exchange (str | Unset):  Default: 'SMART'.
    """

    conid: int
    action: str
    ratio: int | Unset = 1
    exchange: str | Unset = "SMART"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        conid = self.conid

        action = self.action

        ratio = self.ratio

        exchange = self.exchange

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "conid": conid,
                "action": action,
            }
        )
        if ratio is not UNSET:
            field_dict["ratio"] = ratio
        if exchange is not UNSET:
            field_dict["exchange"] = exchange

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        conid = d.pop("conid")

        action = d.pop("action")

        ratio = d.pop("ratio", UNSET)

        exchange = d.pop("exchange", UNSET)

        combo_leg_spec = cls(
            conid=conid,
            action=action,
            ratio=ratio,
            exchange=exchange,
        )

        combo_leg_spec.additional_properties = d
        return combo_leg_spec

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
