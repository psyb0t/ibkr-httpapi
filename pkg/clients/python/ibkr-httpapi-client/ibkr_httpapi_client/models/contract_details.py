from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.contract import Contract


T = TypeVar("T", bound="ContractDetails")


@_attrs_define
class ContractDetails:
    """
    Attributes:
        contract (Contract):
        market_name (str | Unset):
        min_tick (float | Unset):
        order_types (list[str] | Unset):
        valid_exchanges (list[str] | Unset):
        price_magnifier (int | Unset):
        long_name (str | Unset):
        industry (str | Unset):
        category (str | Unset):
        subcategory (str | Unset):
        time_zone_id (str | Unset):
        trading_hours (str | Unset):
        liquid_hours (str | Unset):
        ev_rule (str | Unset):
        ev_multiplier (float | Unset):
    """

    contract: Contract
    market_name: str | Unset = UNSET
    min_tick: float | Unset = UNSET
    order_types: list[str] | Unset = UNSET
    valid_exchanges: list[str] | Unset = UNSET
    price_magnifier: int | Unset = UNSET
    long_name: str | Unset = UNSET
    industry: str | Unset = UNSET
    category: str | Unset = UNSET
    subcategory: str | Unset = UNSET
    time_zone_id: str | Unset = UNSET
    trading_hours: str | Unset = UNSET
    liquid_hours: str | Unset = UNSET
    ev_rule: str | Unset = UNSET
    ev_multiplier: float | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        contract = self.contract.to_dict()

        market_name = self.market_name

        min_tick = self.min_tick

        order_types: list[str] | Unset = UNSET
        if not isinstance(self.order_types, Unset):
            order_types = self.order_types

        valid_exchanges: list[str] | Unset = UNSET
        if not isinstance(self.valid_exchanges, Unset):
            valid_exchanges = self.valid_exchanges

        price_magnifier = self.price_magnifier

        long_name = self.long_name

        industry = self.industry

        category = self.category

        subcategory = self.subcategory

        time_zone_id = self.time_zone_id

        trading_hours = self.trading_hours

        liquid_hours = self.liquid_hours

        ev_rule = self.ev_rule

        ev_multiplier = self.ev_multiplier

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "contract": contract,
            }
        )
        if market_name is not UNSET:
            field_dict["marketName"] = market_name
        if min_tick is not UNSET:
            field_dict["minTick"] = min_tick
        if order_types is not UNSET:
            field_dict["orderTypes"] = order_types
        if valid_exchanges is not UNSET:
            field_dict["validExchanges"] = valid_exchanges
        if price_magnifier is not UNSET:
            field_dict["priceMagnifier"] = price_magnifier
        if long_name is not UNSET:
            field_dict["longName"] = long_name
        if industry is not UNSET:
            field_dict["industry"] = industry
        if category is not UNSET:
            field_dict["category"] = category
        if subcategory is not UNSET:
            field_dict["subcategory"] = subcategory
        if time_zone_id is not UNSET:
            field_dict["timeZoneId"] = time_zone_id
        if trading_hours is not UNSET:
            field_dict["tradingHours"] = trading_hours
        if liquid_hours is not UNSET:
            field_dict["liquidHours"] = liquid_hours
        if ev_rule is not UNSET:
            field_dict["evRule"] = ev_rule
        if ev_multiplier is not UNSET:
            field_dict["evMultiplier"] = ev_multiplier

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.contract import Contract

        d = dict(src_dict)
        contract = Contract.from_dict(d.pop("contract"))

        market_name = d.pop("marketName", UNSET)

        min_tick = d.pop("minTick", UNSET)

        order_types = cast(list[str], d.pop("orderTypes", UNSET))

        valid_exchanges = cast(list[str], d.pop("validExchanges", UNSET))

        price_magnifier = d.pop("priceMagnifier", UNSET)

        long_name = d.pop("longName", UNSET)

        industry = d.pop("industry", UNSET)

        category = d.pop("category", UNSET)

        subcategory = d.pop("subcategory", UNSET)

        time_zone_id = d.pop("timeZoneId", UNSET)

        trading_hours = d.pop("tradingHours", UNSET)

        liquid_hours = d.pop("liquidHours", UNSET)

        ev_rule = d.pop("evRule", UNSET)

        ev_multiplier = d.pop("evMultiplier", UNSET)

        contract_details = cls(
            contract=contract,
            market_name=market_name,
            min_tick=min_tick,
            order_types=order_types,
            valid_exchanges=valid_exchanges,
            price_magnifier=price_magnifier,
            long_name=long_name,
            industry=industry,
            category=category,
            subcategory=subcategory,
            time_zone_id=time_zone_id,
            trading_hours=trading_hours,
            liquid_hours=liquid_hours,
            ev_rule=ev_rule,
            ev_multiplier=ev_multiplier,
        )

        contract_details.additional_properties = d
        return contract_details

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
