from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.fill import Fill


T = TypeVar("T", bound="ExecutionsResponse")


@_attrs_define
class ExecutionsResponse:
    """
    Attributes:
        fills (list[Fill]):
    """

    fills: list[Fill]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        fills = []
        for fills_item_data in self.fills:
            fills_item = fills_item_data.to_dict()
            fills.append(fills_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "fills": fills,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.fill import Fill

        d = dict(src_dict)
        fills = []
        _fills = d.pop("fills")
        for fills_item_data in _fills:
            fills_item = Fill.from_dict(fills_item_data)

            fills.append(fills_item)

        executions_response = cls(
            fills=fills,
        )

        executions_response.additional_properties = d
        return executions_response

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
