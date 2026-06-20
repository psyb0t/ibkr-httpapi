"""Shared constants used across asset-class routers.

Promoted here (per `~/.claude/rules/08-constants-discipline.md` Level 3 —
"2+ packages → project-local common") because the same `secType` strings
showed up as response-payload values in 7 router files. Single source of
truth so a future asset class can't drift its string.
"""

from __future__ import annotations

from typing import Final

# IBKR security-type codes — these are the canonical strings ib_async
# sets on Contract.secType, mirrored back in our response payload so
# clients can SWITCH on a stable identifier without parsing nested
# `contract.secType` paths.
SECTYPE_STK: Final = "STK"
SECTYPE_OPT: Final = "OPT"
SECTYPE_FUT: Final = "FUT"
SECTYPE_CFD: Final = "CFD"
SECTYPE_CASH: Final = "CASH"
SECTYPE_CRYPTO: Final = "CRYPTO"
SECTYPE_IND: Final = "IND"
SECTYPE_BAG: Final = "BAG"

# Order actions — validated against user input on `POST /orders`.
ACTION_BUY: Final = "BUY"
ACTION_SELL: Final = "SELL"
VALID_ACTIONS: Final = (ACTION_BUY, ACTION_SELL)

# Order types — validated against user input.
ORDER_TYPE_MKT: Final = "MKT"
ORDER_TYPE_LMT: Final = "LMT"
ORDER_TYPE_STP: Final = "STP"
ORDER_TYPE_STP_LMT: Final = "STP_LMT"
# Aliases the API accepts for stop-limit (callers vary):
ORDER_TYPE_STP_LMT_ALIASES: Final = ("STP_LMT", "STP LMT", "STPLMT")
# Subset accepted by the combo (BAG) endpoint — combos only support
# market + limit on Deribit/IBKR alike.
COMBO_VALID_ORDER_TYPES: Final = (ORDER_TYPE_MKT, ORDER_TYPE_LMT)

# Time-in-force codes.
TIF_DAY: Final = "DAY"
TIF_GTC: Final = "GTC"

# Option right (call/put). The Option contract factory normalizes
# CALL/PUT to single-letter form too — these are the canonical leaves.
RIGHT_CALL: Final = "C"
RIGHT_PUT: Final = "P"

# Asset-class strings accepted on `POST /orders.assetClass`.
ASSET_STOCK: Final = "stock"
ASSET_STK: Final = "stk"
ASSET_OPTION: Final = "option"
ASSET_OPT: Final = "opt"
ASSET_FUTURE: Final = "future"
ASSET_FUT: Final = "fut"
ASSET_CFD: Final = "cfd"
ASSET_FOREX: Final = "forex"
ASSET_CASH: Final = "cash"
ASSET_CRYPTO: Final = "crypto"
# Grouped — used as fast `in` checks inside the contract builder dispatch.
ASSET_STOCK_ALIASES: Final = (ASSET_STOCK, ASSET_STK)
ASSET_OPTION_ALIASES: Final = (ASSET_OPTION, ASSET_OPT)
ASSET_FUTURE_ALIASES: Final = (ASSET_FUTURE, ASSET_FUT)
ASSET_FOREX_ALIASES: Final = (ASSET_FOREX, ASSET_CASH)
