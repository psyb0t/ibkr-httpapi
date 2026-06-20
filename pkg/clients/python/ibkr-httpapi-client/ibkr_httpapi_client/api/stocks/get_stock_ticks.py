from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.ticks_response import TicksResponse
from ...types import UNSET, Response, Unset


def _get_kwargs(
    symbol: str,
    *,
    start_date_time: None | str | Unset = UNSET,
    end_date_time: None | str | Unset = UNSET,
    number_of_ticks: int | Unset = 1000,
    what_to_show: None | str | Unset = UNSET,
    use_rth: bool | Unset = False,
    exchange: None | str | Unset = UNSET,
    currency: None | str | Unset = UNSET,
    primary_exchange: None | str | Unset = UNSET,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    json_start_date_time: None | str | Unset
    if isinstance(start_date_time, Unset):
        json_start_date_time = UNSET
    else:
        json_start_date_time = start_date_time
    params["startDateTime"] = json_start_date_time

    json_end_date_time: None | str | Unset
    if isinstance(end_date_time, Unset):
        json_end_date_time = UNSET
    else:
        json_end_date_time = end_date_time
    params["endDateTime"] = json_end_date_time

    params["numberOfTicks"] = number_of_ticks

    json_what_to_show: None | str | Unset
    if isinstance(what_to_show, Unset):
        json_what_to_show = UNSET
    else:
        json_what_to_show = what_to_show
    params["whatToShow"] = json_what_to_show

    params["useRTH"] = use_rth

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
        "url": "/stocks/{symbol}/ticks".format(
            symbol=quote(str(symbol), safe=""),
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> TicksResponse | None:
    if response.status_code == 200:
        response_200 = TicksResponse.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[TicksResponse]:
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
    start_date_time: None | str | Unset = UNSET,
    end_date_time: None | str | Unset = UNSET,
    number_of_ticks: int | Unset = 1000,
    what_to_show: None | str | Unset = UNSET,
    use_rth: bool | Unset = False,
    exchange: None | str | Unset = UNSET,
    currency: None | str | Unset = UNSET,
    primary_exchange: None | str | Unset = UNSET,
) -> Response[TicksResponse]:
    """Historical raw ticks.

    Args:
        symbol (str):
        start_date_time (None | str | Unset):
        end_date_time (None | str | Unset): '' for now, or 'YYYYMMDD HH:MM:SS' UTC
        number_of_ticks (int | Unset):  Default: 1000.
        what_to_show (None | str | Unset): TRADES / MIDPOINT / BID / ASK / ...
        use_rth (bool | Unset):  Default: False.
        exchange (None | str | Unset):
        currency (None | str | Unset):
        primary_exchange (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[TicksResponse]
    """

    kwargs = _get_kwargs(
        symbol=symbol,
        start_date_time=start_date_time,
        end_date_time=end_date_time,
        number_of_ticks=number_of_ticks,
        what_to_show=what_to_show,
        use_rth=use_rth,
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
    start_date_time: None | str | Unset = UNSET,
    end_date_time: None | str | Unset = UNSET,
    number_of_ticks: int | Unset = 1000,
    what_to_show: None | str | Unset = UNSET,
    use_rth: bool | Unset = False,
    exchange: None | str | Unset = UNSET,
    currency: None | str | Unset = UNSET,
    primary_exchange: None | str | Unset = UNSET,
) -> TicksResponse | None:
    """Historical raw ticks.

    Args:
        symbol (str):
        start_date_time (None | str | Unset):
        end_date_time (None | str | Unset): '' for now, or 'YYYYMMDD HH:MM:SS' UTC
        number_of_ticks (int | Unset):  Default: 1000.
        what_to_show (None | str | Unset): TRADES / MIDPOINT / BID / ASK / ...
        use_rth (bool | Unset):  Default: False.
        exchange (None | str | Unset):
        currency (None | str | Unset):
        primary_exchange (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        TicksResponse
    """

    return sync_detailed(
        symbol=symbol,
        client=client,
        start_date_time=start_date_time,
        end_date_time=end_date_time,
        number_of_ticks=number_of_ticks,
        what_to_show=what_to_show,
        use_rth=use_rth,
        exchange=exchange,
        currency=currency,
        primary_exchange=primary_exchange,
    ).parsed


async def asyncio_detailed(
    symbol: str,
    *,
    client: AuthenticatedClient | Client,
    start_date_time: None | str | Unset = UNSET,
    end_date_time: None | str | Unset = UNSET,
    number_of_ticks: int | Unset = 1000,
    what_to_show: None | str | Unset = UNSET,
    use_rth: bool | Unset = False,
    exchange: None | str | Unset = UNSET,
    currency: None | str | Unset = UNSET,
    primary_exchange: None | str | Unset = UNSET,
) -> Response[TicksResponse]:
    """Historical raw ticks.

    Args:
        symbol (str):
        start_date_time (None | str | Unset):
        end_date_time (None | str | Unset): '' for now, or 'YYYYMMDD HH:MM:SS' UTC
        number_of_ticks (int | Unset):  Default: 1000.
        what_to_show (None | str | Unset): TRADES / MIDPOINT / BID / ASK / ...
        use_rth (bool | Unset):  Default: False.
        exchange (None | str | Unset):
        currency (None | str | Unset):
        primary_exchange (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[TicksResponse]
    """

    kwargs = _get_kwargs(
        symbol=symbol,
        start_date_time=start_date_time,
        end_date_time=end_date_time,
        number_of_ticks=number_of_ticks,
        what_to_show=what_to_show,
        use_rth=use_rth,
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
    start_date_time: None | str | Unset = UNSET,
    end_date_time: None | str | Unset = UNSET,
    number_of_ticks: int | Unset = 1000,
    what_to_show: None | str | Unset = UNSET,
    use_rth: bool | Unset = False,
    exchange: None | str | Unset = UNSET,
    currency: None | str | Unset = UNSET,
    primary_exchange: None | str | Unset = UNSET,
) -> TicksResponse | None:
    """Historical raw ticks.

    Args:
        symbol (str):
        start_date_time (None | str | Unset):
        end_date_time (None | str | Unset): '' for now, or 'YYYYMMDD HH:MM:SS' UTC
        number_of_ticks (int | Unset):  Default: 1000.
        what_to_show (None | str | Unset): TRADES / MIDPOINT / BID / ASK / ...
        use_rth (bool | Unset):  Default: False.
        exchange (None | str | Unset):
        currency (None | str | Unset):
        primary_exchange (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        TicksResponse
    """

    return (
        await asyncio_detailed(
            symbol=symbol,
            client=client,
            start_date_time=start_date_time,
            end_date_time=end_date_time,
            number_of_ticks=number_of_ticks,
            what_to_show=what_to_show,
            use_rth=use_rth,
            exchange=exchange,
            currency=currency,
            primary_exchange=primary_exchange,
        )
    ).parsed
