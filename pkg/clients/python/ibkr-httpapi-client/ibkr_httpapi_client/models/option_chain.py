from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.option_chain_entry import OptionChainEntry


T = TypeVar("T", bound="OptionChain")


@_attrs_define
class OptionChain:
    """
    Attributes:
        symbol (str):
        chains (list[OptionChainEntry]):
        underlying_con_id (int | None | Unset):
    """

    symbol: str
    chains: list[OptionChainEntry]
    underlying_con_id: int | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        symbol = self.symbol

        chains = []
        for chains_item_data in self.chains:
            chains_item = chains_item_data.to_dict()
            chains.append(chains_item)

        underlying_con_id: int | None | Unset
        if isinstance(self.underlying_con_id, Unset):
            underlying_con_id = UNSET
        else:
            underlying_con_id = self.underlying_con_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "symbol": symbol,
                "chains": chains,
            }
        )
        if underlying_con_id is not UNSET:
            field_dict["underlyingConId"] = underlying_con_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.option_chain_entry import OptionChainEntry

        d = dict(src_dict)
        symbol = d.pop("symbol")

        chains = []
        _chains = d.pop("chains")
        for chains_item_data in _chains:
            chains_item = OptionChainEntry.from_dict(chains_item_data)

            chains.append(chains_item)

        def _parse_underlying_con_id(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        underlying_con_id = _parse_underlying_con_id(d.pop("underlyingConId", UNSET))

        option_chain = cls(
            symbol=symbol,
            chains=chains,
            underlying_con_id=underlying_con_id,
        )

        option_chain.additional_properties = d
        return option_chain

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
