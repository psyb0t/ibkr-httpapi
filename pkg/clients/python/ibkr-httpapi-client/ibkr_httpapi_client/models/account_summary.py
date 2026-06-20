from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.account_summary_accounts import AccountSummaryAccounts


T = TypeVar("T", bound="AccountSummary")


@_attrs_define
class AccountSummary:
    """
    Attributes:
        accounts (AccountSummaryAccounts):
    """

    accounts: AccountSummaryAccounts
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        accounts = self.accounts.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "accounts": accounts,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.account_summary_accounts import AccountSummaryAccounts

        d = dict(src_dict)
        accounts = AccountSummaryAccounts.from_dict(d.pop("accounts"))

        account_summary = cls(
            accounts=accounts,
        )

        account_summary.additional_properties = d
        return account_summary

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
