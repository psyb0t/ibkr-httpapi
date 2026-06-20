from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.completed_orders_response import CompletedOrdersResponse
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    api_only: bool | Unset = False,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    params["apiOnly"] = api_only

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/history/completed_orders",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> CompletedOrdersResponse | None:
    if response.status_code == 200:
        response_200 = CompletedOrdersResponse.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[CompletedOrdersResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    api_only: bool | Unset = False,
) -> Response[CompletedOrdersResponse]:
    """Completed orders (today + historical buffer).

    Args:
        api_only (bool | Unset):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CompletedOrdersResponse]
    """

    kwargs = _get_kwargs(
        api_only=api_only,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    api_only: bool | Unset = False,
) -> CompletedOrdersResponse | None:
    """Completed orders (today + historical buffer).

    Args:
        api_only (bool | Unset):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        CompletedOrdersResponse
    """

    return sync_detailed(
        client=client,
        api_only=api_only,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    api_only: bool | Unset = False,
) -> Response[CompletedOrdersResponse]:
    """Completed orders (today + historical buffer).

    Args:
        api_only (bool | Unset):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CompletedOrdersResponse]
    """

    kwargs = _get_kwargs(
        api_only=api_only,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    api_only: bool | Unset = False,
) -> CompletedOrdersResponse | None:
    """Completed orders (today + historical buffer).

    Args:
        api_only (bool | Unset):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        CompletedOrdersResponse
    """

    return (
        await asyncio_detailed(
            client=client,
            api_only=api_only,
        )
    ).parsed
