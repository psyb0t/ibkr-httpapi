from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ExerciseRequest")


@_attrs_define
class ExerciseRequest:
    """
    Attributes:
        conid (int):
        action (str): EXERCISE or LAPSE
        quantity (int):
        account (str):
        override (bool | Unset):  Default: False.
    """

    conid: int
    action: str
    quantity: int
    account: str
    override: bool | Unset = False
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        conid = self.conid

        action = self.action

        quantity = self.quantity

        account = self.account

        override = self.override

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "conid": conid,
                "action": action,
                "quantity": quantity,
                "account": account,
            }
        )
        if override is not UNSET:
            field_dict["override"] = override

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        conid = d.pop("conid")

        action = d.pop("action")

        quantity = d.pop("quantity")

        account = d.pop("account")

        override = d.pop("override", UNSET)

        exercise_request = cls(
            conid=conid,
            action=action,
            quantity=quantity,
            account=account,
            override=override,
        )

        exercise_request.additional_properties = d
        return exercise_request

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
