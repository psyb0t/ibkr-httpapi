from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.account_summary import AccountSummary
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    account: None | str | Unset = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    json_account: None | str | Unset
    if isinstance(account, Unset):
        json_account = UNSET
    else:
        json_account = account
    params["account"] = json_account

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/account/values",
        "params": params,
    }

    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> AccountSummary | None:
    if response.status_code == 200:
        response_200 = AccountSummary.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[AccountSummary]:
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
) -> Response[AccountSummary]:
    """Raw account-values stream (more fields than the summary).

    Args:
        account (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[AccountSummary]
    """

    kwargs = _get_kwargs(
        account=account,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    account: None | str | Unset = UNSET,
) -> AccountSummary | None:
    """Raw account-values stream (more fields than the summary).

    Args:
        account (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        AccountSummary
    """

    return sync_detailed(
        client=client,
        account=account,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    account: None | str | Unset = UNSET,
) -> Response[AccountSummary]:
    """Raw account-values stream (more fields than the summary).

    Args:
        account (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[AccountSummary]
    """

    kwargs = _get_kwargs(
        account=account,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    account: None | str | Unset = UNSET,
) -> AccountSummary | None:
    """Raw account-values stream (more fields than the summary).

    Args:
        account (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        AccountSummary
    """

    return (
        await asyncio_detailed(
            client=client,
            account=account,
        )
    ).parsed
