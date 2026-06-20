from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.completed_orders_response_trades_item import CompletedOrdersResponseTradesItem


T = TypeVar("T", bound="CompletedOrdersResponse")


@_attrs_define
class CompletedOrdersResponse:
    """
    Attributes:
        trades (list[CompletedOrdersResponseTradesItem]):
    """

    trades: list[CompletedOrdersResponseTradesItem]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        trades = []
        for trades_item_data in self.trades:
            trades_item = trades_item_data.to_dict()
            trades.append(trades_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "trades": trades,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.completed_orders_response_trades_item import CompletedOrdersResponseTradesItem

        d = dict(src_dict)
        trades = []
        _trades = d.pop("trades")
        for trades_item_data in _trades:
            trades_item = CompletedOrdersResponseTradesItem.from_dict(trades_item_data)

            trades.append(trades_item)

        completed_orders_response = cls(
            trades=trades,
        )

        completed_orders_response.additional_properties = d
        return completed_orders_response

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
