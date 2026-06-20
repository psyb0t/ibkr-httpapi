from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.combo_leg_spec import ComboLegSpec


T = TypeVar("T", bound="ComboOrderRequest")


@_attrs_define
class ComboOrderRequest:
    """
    Attributes:
        symbol (str):
        legs (list[ComboLegSpec]):
        action (str):
        quantity (int):
        order_type (str | Unset):  Default: 'LMT'.
        lmt_price (float | None | Unset):
        tif (str | Unset):  Default: 'DAY'.
        exchange (str | Unset):  Default: 'SMART'.
        currency (str | Unset):  Default: 'USD'.
        account (None | str | Unset):
    """

    symbol: str
    legs: list[ComboLegSpec]
    action: str
    quantity: int
    order_type: str | Unset = "LMT"
    lmt_price: float | None | Unset = UNSET
    tif: str | Unset = "DAY"
    exchange: str | Unset = "SMART"
    currency: str | Unset = "USD"
    account: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        symbol = self.symbol

        legs = []
        for legs_item_data in self.legs:
            legs_item = legs_item_data.to_dict()
            legs.append(legs_item)

        action = self.action

        quantity = self.quantity

        order_type = self.order_type

        lmt_price: float | None | Unset
        if isinstance(self.lmt_price, Unset):
            lmt_price = UNSET
        else:
            lmt_price = self.lmt_price

        tif = self.tif

        exchange = self.exchange

        currency = self.currency

        account: None | str | Unset
        if isinstance(self.account, Unset):
            account = UNSET
        else:
            account = self.account

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "symbol": symbol,
                "legs": legs,
                "action": action,
                "quantity": quantity,
            }
        )
        if order_type is not UNSET:
            field_dict["orderType"] = order_type
        if lmt_price is not UNSET:
            field_dict["lmtPrice"] = lmt_price
        if tif is not UNSET:
            field_dict["tif"] = tif
        if exchange is not UNSET:
            field_dict["exchange"] = exchange
        if currency is not UNSET:
            field_dict["currency"] = currency
        if account is not UNSET:
            field_dict["account"] = account

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.combo_leg_spec import ComboLegSpec

        d = dict(src_dict)
        symbol = d.pop("symbol")

        legs = []
        _legs = d.pop("legs")
        for legs_item_data in _legs:
            legs_item = ComboLegSpec.from_dict(legs_item_data)

            legs.append(legs_item)

        action = d.pop("action")

        quantity = d.pop("quantity")

        order_type = d.pop("orderType", UNSET)

        def _parse_lmt_price(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        lmt_price = _parse_lmt_price(d.pop("lmtPrice", UNSET))

        tif = d.pop("tif", UNSET)

        exchange = d.pop("exchange", UNSET)

        currency = d.pop("currency", UNSET)

        def _parse_account(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        account = _parse_account(d.pop("account", UNSET))

        combo_order_request = cls(
            symbol=symbol,
            legs=legs,
            action=action,
            quantity=quantity,
            order_type=order_type,
            lmt_price=lmt_price,
            tif=tif,
            exchange=exchange,
            currency=currency,
            account=account,
        )

        combo_order_request.additional_properties = d
        return combo_order_request

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
