from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="OrderRequest")


@_attrs_define
class OrderRequest:
    """
    Attributes:
        asset_class (str): stock / option / future / cfd / forex / crypto
        symbol (str):
        action (str): BUY or SELL
        quantity (float):
        expiry (None | str | Unset):
        strike (float | None | Unset):
        right (None | str | Unset):
        exchange (None | str | Unset):
        currency (None | str | Unset):
        multiplier (None | str | Unset):
        trading_class (None | str | Unset):
        primary_exchange (None | str | Unset):
        conid (int | None | Unset):
        order_type (str | Unset):  Default: 'MKT'.
        lmt_price (float | None | Unset):
        aux_price (float | None | Unset):
        tif (str | Unset):  Default: 'DAY'.
        outside_rth (bool | Unset):  Default: False.
        transmit (bool | Unset):  Default: True.
        account (None | str | Unset):
        good_after_time (None | str | Unset):
        good_till_date (None | str | Unset):
        oca_group (None | str | Unset):
        parent_id (int | None | Unset):
    """

    asset_class: str
    symbol: str
    action: str
    quantity: float
    expiry: None | str | Unset = UNSET
    strike: float | None | Unset = UNSET
    right: None | str | Unset = UNSET
    exchange: None | str | Unset = UNSET
    currency: None | str | Unset = UNSET
    multiplier: None | str | Unset = UNSET
    trading_class: None | str | Unset = UNSET
    primary_exchange: None | str | Unset = UNSET
    conid: int | None | Unset = UNSET
    order_type: str | Unset = "MKT"
    lmt_price: float | None | Unset = UNSET
    aux_price: float | None | Unset = UNSET
    tif: str | Unset = "DAY"
    outside_rth: bool | Unset = False
    transmit: bool | Unset = True
    account: None | str | Unset = UNSET
    good_after_time: None | str | Unset = UNSET
    good_till_date: None | str | Unset = UNSET
    oca_group: None | str | Unset = UNSET
    parent_id: int | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        asset_class = self.asset_class

        symbol = self.symbol

        action = self.action

        quantity = self.quantity

        expiry: None | str | Unset
        if isinstance(self.expiry, Unset):
            expiry = UNSET
        else:
            expiry = self.expiry

        strike: float | None | Unset
        if isinstance(self.strike, Unset):
            strike = UNSET
        else:
            strike = self.strike

        right: None | str | Unset
        if isinstance(self.right, Unset):
            right = UNSET
        else:
            right = self.right

        exchange: None | str | Unset
        if isinstance(self.exchange, Unset):
            exchange = UNSET
        else:
            exchange = self.exchange

        currency: None | str | Unset
        if isinstance(self.currency, Unset):
            currency = UNSET
        else:
            currency = self.currency

        multiplier: None | str | Unset
        if isinstance(self.multiplier, Unset):
            multiplier = UNSET
        else:
            multiplier = self.multiplier

        trading_class: None | str | Unset
        if isinstance(self.trading_class, Unset):
            trading_class = UNSET
        else:
            trading_class = self.trading_class

        primary_exchange: None | str | Unset
        if isinstance(self.primary_exchange, Unset):
            primary_exchange = UNSET
        else:
            primary_exchange = self.primary_exchange

        conid: int | None | Unset
        if isinstance(self.conid, Unset):
            conid = UNSET
        else:
            conid = self.conid

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

        account: None | str | Unset
        if isinstance(self.account, Unset):
            account = UNSET
        else:
            account = self.account

        good_after_time: None | str | Unset
        if isinstance(self.good_after_time, Unset):
            good_after_time = UNSET
        else:
            good_after_time = self.good_after_time

        good_till_date: None | str | Unset
        if isinstance(self.good_till_date, Unset):
            good_till_date = UNSET
        else:
            good_till_date = self.good_till_date

        oca_group: None | str | Unset
        if isinstance(self.oca_group, Unset):
            oca_group = UNSET
        else:
            oca_group = self.oca_group

        parent_id: int | None | Unset
        if isinstance(self.parent_id, Unset):
            parent_id = UNSET
        else:
            parent_id = self.parent_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "assetClass": asset_class,
                "symbol": symbol,
                "action": action,
                "quantity": quantity,
            }
        )
        if expiry is not UNSET:
            field_dict["expiry"] = expiry
        if strike is not UNSET:
            field_dict["strike"] = strike
        if right is not UNSET:
            field_dict["right"] = right
        if exchange is not UNSET:
            field_dict["exchange"] = exchange
        if currency is not UNSET:
            field_dict["currency"] = currency
        if multiplier is not UNSET:
            field_dict["multiplier"] = multiplier
        if trading_class is not UNSET:
            field_dict["tradingClass"] = trading_class
        if primary_exchange is not UNSET:
            field_dict["primaryExchange"] = primary_exchange
        if conid is not UNSET:
            field_dict["conid"] = conid
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
        if good_after_time is not UNSET:
            field_dict["goodAfterTime"] = good_after_time
        if good_till_date is not UNSET:
            field_dict["goodTillDate"] = good_till_date
        if oca_group is not UNSET:
            field_dict["ocaGroup"] = oca_group
        if parent_id is not UNSET:
            field_dict["parentId"] = parent_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        asset_class = d.pop("assetClass")

        symbol = d.pop("symbol")

        action = d.pop("action")

        quantity = d.pop("quantity")

        def _parse_expiry(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        expiry = _parse_expiry(d.pop("expiry", UNSET))

        def _parse_strike(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        strike = _parse_strike(d.pop("strike", UNSET))

        def _parse_right(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        right = _parse_right(d.pop("right", UNSET))

        def _parse_exchange(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        exchange = _parse_exchange(d.pop("exchange", UNSET))

        def _parse_currency(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        currency = _parse_currency(d.pop("currency", UNSET))

        def _parse_multiplier(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        multiplier = _parse_multiplier(d.pop("multiplier", UNSET))

        def _parse_trading_class(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        trading_class = _parse_trading_class(d.pop("tradingClass", UNSET))

        def _parse_primary_exchange(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        primary_exchange = _parse_primary_exchange(d.pop("primaryExchange", UNSET))

        def _parse_conid(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        conid = _parse_conid(d.pop("conid", UNSET))

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

        def _parse_account(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        account = _parse_account(d.pop("account", UNSET))

        def _parse_good_after_time(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        good_after_time = _parse_good_after_time(d.pop("goodAfterTime", UNSET))

        def _parse_good_till_date(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        good_till_date = _parse_good_till_date(d.pop("goodTillDate", UNSET))

        def _parse_oca_group(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        oca_group = _parse_oca_group(d.pop("ocaGroup", UNSET))

        def _parse_parent_id(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        parent_id = _parse_parent_id(d.pop("parentId", UNSET))

        order_request = cls(
            asset_class=asset_class,
            symbol=symbol,
            action=action,
            quantity=quantity,
            expiry=expiry,
            strike=strike,
            right=right,
            exchange=exchange,
            currency=currency,
            multiplier=multiplier,
            trading_class=trading_class,
            primary_exchange=primary_exchange,
            conid=conid,
            order_type=order_type,
            lmt_price=lmt_price,
            aux_price=aux_price,
            tif=tif,
            outside_rth=outside_rth,
            transmit=transmit,
            account=account,
            good_after_time=good_after_time,
            good_till_date=good_till_date,
            oca_group=oca_group,
            parent_id=parent_id,
        )

        order_request.additional_properties = d
        return order_request

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
