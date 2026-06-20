from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PingResponse")


@_attrs_define
class PingResponse:
    """
    Attributes:
        status (str):
        connected (bool):
        server_version (int | None | Unset):
        start_time (None | str | Unset):
        uptime_seconds (float | None | Unset):
        msgs_sent (int | None | Unset):
        msgs_recv (int | None | Unset):
    """

    status: str
    connected: bool
    server_version: int | None | Unset = UNSET
    start_time: None | str | Unset = UNSET
    uptime_seconds: float | None | Unset = UNSET
    msgs_sent: int | None | Unset = UNSET
    msgs_recv: int | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        status = self.status

        connected = self.connected

        server_version: int | None | Unset
        if isinstance(self.server_version, Unset):
            server_version = UNSET
        else:
            server_version = self.server_version

        start_time: None | str | Unset
        if isinstance(self.start_time, Unset):
            start_time = UNSET
        else:
            start_time = self.start_time

        uptime_seconds: float | None | Unset
        if isinstance(self.uptime_seconds, Unset):
            uptime_seconds = UNSET
        else:
            uptime_seconds = self.uptime_seconds

        msgs_sent: int | None | Unset
        if isinstance(self.msgs_sent, Unset):
            msgs_sent = UNSET
        else:
            msgs_sent = self.msgs_sent

        msgs_recv: int | None | Unset
        if isinstance(self.msgs_recv, Unset):
            msgs_recv = UNSET
        else:
            msgs_recv = self.msgs_recv

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "status": status,
                "connected": connected,
            }
        )
        if server_version is not UNSET:
            field_dict["serverVersion"] = server_version
        if start_time is not UNSET:
            field_dict["startTime"] = start_time
        if uptime_seconds is not UNSET:
            field_dict["uptimeSeconds"] = uptime_seconds
        if msgs_sent is not UNSET:
            field_dict["msgsSent"] = msgs_sent
        if msgs_recv is not UNSET:
            field_dict["msgsRecv"] = msgs_recv

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        status = d.pop("status")

        connected = d.pop("connected")

        def _parse_server_version(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        server_version = _parse_server_version(d.pop("serverVersion", UNSET))

        def _parse_start_time(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        start_time = _parse_start_time(d.pop("startTime", UNSET))

        def _parse_uptime_seconds(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        uptime_seconds = _parse_uptime_seconds(d.pop("uptimeSeconds", UNSET))

        def _parse_msgs_sent(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        msgs_sent = _parse_msgs_sent(d.pop("msgsSent", UNSET))

        def _parse_msgs_recv(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        msgs_recv = _parse_msgs_recv(d.pop("msgsRecv", UNSET))

        ping_response = cls(
            status=status,
            connected=connected,
            server_version=server_version,
            start_time=start_time,
            uptime_seconds=uptime_seconds,
            msgs_sent=msgs_sent,
            msgs_recv=msgs_recv,
        )

        ping_response.additional_properties = d
        return ping_response

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
