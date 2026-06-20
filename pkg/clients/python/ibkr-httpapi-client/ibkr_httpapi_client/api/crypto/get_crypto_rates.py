from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.bars_response import BarsResponse
from ...types import UNSET, Response, Unset


def _get_kwargs(
    symbol: str,
    *,
    duration: str,
    bar_size: None | str | Unset = UNSET,
    end_date_time: None | str | Unset = UNSET,
    what_to_show: None | str | Unset = UNSET,
    use_rth: bool | Unset = False,
    exchange: None | str | Unset = UNSET,
    currency: None | str | Unset = UNSET,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    params["duration"] = duration

    json_bar_size: None | str | Unset
    if isinstance(bar_size, Unset):
        json_bar_size = UNSET
    else:
        json_bar_size = bar_size
    params["barSize"] = json_bar_size

    json_end_date_time: None | str | Unset
    if isinstance(end_date_time, Unset):
        json_end_date_time = UNSET
    else:
        json_end_date_time = end_date_time
    params["endDateTime"] = json_end_date_time

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

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/crypto/{symbol}/rates".format(
            symbol=quote(str(symbol), safe=""),
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> BarsResponse | None:
    if response.status_code == 200:
        response_200 = BarsResponse.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[BarsResponse]:
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
    duration: str,
    bar_size: None | str | Unset = UNSET,
    end_date_time: None | str | Unset = UNSET,
    what_to_show: None | str | Unset = UNSET,
    use_rth: bool | Unset = False,
    exchange: None | str | Unset = UNSET,
    currency: None | str | Unset = UNSET,
) -> Response[BarsResponse]:
    """
    Args:
        symbol (str):
        duration (str): IBKR duration: '60 S' / '1 D' / '13 W' / '6 M' / '1 Y'
        bar_size (None | str | Unset): '1h' / '1d' / '15m' etc.
        end_date_time (None | str | Unset): '' for now, or 'YYYYMMDD HH:MM:SS' UTC
        what_to_show (None | str | Unset): TRADES / MIDPOINT / BID / ASK / ...
        use_rth (bool | Unset):  Default: False.
        exchange (None | str | Unset):
        currency (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[BarsResponse]
    """

    kwargs = _get_kwargs(
        symbol=symbol,
        duration=duration,
        bar_size=bar_size,
        end_date_time=end_date_time,
        what_to_show=what_to_show,
        use_rth=use_rth,
        exchange=exchange,
        currency=currency,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    symbol: str,
    *,
    client: AuthenticatedClient | Client,
    duration: str,
    bar_size: None | str | Unset = UNSET,
    end_date_time: None | str | Unset = UNSET,
    what_to_show: None | str | Unset = UNSET,
    use_rth: bool | Unset = False,
    exchange: None | str | Unset = UNSET,
    currency: None | str | Unset = UNSET,
) -> BarsResponse | None:
    """
    Args:
        symbol (str):
        duration (str): IBKR duration: '60 S' / '1 D' / '13 W' / '6 M' / '1 Y'
        bar_size (None | str | Unset): '1h' / '1d' / '15m' etc.
        end_date_time (None | str | Unset): '' for now, or 'YYYYMMDD HH:MM:SS' UTC
        what_to_show (None | str | Unset): TRADES / MIDPOINT / BID / ASK / ...
        use_rth (bool | Unset):  Default: False.
        exchange (None | str | Unset):
        currency (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        BarsResponse
    """

    return sync_detailed(
        symbol=symbol,
        client=client,
        duration=duration,
        bar_size=bar_size,
        end_date_time=end_date_time,
        what_to_show=what_to_show,
        use_rth=use_rth,
        exchange=exchange,
        currency=currency,
    ).parsed


async def asyncio_detailed(
    symbol: str,
    *,
    client: AuthenticatedClient | Client,
    duration: str,
    bar_size: None | str | Unset = UNSET,
    end_date_time: None | str | Unset = UNSET,
    what_to_show: None | str | Unset = UNSET,
    use_rth: bool | Unset = False,
    exchange: None | str | Unset = UNSET,
    currency: None | str | Unset = UNSET,
) -> Response[BarsResponse]:
    """
    Args:
        symbol (str):
        duration (str): IBKR duration: '60 S' / '1 D' / '13 W' / '6 M' / '1 Y'
        bar_size (None | str | Unset): '1h' / '1d' / '15m' etc.
        end_date_time (None | str | Unset): '' for now, or 'YYYYMMDD HH:MM:SS' UTC
        what_to_show (None | str | Unset): TRADES / MIDPOINT / BID / ASK / ...
        use_rth (bool | Unset):  Default: False.
        exchange (None | str | Unset):
        currency (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[BarsResponse]
    """

    kwargs = _get_kwargs(
        symbol=symbol,
        duration=duration,
        bar_size=bar_size,
        end_date_time=end_date_time,
        what_to_show=what_to_show,
        use_rth=use_rth,
        exchange=exchange,
        currency=currency,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    symbol: str,
    *,
    client: AuthenticatedClient | Client,
    duration: str,
    bar_size: None | str | Unset = UNSET,
    end_date_time: None | str | Unset = UNSET,
    what_to_show: None | str | Unset = UNSET,
    use_rth: bool | Unset = False,
    exchange: None | str | Unset = UNSET,
    currency: None | str | Unset = UNSET,
) -> BarsResponse | None:
    """
    Args:
        symbol (str):
        duration (str): IBKR duration: '60 S' / '1 D' / '13 W' / '6 M' / '1 Y'
        bar_size (None | str | Unset): '1h' / '1d' / '15m' etc.
        end_date_time (None | str | Unset): '' for now, or 'YYYYMMDD HH:MM:SS' UTC
        what_to_show (None | str | Unset): TRADES / MIDPOINT / BID / ASK / ...
        use_rth (bool | Unset):  Default: False.
        exchange (None | str | Unset):
        currency (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        BarsResponse
    """

    return (
        await asyncio_detailed(
            symbol=symbol,
            client=client,
            duration=duration,
            bar_size=bar_size,
            end_date_time=end_date_time,
            what_to_show=what_to_show,
            use_rth=use_rth,
            exchange=exchange,
            currency=currency,
        )
    ).parsed
