from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error_envelope import ErrorEnvelope
from ...models.executions_response import ExecutionsResponse
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    account: None | str | Unset = UNSET,
    client_id: int | None | Unset = UNSET,
    sec_type: None | str | Unset = UNSET,
    symbol: None | str | Unset = UNSET,
    exchange: None | str | Unset = UNSET,
    side: None | str | Unset = UNSET,
    time_after: None | str | Unset = UNSET,
    refresh: bool | Unset = False,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    json_account: None | str | Unset
    if isinstance(account, Unset):
        json_account = UNSET
    else:
        json_account = account
    params["account"] = json_account

    json_client_id: int | None | Unset
    if isinstance(client_id, Unset):
        json_client_id = UNSET
    else:
        json_client_id = client_id
    params["clientId"] = json_client_id

    json_sec_type: None | str | Unset
    if isinstance(sec_type, Unset):
        json_sec_type = UNSET
    else:
        json_sec_type = sec_type
    params["secType"] = json_sec_type

    json_symbol: None | str | Unset
    if isinstance(symbol, Unset):
        json_symbol = UNSET
    else:
        json_symbol = symbol
    params["symbol"] = json_symbol

    json_exchange: None | str | Unset
    if isinstance(exchange, Unset):
        json_exchange = UNSET
    else:
        json_exchange = exchange
    params["exchange"] = json_exchange

    json_side: None | str | Unset
    if isinstance(side, Unset):
        json_side = UNSET
    else:
        json_side = side
    params["side"] = json_side

    json_time_after: None | str | Unset
    if isinstance(time_after, Unset):
        json_time_after = UNSET
    else:
        json_time_after = time_after
    params["timeAfter"] = json_time_after

    params["refresh"] = refresh

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/history/executions",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ErrorEnvelope | ExecutionsResponse | None:
    if response.status_code == 200:
        response_200 = ExecutionsResponse.from_dict(response.json())

        return response_200

    if response.status_code == 429:
        response_429 = ErrorEnvelope.from_dict(response.json())

        return response_429

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[ErrorEnvelope | ExecutionsResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    account: None | str | Unset = UNSET,
    client_id: int | None | Unset = UNSET,
    sec_type: None | str | Unset = UNSET,
    symbol: None | str | Unset = UNSET,
    exchange: None | str | Unset = UNSET,
    side: None | str | Unset = UNSET,
    time_after: None | str | Unset = UNSET,
    refresh: bool | Unset = False,
) -> Response[ErrorEnvelope | ExecutionsResponse]:
    """Today's executions (broker-side fills feed).

    Args:
        account (None | str | Unset):
        client_id (int | None | Unset):
        sec_type (None | str | Unset):
        symbol (None | str | Unset):
        exchange (None | str | Unset):
        side (None | str | Unset):
        time_after (None | str | Unset): 'YYYYMMDD HH:MM:SS' UTC
        refresh (bool | Unset):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorEnvelope | ExecutionsResponse]
    """

    kwargs = _get_kwargs(
        account=account,
        client_id=client_id,
        sec_type=sec_type,
        symbol=symbol,
        exchange=exchange,
        side=side,
        time_after=time_after,
        refresh=refresh,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    account: None | str | Unset = UNSET,
    client_id: int | None | Unset = UNSET,
    sec_type: None | str | Unset = UNSET,
    symbol: None | str | Unset = UNSET,
    exchange: None | str | Unset = UNSET,
    side: None | str | Unset = UNSET,
    time_after: None | str | Unset = UNSET,
    refresh: bool | Unset = False,
) -> ErrorEnvelope | ExecutionsResponse | None:
    """Today's executions (broker-side fills feed).

    Args:
        account (None | str | Unset):
        client_id (int | None | Unset):
        sec_type (None | str | Unset):
        symbol (None | str | Unset):
        exchange (None | str | Unset):
        side (None | str | Unset):
        time_after (None | str | Unset): 'YYYYMMDD HH:MM:SS' UTC
        refresh (bool | Unset):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorEnvelope | ExecutionsResponse
    """

    return sync_detailed(
        client=client,
        account=account,
        client_id=client_id,
        sec_type=sec_type,
        symbol=symbol,
        exchange=exchange,
        side=side,
        time_after=time_after,
        refresh=refresh,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    account: None | str | Unset = UNSET,
    client_id: int | None | Unset = UNSET,
    sec_type: None | str | Unset = UNSET,
    symbol: None | str | Unset = UNSET,
    exchange: None | str | Unset = UNSET,
    side: None | str | Unset = UNSET,
    time_after: None | str | Unset = UNSET,
    refresh: bool | Unset = False,
) -> Response[ErrorEnvelope | ExecutionsResponse]:
    """Today's executions (broker-side fills feed).

    Args:
        account (None | str | Unset):
        client_id (int | None | Unset):
        sec_type (None | str | Unset):
        symbol (None | str | Unset):
        exchange (None | str | Unset):
        side (None | str | Unset):
        time_after (None | str | Unset): 'YYYYMMDD HH:MM:SS' UTC
        refresh (bool | Unset):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorEnvelope | ExecutionsResponse]
    """

    kwargs = _get_kwargs(
        account=account,
        client_id=client_id,
        sec_type=sec_type,
        symbol=symbol,
        exchange=exchange,
        side=side,
        time_after=time_after,
        refresh=refresh,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    account: None | str | Unset = UNSET,
    client_id: int | None | Unset = UNSET,
    sec_type: None | str | Unset = UNSET,
    symbol: None | str | Unset = UNSET,
    exchange: None | str | Unset = UNSET,
    side: None | str | Unset = UNSET,
    time_after: None | str | Unset = UNSET,
    refresh: bool | Unset = False,
) -> ErrorEnvelope | ExecutionsResponse | None:
    """Today's executions (broker-side fills feed).

    Args:
        account (None | str | Unset):
        client_id (int | None | Unset):
        sec_type (None | str | Unset):
        symbol (None | str | Unset):
        exchange (None | str | Unset):
        side (None | str | Unset):
        time_after (None | str | Unset): 'YYYYMMDD HH:MM:SS' UTC
        refresh (bool | Unset):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorEnvelope | ExecutionsResponse
    """

    return (
        await asyncio_detailed(
            client=client,
            account=account,
            client_id=client_id,
            sec_type=sec_type,
            symbol=symbol,
            exchange=exchange,
            side=side,
            time_after=time_after,
            refresh=refresh,
        )
    ).parsed
