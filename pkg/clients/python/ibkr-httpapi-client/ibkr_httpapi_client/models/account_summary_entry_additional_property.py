from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="AccountSummaryEntryAdditionalProperty")


@_attrs_define
class AccountSummaryEntryAdditionalProperty:
    """
    Attributes:
        value (str | Unset):
        currency (str | Unset):
        model_code (str | Unset):
    """

    value: str | Unset = UNSET
    currency: str | Unset = UNSET
    model_code: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        value = self.value

        currency = self.currency

        model_code = self.model_code

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if value is not UNSET:
            field_dict["value"] = value
        if currency is not UNSET:
            field_dict["currency"] = currency
        if model_code is not UNSET:
            field_dict["modelCode"] = model_code

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        value = d.pop("value", UNSET)

        currency = d.pop("currency", UNSET)

        model_code = d.pop("modelCode", UNSET)

        account_summary_entry_additional_property = cls(
            value=value,
            currency=currency,
            model_code=model_code,
        )

        account_summary_entry_additional_property.additional_properties = d
        return account_summary_entry_additional_property

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
