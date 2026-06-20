from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.ticker import Ticker
from ...types import UNSET, Response, Unset


def _get_kwargs(
    symbol: str,
    *,
    exchange: None | str | Unset = UNSET,
    currency: None | str | Unset = UNSET,
    primary_exchange: None | str | Unset = UNSET,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    json_exchange: None | str | Unset
    if isinstance(exchange, Unset):
        json_exchange = UNSET
    else:
        json_exchange = exchange
    params["exchange"] = json_exchange

    json_currency: None | str | Unset
    if isinstance(currency, Unset):
        json_currency = UNSET
    else:
        json_currency = currency
    params["currency"] = json_currency

    json_primary_exchange: None | str | Unset
    if isinstance(primary_exchange, Unset):
        json_primary_exchange = UNSET
    else:
        json_primary_exchange = primary_exchange
    params["primaryExchange"] = json_primary_exchange

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/stocks/{symbol}/tick".format(
            symbol=quote(str(symbol), safe=""),
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Ticker | None:
    if response.status_code == 200:
        response_200 = Ticker.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[Ticker]:
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
    exchange: None | str | Unset = UNSET,
    currency: None | str | Unset = UNSET,
    primary_exchange: None | str | Unset = UNSET,
) -> Response[Ticker]:
    """Snapshot tick (bid/ask/last + volume/OHLC for the session).

    Args:
        symbol (str):
        exchange (None | str | Unset):
        currency (None | str | Unset):
        primary_exchange (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Ticker]
    """

    kwargs = _get_kwargs(
        symbol=symbol,
        exchange=exchange,
        currency=currency,
        primary_exchange=primary_exchange,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    symbol: str,
    *,
    client: AuthenticatedClient | Client,
    exchange: None | str | Unset = UNSET,
    currency: None | str | Unset = UNSET,
    primary_exchange: None | str | Unset = UNSET,
) -> Ticker | None:
    """Snapshot tick (bid/ask/last + volume/OHLC for the session).

    Args:
        symbol (str):
        exchange (None | str | Unset):
        currency (None | str | Unset):
        primary_exchange (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Ticker
    """

    return sync_detailed(
        symbol=symbol,
        client=client,
        exchange=exchange,
        currency=currency,
        primary_exchange=primary_exchange,
    ).parsed


async def asyncio_detailed(
    symbol: str,
    *,
    client: AuthenticatedClient | Client,
    exchange: None | str | Unset = UNSET,
    currency: None | str | Unset = UNSET,
    primary_exchange: None | str | Unset = UNSET,
) -> Response[Ticker]:
    """Snapshot tick (bid/ask/last + volume/OHLC for the session).

    Args:
        symbol (str):
        exchange (None | str | Unset):
        currency (None | str | Unset):
        primary_exchange (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Ticker]
    """

    kwargs = _get_kwargs(
        symbol=symbol,
        exchange=exchange,
        currency=currency,
        primary_exchange=primary_exchange,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    symbol: str,
    *,
    client: AuthenticatedClient | Client,
    exchange: None | str | Unset = UNSET,
    currency: None | str | Unset = UNSET,
    primary_exchange: None | str | Unset = UNSET,
) -> Ticker | None:
    """Snapshot tick (bid/ask/last + volume/OHLC for the session).

    Args:
        symbol (str):
        exchange (None | str | Unset):
        currency (None | str | Unset):
        primary_exchange (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Ticker
    """

    return (
        await asyncio_detailed(
            symbol=symbol,
            client=client,
            exchange=exchange,
            currency=currency,
            primary_exchange=primary_exchange,
        )
    ).parsed
