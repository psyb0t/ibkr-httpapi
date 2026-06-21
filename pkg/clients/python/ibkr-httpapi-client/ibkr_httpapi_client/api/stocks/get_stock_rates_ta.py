from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error_envelope import ErrorEnvelope
from ...models.rates_ta_request import RatesTARequest
from ...models.rates_ta_response import RatesTAResponse
from ...types import UNSET, Response, Unset


def _get_kwargs(
    symbol: str,
    *,
    body: RatesTARequest,
    exchange: None | str | Unset = UNSET,
    currency: None | str | Unset = UNSET,
    primary_exchange: None | str | Unset = UNSET,
    refresh: bool | Unset = False,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

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

    params["refresh"] = refresh

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/stocks/{symbol}/rates/ta".format(
            symbol=quote(str(symbol), safe=""),
        ),
        "params": params,
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ErrorEnvelope | RatesTAResponse | None:
    if response.status_code == 200:
        response_200 = RatesTAResponse.from_dict(response.json())

        return response_200

    if response.status_code == 429:
        response_429 = ErrorEnvelope.from_dict(response.json())

        return response_429

    if response.status_code == 503:
        response_503 = ErrorEnvelope.from_dict(response.json())

        return response_503

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[ErrorEnvelope | RatesTAResponse]:
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
    body: RatesTARequest,
    exchange: None | str | Unset = UNSET,
    currency: None | str | Unset = UNSET,
    primary_exchange: None | str | Unset = UNSET,
    refresh: bool | Unset = False,
) -> Response[ErrorEnvelope | RatesTAResponse]:
    """Bars + wickworks TA enrichment.

    Args:
        symbol (str):
        exchange (None | str | Unset):
        currency (None | str | Unset):
        primary_exchange (None | str | Unset):
        refresh (bool | Unset):  Default: False.
        body (RatesTARequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorEnvelope | RatesTAResponse]
    """

    kwargs = _get_kwargs(
        symbol=symbol,
        body=body,
        exchange=exchange,
        currency=currency,
        primary_exchange=primary_exchange,
        refresh=refresh,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    symbol: str,
    *,
    client: AuthenticatedClient | Client,
    body: RatesTARequest,
    exchange: None | str | Unset = UNSET,
    currency: None | str | Unset = UNSET,
    primary_exchange: None | str | Unset = UNSET,
    refresh: bool | Unset = False,
) -> ErrorEnvelope | RatesTAResponse | None:
    """Bars + wickworks TA enrichment.

    Args:
        symbol (str):
        exchange (None | str | Unset):
        currency (None | str | Unset):
        primary_exchange (None | str | Unset):
        refresh (bool | Unset):  Default: False.
        body (RatesTARequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorEnvelope | RatesTAResponse
    """

    return sync_detailed(
        symbol=symbol,
        client=client,
        body=body,
        exchange=exchange,
        currency=currency,
        primary_exchange=primary_exchange,
        refresh=refresh,
    ).parsed


async def asyncio_detailed(
    symbol: str,
    *,
    client: AuthenticatedClient | Client,
    body: RatesTARequest,
    exchange: None | str | Unset = UNSET,
    currency: None | str | Unset = UNSET,
    primary_exchange: None | str | Unset = UNSET,
    refresh: bool | Unset = False,
) -> Response[ErrorEnvelope | RatesTAResponse]:
    """Bars + wickworks TA enrichment.

    Args:
        symbol (str):
        exchange (None | str | Unset):
        currency (None | str | Unset):
        primary_exchange (None | str | Unset):
        refresh (bool | Unset):  Default: False.
        body (RatesTARequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorEnvelope | RatesTAResponse]
    """

    kwargs = _get_kwargs(
        symbol=symbol,
        body=body,
        exchange=exchange,
        currency=currency,
        primary_exchange=primary_exchange,
        refresh=refresh,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    symbol: str,
    *,
    client: AuthenticatedClient | Client,
    body: RatesTARequest,
    exchange: None | str | Unset = UNSET,
    currency: None | str | Unset = UNSET,
    primary_exchange: None | str | Unset = UNSET,
    refresh: bool | Unset = False,
) -> ErrorEnvelope | RatesTAResponse | None:
    """Bars + wickworks TA enrichment.

    Args:
        symbol (str):
        exchange (None | str | Unset):
        currency (None | str | Unset):
        primary_exchange (None | str | Unset):
        refresh (bool | Unset):  Default: False.
        body (RatesTARequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorEnvelope | RatesTAResponse
    """

    return (
        await asyncio_detailed(
            symbol=symbol,
            client=client,
            body=body,
            exchange=exchange,
            currency=currency,
            primary_exchange=primary_exchange,
            refresh=refresh,
        )
    ).parsed
