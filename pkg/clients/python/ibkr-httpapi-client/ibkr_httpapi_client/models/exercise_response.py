from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.contract import Contract


T = TypeVar("T", bound="ExerciseResponse")


@_attrs_define
class ExerciseResponse:
    """
    Attributes:
        status (str | Unset):
        contract (Contract | Unset):
        action (str | Unset):
    """

    status: str | Unset = UNSET
    contract: Contract | Unset = UNSET
    action: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        status = self.status

        contract: dict[str, Any] | Unset = UNSET
        if not isinstance(self.contract, Unset):
            contract = self.contract.to_dict()

        action = self.action

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if status is not UNSET:
            field_dict["status"] = status
        if contract is not UNSET:
            field_dict["contract"] = contract
        if action is not UNSET:
            field_dict["action"] = action

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.contract import Contract

        d = dict(src_dict)
        status = d.pop("status", UNSET)

        _contract = d.pop("contract", UNSET)
        contract: Contract | Unset
        if isinstance(_contract, Unset):
            contract = UNSET
        else:
            contract = Contract.from_dict(_contract)

        action = d.pop("action", UNSET)

        exercise_response = cls(
            status=status,
            contract=contract,
            action=action,
        )

        exercise_response.additional_properties = d
        return exercise_response

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
