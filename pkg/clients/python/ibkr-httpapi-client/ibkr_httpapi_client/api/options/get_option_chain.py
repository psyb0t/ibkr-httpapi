from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error_envelope import ErrorEnvelope
from ...models.option_chain import OptionChain
from ...types import UNSET, Response, Unset


def _get_kwargs(
    symbol: str,
    *,
    underlying_sec_type: str | Unset = "STK",
    fut_fop_exchange: str | Unset = "",
    underlying_con_id: int | None | Unset = UNSET,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    params["underlyingSecType"] = underlying_sec_type

    params["futFopExchange"] = fut_fop_exchange

    json_underlying_con_id: int | None | Unset
    if isinstance(underlying_con_id, Unset):
        json_underlying_con_id = UNSET
    else:
        json_underlying_con_id = underlying_con_id
    params["underlyingConId"] = json_underlying_con_id

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/options/{symbol}/chain".format(
            symbol=quote(str(symbol), safe=""),
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ErrorEnvelope | OptionChain | None:
    if response.status_code == 200:
        response_200 = OptionChain.from_dict(response.json())

        return response_200

    if response.status_code == 404:
        response_404 = ErrorEnvelope.from_dict(response.json())

        return response_404

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[ErrorEnvelope | OptionChain]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    symbol: str,
    *,
    client: AuthenticatedClient | Client,
    underlying_sec_type: str | Unset = "STK",
    fut_fop_exchange: str | Unset = "",
    underlying_con_id: int | None | Unset = UNSET,
) -> Response[ErrorEnvelope | OptionChain]:
    """Full option chain (every expiry × strike per exchange).

    Args:
        symbol (str):
        underlying_sec_type (str | Unset):  Default: 'STK'.
        fut_fop_exchange (str | Unset):  Default: ''.
        underlying_con_id (int | None | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorEnvelope | OptionChain]
    """

    kwargs = _get_kwargs(
        symbol=symbol,
        underlying_sec_type=underlying_sec_type,
        fut_fop_exchange=fut_fop_exchange,
        underlying_con_id=underlying_con_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    symbol: str,
    *,
    client: AuthenticatedClient | Client,
    underlying_sec_type: str | Unset = "STK",
    fut_fop_exchange: str | Unset = "",
    underlying_con_id: int | None | Unset = UNSET,
) -> ErrorEnvelope | OptionChain | None:
    """Full option chain (every expiry × strike per exchange).

    Args:
        symbol (str):
        underlying_sec_type (str | Unset):  Default: 'STK'.
        fut_fop_exchange (str | Unset):  Default: ''.
        underlying_con_id (int | None | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorEnvelope | OptionChain
    """

    return sync_detailed(
        symbol=symbol,
        client=client,
        underlying_sec_type=underlying_sec_type,
        fut_fop_exchange=fut_fop_exchange,
        underlying_con_id=underlying_con_id,
    ).parsed


async def asyncio_detailed(
    symbol: str,
    *,
    client: AuthenticatedClient | Client,
    underlying_sec_type: str | Unset = "STK",
    fut_fop_exchange: str | Unset = "",
    underlying_con_id: int | None | Unset = UNSET,
) -> Response[ErrorEnvelope | OptionChain]:
    """Full option chain (every expiry × strike per exchange).

    Args:
        symbol (str):
        underlying_sec_type (str | Unset):  Default: 'STK'.
        fut_fop_exchange (str | Unset):  Default: ''.
        underlying_con_id (int | None | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorEnvelope | OptionChain]
    """

    kwargs = _get_kwargs(
        symbol=symbol,
        underlying_sec_type=underlying_sec_type,
        fut_fop_exchange=fut_fop_exchange,
        underlying_con_id=underlying_con_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    symbol: str,
    *,
    client: AuthenticatedClient | Client,
    underlying_sec_type: str | Unset = "STK",
    fut_fop_exchange: str | Unset = "",
    underlying_con_id: int | None | Unset = UNSET,
) -> ErrorEnvelope | OptionChain | None:
    """Full option chain (every expiry × strike per exchange).

    Args:
        symbol (str):
        underlying_sec_type (str | Unset):  Default: 'STK'.
        fut_fop_exchange (str | Unset):  Default: ''.
        underlying_con_id (int | None | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorEnvelope | OptionChain
    """

    return (
        await asyncio_detailed(
            symbol=symbol,
            client=client,
            underlying_sec_type=underlying_sec_type,
            fut_fop_exchange=fut_fop_exchange,
            underlying_con_id=underlying_con_id,
        )
    ).parsed
