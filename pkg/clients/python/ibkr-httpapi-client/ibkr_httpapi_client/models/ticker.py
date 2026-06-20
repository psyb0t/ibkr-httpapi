from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.contract import Contract
    from ..models.greeks import Greeks


T = TypeVar("T", bound="Ticker")


@_attrs_define
class Ticker:
    """
    Attributes:
        contract (Contract):
        time (None | str | Unset):
        bid (float | None | Unset):
        bid_size (float | None | Unset):
        ask (float | None | Unset):
        ask_size (float | None | Unset):
        last (float | None | Unset):
        last_size (float | None | Unset):
        close (float | None | Unset):
        open_ (float | None | Unset):
        high (float | None | Unset):
        low (float | None | Unset):
        volume (float | None | Unset):
        vwap (float | None | Unset):
        halted (float | None | Unset):
        model_greeks (Greeks | None | Unset):
        bid_greeks (Greeks | None | Unset):
        ask_greeks (Greeks | None | Unset):
        last_greeks (Greeks | None | Unset):
    """

    contract: Contract
    time: None | str | Unset = UNSET
    bid: float | None | Unset = UNSET
    bid_size: float | None | Unset = UNSET
    ask: float | None | Unset = UNSET
    ask_size: float | None | Unset = UNSET
    last: float | None | Unset = UNSET
    last_size: float | None | Unset = UNSET
    close: float | None | Unset = UNSET
    open_: float | None | Unset = UNSET
    high: float | None | Unset = UNSET
    low: float | None | Unset = UNSET
    volume: float | None | Unset = UNSET
    vwap: float | None | Unset = UNSET
    halted: float | None | Unset = UNSET
    model_greeks: Greeks | None | Unset = UNSET
    bid_greeks: Greeks | None | Unset = UNSET
    ask_greeks: Greeks | None | Unset = UNSET
    last_greeks: Greeks | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.greeks import Greeks

        contract = self.contract.to_dict()

        time: None | str | Unset
        if isinstance(self.time, Unset):
            time = UNSET
        else:
            time = self.time

        bid: float | None | Unset
        if isinstance(self.bid, Unset):
            bid = UNSET
        else:
            bid = self.bid

        bid_size: float | None | Unset
        if isinstance(self.bid_size, Unset):
            bid_size = UNSET
        else:
            bid_size = self.bid_size

        ask: float | None | Unset
        if isinstance(self.ask, Unset):
            ask = UNSET
        else:
            ask = self.ask

        ask_size: float | None | Unset
        if isinstance(self.ask_size, Unset):
            ask_size = UNSET
        else:
            ask_size = self.ask_size

        last: float | None | Unset
        if isinstance(self.last, Unset):
            last = UNSET
        else:
            last = self.last

        last_size: float | None | Unset
        if isinstance(self.last_size, Unset):
            last_size = UNSET
        else:
            last_size = self.last_size

        close: float | None | Unset
        if isinstance(self.close, Unset):
            close = UNSET
        else:
            close = self.close

        open_: float | None | Unset
        if isinstance(self.open_, Unset):
            open_ = UNSET
        else:
            open_ = self.open_

        high: float | None | Unset
        if isinstance(self.high, Unset):
            high = UNSET
        else:
            high = self.high

        low: float | None | Unset
        if isinstance(self.low, Unset):
            low = UNSET
        else:
            low = self.low

        volume: float | None | Unset
        if isinstance(self.volume, Unset):
            volume = UNSET
        else:
            volume = self.volume

        vwap: float | None | Unset
        if isinstance(self.vwap, Unset):
            vwap = UNSET
        else:
            vwap = self.vwap

        halted: float | None | Unset
        if isinstance(self.halted, Unset):
            halted = UNSET
        else:
            halted = self.halted

        model_greeks: dict[str, Any] | None | Unset
        if isinstance(self.model_greeks, Unset):
            model_greeks = UNSET
        elif isinstance(self.model_greeks, Greeks):
            model_greeks = self.model_greeks.to_dict()
        else:
            model_greeks = self.model_greeks

        bid_greeks: dict[str, Any] | None | Unset
        if isinstance(self.bid_greeks, Unset):
            bid_greeks = UNSET
        elif isinstance(self.bid_greeks, Greeks):
            bid_greeks = self.bid_greeks.to_dict()
        else:
            bid_greeks = self.bid_greeks

        ask_greeks: dict[str, Any] | None | Unset
        if isinstance(self.ask_greeks, Unset):
            ask_greeks = UNSET
        elif isinstance(self.ask_greeks, Greeks):
            ask_greeks = self.ask_greeks.to_dict()
        else:
            ask_greeks = self.ask_greeks

        last_greeks: dict[str, Any] | None | Unset
        if isinstance(self.last_greeks, Unset):
            last_greeks = UNSET
        elif isinstance(self.last_greeks, Greeks):
            last_greeks = self.last_greeks.to_dict()
        else:
            last_greeks = self.last_greeks

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "contract": contract,
            }
        )
        if time is not UNSET:
            field_dict["time"] = time
        if bid is not UNSET:
            field_dict["bid"] = bid
        if bid_size is not UNSET:
            field_dict["bidSize"] = bid_size
        if ask is not UNSET:
            field_dict["ask"] = ask
        if ask_size is not UNSET:
            field_dict["askSize"] = ask_size
        if last is not UNSET:
            field_dict["last"] = last
        if last_size is not UNSET:
            field_dict["lastSize"] = last_size
        if close is not UNSET:
            field_dict["close"] = close
        if open_ is not UNSET:
            field_dict["open"] = open_
        if high is not UNSET:
            field_dict["high"] = high
        if low is not UNSET:
            field_dict["low"] = low
        if volume is not UNSET:
            field_dict["volume"] = volume
        if vwap is not UNSET:
            field_dict["vwap"] = vwap
        if halted is not UNSET:
            field_dict["halted"] = halted
        if model_greeks is not UNSET:
            field_dict["modelGreeks"] = model_greeks
        if bid_greeks is not UNSET:
            field_dict["bidGreeks"] = bid_greeks
        if ask_greeks is not UNSET:
            field_dict["askGreeks"] = ask_greeks
        if last_greeks is not UNSET:
            field_dict["lastGreeks"] = last_greeks

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.contract import Contract
        from ..models.greeks import Greeks

        d = dict(src_dict)
        contract = Contract.from_dict(d.pop("contract"))

        def _parse_time(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        time = _parse_time(d.pop("time", UNSET))

        def _parse_bid(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        bid = _parse_bid(d.pop("bid", UNSET))

        def _parse_bid_size(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        bid_size = _parse_bid_size(d.pop("bidSize", UNSET))

        def _parse_ask(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        ask = _parse_ask(d.pop("ask", UNSET))

        def _parse_ask_size(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        ask_size = _parse_ask_size(d.pop("askSize", UNSET))

        def _parse_last(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        last = _parse_last(d.pop("last", UNSET))

        def _parse_last_size(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        last_size = _parse_last_size(d.pop("lastSize", UNSET))

        def _parse_close(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        close = _parse_close(d.pop("close", UNSET))

        def _parse_open_(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        open_ = _parse_open_(d.pop("open", UNSET))

        def _parse_high(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        high = _parse_high(d.pop("high", UNSET))

        def _parse_low(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        low = _parse_low(d.pop("low", UNSET))

        def _parse_volume(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        volume = _parse_volume(d.pop("volume", UNSET))

        def _parse_vwap(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        vwap = _parse_vwap(d.pop("vwap", UNSET))

        def _parse_halted(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        halted = _parse_halted(d.pop("halted", UNSET))

        def _parse_model_greeks(data: object) -> Greeks | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                model_greeks_type_1 = Greeks.from_dict(data)

                return model_greeks_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(Greeks | None | Unset, data)

        model_greeks = _parse_model_greeks(d.pop("modelGreeks", UNSET))

        def _parse_bid_greeks(data: object) -> Greeks | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                bid_greeks_type_1 = Greeks.from_dict(data)

                return bid_greeks_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(Greeks | None | Unset, data)

        bid_greeks = _parse_bid_greeks(d.pop("bidGreeks", UNSET))

        def _parse_ask_greeks(data: object) -> Greeks | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                ask_greeks_type_1 = Greeks.from_dict(data)

                return ask_greeks_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(Greeks | None | Unset, data)

        ask_greeks = _parse_ask_greeks(d.pop("askGreeks", UNSET))

        def _parse_last_greeks(data: object) -> Greeks | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                last_greeks_type_1 = Greeks.from_dict(data)

                return last_greeks_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(Greeks | None | Unset, data)

        last_greeks = _parse_last_greeks(d.pop("lastGreeks", UNSET))

        ticker = cls(
            contract=contract,
            time=time,
            bid=bid,
            bid_size=bid_size,
            ask=ask,
            ask_size=ask_size,
            last=last,
            last_size=last_size,
            close=close,
            open_=open_,
            high=high,
            low=low,
            volume=volume,
            vwap=vwap,
            halted=halted,
            model_greeks=model_greeks,
            bid_greeks=bid_greeks,
            ask_greeks=ask_greeks,
            last_greeks=last_greeks,
        )

        ticker.additional_properties = d
        return ticker

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
