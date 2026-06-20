"""Load + expose the project's runtime configuration from config.yaml.

Resolves config.yaml relative to the project root (BASE_DIR). Provides
typed module-level constants so handlers can do `from ibkrapi.config
import GATEWAY_HOST` instead of re-parsing YAML on every call.
"""

from __future__ import annotations

import argparse
import os
import re

import yaml

PACKAGE_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(PACKAGE_DIR)
CONFIG_YAML = os.path.join(BASE_DIR, "config", "config.yaml")
LOG_DIR = os.path.join(BASE_DIR, "logs")
FULL_LOG = os.path.join(LOG_DIR, "full.log")

_DURATION_RE = re.compile(r"(\d+(?:\.\d+)?)\s*([smhdSMHD]?)")


def parse_duration_to_seconds(value) -> float:
    """Parse '5s', '30m', '2h', '1d', '1h30m', or bare number into seconds.

    Bare number is interpreted as seconds. Unknown unit raises ValueError.
    """
    if value in (None, ""):
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip().lower()
    if not text:
        return 0.0
    total = 0.0
    pos = 0
    while pos < len(text):
        m = _DURATION_RE.match(text, pos)
        if not m or m.start() != pos:
            raise ValueError(f"Invalid duration: {value!r}")
        amount = float(m.group(1))
        unit = m.group(2) or "s"
        multipliers = {"s": 1, "m": 60, "h": 3600, "d": 86400}
        if unit not in multipliers:
            raise ValueError(f"Unknown duration unit: {unit!r}")
        total += amount * multipliers[unit]
        pos = m.end()
    return total


def load_yaml_config() -> dict:
    if not os.path.isfile(CONFIG_YAML):
        return {}
    with open(CONFIG_YAML, encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def _parse_args():
    parser = argparse.ArgumentParser(prog="ibkrapi")
    parser.add_argument("--host", default=None)
    parser.add_argument("--port", type=int, default=None)
    parser.add_argument("--token", default=None)
    parser.add_argument("--gateway-host", default=None)
    parser.add_argument("--gateway-port", type=int, default=None)
    parser.add_argument("--client-id", type=int, default=None)
    parser.add_argument("--account", default=None)
    args, _ = parser.parse_known_args()
    return args


_args = _parse_args()
_cfg = load_yaml_config()

# ── API server ──────────────────────────────────────────────────
# 0.0.0.0 binding is intentional inside the api container — nginx is the
# only thing on the same docker network that talks to it, and nginx is
# the loopback-published edge. See compose `expose:` (no host port) on
# the api service for the actual network exposure.
HOST = _args.host or os.environ.get("API_HOST", "0.0.0.0")  # noqa: S104  # nosec B104
PORT = _args.port or int(os.environ.get("API_PORT", "8889"))
API_TOKEN = _args.token or os.environ.get("API_TOKEN", "") or (_cfg.get("api_token") or "")

# ── Gateway (ib_async target) ────────────────────────────────────
_gw = _cfg.get("gateway") or {}
GATEWAY_HOST = (
    _args.gateway_host or os.environ.get("IBKR_GATEWAY_HOST") or _gw.get("host") or "ibgateway"
)
GATEWAY_PORT = (
    _args.gateway_port
    or int(os.environ.get("IBKR_GATEWAY_PORT", "0") or 0)
    or int(_gw.get("port") or 4002)
)
CLIENT_ID = (
    _args.client_id
    or int(os.environ.get("IBKR_CLIENT_ID", "0") or 0)
    or int(_gw.get("client_id") or 1)
)
ACCOUNT = _args.account or os.environ.get("IBKR_ACCOUNT") or (_gw.get("account") or "")
CONNECT_TIMEOUT_SECONDS = parse_duration_to_seconds(_gw.get("connect_timeout") or "20s")
RECONNECT_BACKOFF_SECONDS = parse_duration_to_seconds(_gw.get("reconnect_backoff") or "5s")
RECONNECT_MAX_BACKOFF_SECONDS = parse_duration_to_seconds(_gw.get("reconnect_max_backoff") or "60s")

# ── Market data ─────────────────────────────────────────────────
MARKET_DATA_TYPE = int(_cfg.get("market_data_type") or 3)
if MARKET_DATA_TYPE not in (1, 2, 3, 4):
    raise ValueError(
        f"config.market_data_type must be 1/2/3/4 (live/frozen/delayed/delayed-frozen), "
        f"got {MARKET_DATA_TYPE!r}"
    )

# ── Wickworks TA sidecar ────────────────────────────────────────
_ww = _cfg.get("wickworks") or {}
WICKWORKS_URL = os.environ.get("WICKWORKS_URL") or (_ww.get("url") or "")
WICKWORKS_TIMEOUT_SECONDS = (
    parse_duration_to_seconds(os.environ.get("WICKWORKS_TIMEOUT") or _ww.get("timeout") or "30s")
    or 30.0
)

# ── Contract defaults ───────────────────────────────────────────
CONTRACT_DEFAULTS = _cfg.get("contract_defaults") or {}

# ── Identity (for log prefix) ───────────────────────────────────
IDENTITY = f"{GATEWAY_HOST}:{GATEWAY_PORT}#{CLIENT_ID}"
