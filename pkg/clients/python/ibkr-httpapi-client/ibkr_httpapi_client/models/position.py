from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.contract import Contract


T = TypeVar("T", bound="Position")


@_attrs_define
class Position:
    """
    Attributes:
        account (str):
        contract (Contract):
        position (float):
        avg_cost (float):
    """

    account: str
    contract: Contract
    position: float
    avg_cost: float
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        account = self.account

        contract = self.contract.to_dict()

        position = self.position

        avg_cost = self.avg_cost

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "account": account,
                "contract": contract,
                "position": position,
                "avgCost": avg_cost,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.contract import Contract

        d = dict(src_dict)
        account = d.pop("account")

        contract = Contract.from_dict(d.pop("contract"))

        position = d.pop("position")

        avg_cost = d.pop("avgCost")

        position = cls(
            account=account,
            contract=contract,
            position=position,
            avg_cost=avg_cost,
        )

        position.additional_properties = d
        return position

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
