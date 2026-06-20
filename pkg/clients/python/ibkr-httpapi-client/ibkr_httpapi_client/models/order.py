from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="Order")


@_attrs_define
class Order:
    """
    Attributes:
        order_id (int | Unset):
        perm_id (int | Unset):
        client_id (int | Unset):
        action (str | Unset):
        total_quantity (float | Unset):
        order_type (str | Unset):
        lmt_price (float | None | Unset):
        aux_price (float | None | Unset):
        tif (str | Unset):
        outside_rth (bool | Unset):
        transmit (bool | Unset):
        account (str | Unset):
        parent_id (int | Unset):
        oca_group (str | Unset):
        good_after_time (str | Unset):
        good_till_date (str | Unset):
    """

    order_id: int | Unset = UNSET
    perm_id: int | Unset = UNSET
    client_id: int | Unset = UNSET
    action: str | Unset = UNSET
    total_quantity: float | Unset = UNSET
    order_type: str | Unset = UNSET
    lmt_price: float | None | Unset = UNSET
    aux_price: float | None | Unset = UNSET
    tif: str | Unset = UNSET
    outside_rth: bool | Unset = UNSET
    transmit: bool | Unset = UNSET
    account: str | Unset = UNSET
    parent_id: int | Unset = UNSET
    oca_group: str | Unset = UNSET
    good_after_time: str | Unset = UNSET
    good_till_date: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        order_id = self.order_id

        perm_id = self.perm_id

        client_id = self.client_id

        action = self.action

        total_quantity = self.total_quantity

        order_type = self.order_type

        lmt_price: float | None | Unset
        if isinstance(self.lmt_price, Unset):
            lmt_price = UNSET
        else:
            lmt_price = self.lmt_price

        aux_price: float | None | Unset
        if isinstance(self.aux_price, Unset):
            aux_price = UNSET
        else:
            aux_price = self.aux_price

        tif = self.tif

        outside_rth = self.outside_rth

        transmit = self.transmit

        account = self.account

        parent_id = self.parent_id

        oca_group = self.oca_group

        good_after_time = self.good_after_time

        good_till_date = self.good_till_date

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if order_id is not UNSET:
            field_dict["orderId"] = order_id
        if perm_id is not UNSET:
            field_dict["permId"] = perm_id
        if client_id is not UNSET:
            field_dict["clientId"] = client_id
        if action is not UNSET:
            field_dict["action"] = action
        if total_quantity is not UNSET:
            field_dict["totalQuantity"] = total_quantity
        if order_type is not UNSET:
            field_dict["orderType"] = order_type
        if lmt_price is not UNSET:
            field_dict["lmtPrice"] = lmt_price
        if aux_price is not UNSET:
            field_dict["auxPrice"] = aux_price
        if tif is not UNSET:
            field_dict["tif"] = tif
        if outside_rth is not UNSET:
            field_dict["outsideRth"] = outside_rth
        if transmit is not UNSET:
            field_dict["transmit"] = transmit
        if account is not UNSET:
            field_dict["account"] = account
        if parent_id is not UNSET:
            field_dict["parentId"] = parent_id
        if oca_group is not UNSET:
            field_dict["ocaGroup"] = oca_group
        if good_after_time is not UNSET:
            field_dict["goodAfterTime"] = good_after_time
        if good_till_date is not UNSET:
            field_dict["goodTillDate"] = good_till_date

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        order_id = d.pop("orderId", UNSET)

        perm_id = d.pop("permId", UNSET)

        client_id = d.pop("clientId", UNSET)

        action = d.pop("action", UNSET)

        total_quantity = d.pop("totalQuantity", UNSET)

        order_type = d.pop("orderType", UNSET)

        def _parse_lmt_price(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        lmt_price = _parse_lmt_price(d.pop("lmtPrice", UNSET))

        def _parse_aux_price(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        aux_price = _parse_aux_price(d.pop("auxPrice", UNSET))

        tif = d.pop("tif", UNSET)

        outside_rth = d.pop("outsideRth", UNSET)

        transmit = d.pop("transmit", UNSET)

        account = d.pop("account", UNSET)

        parent_id = d.pop("parentId", UNSET)

        oca_group = d.pop("ocaGroup", UNSET)

        good_after_time = d.pop("goodAfterTime", UNSET)

        good_till_date = d.pop("goodTillDate", UNSET)

        order = cls(
            order_id=order_id,
            perm_id=perm_id,
            client_id=client_id,
            action=action,
            total_quantity=total_quantity,
            order_type=order_type,
            lmt_price=lmt_price,
            aux_price=aux_price,
            tif=tif,
            outside_rth=outside_rth,
            transmit=transmit,
            account=account,
            parent_id=parent_id,
            oca_group=oca_group,
            good_after_time=good_after_time,
            good_till_date=good_till_date,
        )

        order.additional_properties = d
        return order

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
