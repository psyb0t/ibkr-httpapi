from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.bars_response import BarsResponse
from ...models.error_envelope import ErrorEnvelope
from ...types import UNSET, Response, Unset


def _get_kwargs(
    pair: str,
    *,
    duration: str,
    bar_size: None | str | Unset = UNSET,
    end_date_time: None | str | Unset = UNSET,
    what_to_show: None | str | Unset = UNSET,
    use_rth: bool | Unset = False,
    exchange: None | str | Unset = UNSET,
    refresh: bool | Unset = False,
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

    params["refresh"] = refresh

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/forex/{pair}/rates".format(
            pair=quote(str(pair), safe=""),
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> BarsResponse | ErrorEnvelope | None:
    if response.status_code == 200:
        response_200 = BarsResponse.from_dict(response.json())

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
) -> Response[BarsResponse | ErrorEnvelope]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    pair: str,
    *,
    client: AuthenticatedClient | Client,
    duration: str,
    bar_size: None | str | Unset = UNSET,
    end_date_time: None | str | Unset = UNSET,
    what_to_show: None | str | Unset = UNSET,
    use_rth: bool | Unset = False,
    exchange: None | str | Unset = UNSET,
    refresh: bool | Unset = False,
) -> Response[BarsResponse | ErrorEnvelope]:
    """
    Args:
        pair (str):
        duration (str): IBKR duration: '60 S' / '1 D' / '13 W' / '6 M' / '1 Y'
        bar_size (None | str | Unset): '1h' / '1d' / '15m' etc.
        end_date_time (None | str | Unset): '' for now, or 'YYYYMMDD HH:MM:SS' UTC
        what_to_show (None | str | Unset): TRADES / MIDPOINT / BID / ASK / ...
        use_rth (bool | Unset):  Default: False.
        exchange (None | str | Unset):
        refresh (bool | Unset):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[BarsResponse | ErrorEnvelope]
    """

    kwargs = _get_kwargs(
        pair=pair,
        duration=duration,
        bar_size=bar_size,
        end_date_time=end_date_time,
        what_to_show=what_to_show,
        use_rth=use_rth,
        exchange=exchange,
        refresh=refresh,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    pair: str,
    *,
    client: AuthenticatedClient | Client,
    duration: str,
    bar_size: None | str | Unset = UNSET,
    end_date_time: None | str | Unset = UNSET,
    what_to_show: None | str | Unset = UNSET,
    use_rth: bool | Unset = False,
    exchange: None | str | Unset = UNSET,
    refresh: bool | Unset = False,
) -> BarsResponse | ErrorEnvelope | None:
    """
    Args:
        pair (str):
        duration (str): IBKR duration: '60 S' / '1 D' / '13 W' / '6 M' / '1 Y'
        bar_size (None | str | Unset): '1h' / '1d' / '15m' etc.
        end_date_time (None | str | Unset): '' for now, or 'YYYYMMDD HH:MM:SS' UTC
        what_to_show (None | str | Unset): TRADES / MIDPOINT / BID / ASK / ...
        use_rth (bool | Unset):  Default: False.
        exchange (None | str | Unset):
        refresh (bool | Unset):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        BarsResponse | ErrorEnvelope
    """

    return sync_detailed(
        pair=pair,
        client=client,
        duration=duration,
        bar_size=bar_size,
        end_date_time=end_date_time,
        what_to_show=what_to_show,
        use_rth=use_rth,
        exchange=exchange,
        refresh=refresh,
    ).parsed


async def asyncio_detailed(
    pair: str,
    *,
    client: AuthenticatedClient | Client,
    duration: str,
    bar_size: None | str | Unset = UNSET,
    end_date_time: None | str | Unset = UNSET,
    what_to_show: None | str | Unset = UNSET,
    use_rth: bool | Unset = False,
    exchange: None | str | Unset = UNSET,
    refresh: bool | Unset = False,
) -> Response[BarsResponse | ErrorEnvelope]:
    """
    Args:
        pair (str):
        duration (str): IBKR duration: '60 S' / '1 D' / '13 W' / '6 M' / '1 Y'
        bar_size (None | str | Unset): '1h' / '1d' / '15m' etc.
        end_date_time (None | str | Unset): '' for now, or 'YYYYMMDD HH:MM:SS' UTC
        what_to_show (None | str | Unset): TRADES / MIDPOINT / BID / ASK / ...
        use_rth (bool | Unset):  Default: False.
        exchange (None | str | Unset):
        refresh (bool | Unset):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[BarsResponse | ErrorEnvelope]
    """

    kwargs = _get_kwargs(
        pair=pair,
        duration=duration,
        bar_size=bar_size,
        end_date_time=end_date_time,
        what_to_show=what_to_show,
        use_rth=use_rth,
        exchange=exchange,
        refresh=refresh,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    pair: str,
    *,
    client: AuthenticatedClient | Client,
    duration: str,
    bar_size: None | str | Unset = UNSET,
    end_date_time: None | str | Unset = UNSET,
    what_to_show: None | str | Unset = UNSET,
    use_rth: bool | Unset = False,
    exchange: None | str | Unset = UNSET,
    refresh: bool | Unset = False,
) -> BarsResponse | ErrorEnvelope | None:
    """
    Args:
        pair (str):
        duration (str): IBKR duration: '60 S' / '1 D' / '13 W' / '6 M' / '1 Y'
        bar_size (None | str | Unset): '1h' / '1d' / '15m' etc.
        end_date_time (None | str | Unset): '' for now, or 'YYYYMMDD HH:MM:SS' UTC
        what_to_show (None | str | Unset): TRADES / MIDPOINT / BID / ASK / ...
        use_rth (bool | Unset):  Default: False.
        exchange (None | str | Unset):
        refresh (bool | Unset):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        BarsResponse | ErrorEnvelope
    """

    return (
        await asyncio_detailed(
            pair=pair,
            client=client,
            duration=duration,
            bar_size=bar_size,
            end_date_time=end_date_time,
            what_to_show=what_to_show,
            use_rth=use_rth,
            exchange=exchange,
            refresh=refresh,
        )
    ).parsed
