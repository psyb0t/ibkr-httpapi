from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.contract import Contract
    from ..models.order import Order
    from ..models.order_status import OrderStatus
    from ..models.trade_fills_item import TradeFillsItem
    from ..models.trade_log_item import TradeLogItem


T = TypeVar("T", bound="Trade")


@_attrs_define
class Trade:
    """
    Attributes:
        contract (Contract | Unset):
        order (Order | Unset):
        order_status (OrderStatus | Unset):
        fills (list[TradeFillsItem] | Unset):
        log (list[TradeLogItem] | Unset):
    """

    contract: Contract | Unset = UNSET
    order: Order | Unset = UNSET
    order_status: OrderStatus | Unset = UNSET
    fills: list[TradeFillsItem] | Unset = UNSET
    log: list[TradeLogItem] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        contract: dict[str, Any] | Unset = UNSET
        if not isinstance(self.contract, Unset):
            contract = self.contract.to_dict()

        order: dict[str, Any] | Unset = UNSET
        if not isinstance(self.order, Unset):
            order = self.order.to_dict()

        order_status: dict[str, Any] | Unset = UNSET
        if not isinstance(self.order_status, Unset):
            order_status = self.order_status.to_dict()

        fills: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.fills, Unset):
            fills = []
            for fills_item_data in self.fills:
                fills_item = fills_item_data.to_dict()
                fills.append(fills_item)

        log: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.log, Unset):
            log = []
            for log_item_data in self.log:
                log_item = log_item_data.to_dict()
                log.append(log_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if contract is not UNSET:
            field_dict["contract"] = contract
        if order is not UNSET:
            field_dict["order"] = order
        if order_status is not UNSET:
            field_dict["orderStatus"] = order_status
        if fills is not UNSET:
            field_dict["fills"] = fills
        if log is not UNSET:
            field_dict["log"] = log

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.contract import Contract
        from ..models.order import Order
        from ..models.order_status import OrderStatus
        from ..models.trade_fills_item import TradeFillsItem
        from ..models.trade_log_item import TradeLogItem

        d = dict(src_dict)
        _contract = d.pop("contract", UNSET)
        contract: Contract | Unset
        if isinstance(_contract, Unset):
            contract = UNSET
        else:
            contract = Contract.from_dict(_contract)

        _order = d.pop("order", UNSET)
        order: Order | Unset
        if isinstance(_order, Unset):
            order = UNSET
        else:
            order = Order.from_dict(_order)

        _order_status = d.pop("orderStatus", UNSET)
        order_status: OrderStatus | Unset
        if isinstance(_order_status, Unset):
            order_status = UNSET
        else:
            order_status = OrderStatus.from_dict(_order_status)

        _fills = d.pop("fills", UNSET)
        fills: list[TradeFillsItem] | Unset = UNSET
        if _fills is not UNSET:
            fills = []
            for fills_item_data in _fills:
                fills_item = TradeFillsItem.from_dict(fills_item_data)

                fills.append(fills_item)

        _log = d.pop("log", UNSET)
        log: list[TradeLogItem] | Unset = UNSET
        if _log is not UNSET:
            log = []
            for log_item_data in _log:
                log_item = TradeLogItem.from_dict(log_item_data)

                log.append(log_item)

        trade = cls(
            contract=contract,
            order=order,
            order_status=order_status,
            fills=fills,
            log=log,
        )

        trade.additional_properties = d
        return trade

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
