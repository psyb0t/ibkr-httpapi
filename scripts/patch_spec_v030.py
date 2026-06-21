#!/usr/bin/env python3
"""One-shot v0.3.0 spec patch — adds RefreshQuery + RateLimitNear refs
to every operation that needs them.

Run ONCE before `make generate`. Idempotent — re-running is a no-op
since the script checks for existing refs.

Per ~/.claude/rule-details/working-with-generated-code.md: this is a
spec mutation, NOT generated-code editing. The spec is the source of
truth and we're updating it.
"""

from __future__ import annotations

import sys
from collections import OrderedDict

import yaml

SPEC = "api/v1.yaml"

# operationIds that hit the disk cache → get ?refresh
CACHEABLE_OPS = {
    # stocks
    "getStockContract", "getStockRates", "getStockTicks", "getStockRatesTA",
    # options
    "getOptionChain", "getOptionContract", "getOptionRates", "getOptionRatesTA",
    # futures
    "getContinuousFuture", "listFutureContracts", "getFutureContract",
    "getFutureRates", "getFutureRatesTA",
    # cfd (operationId uses CFD upper-case)
    "getCFDContract", "getCFDRates", "getCFDRatesTA",
    # forex
    "getForexContract", "getForexRates", "getForexRatesTA",
    # crypto
    "getCryptoContract", "getCryptoRates", "getCryptoRatesTA",
    # history
    "getExecutions", "getCompletedOrders",
}

# operationIds that hit IBKR (any tier) → get 429 documented
IBKR_OPS = CACHEABLE_OPS | {
    # /tick endpoints
    "getStockTick", "getOptionTick", "getFutureTick",
    "getCFDTick", "getForexTick", "getCryptoTick",
    # orders + option-specific actions
    "placeOrder", "cancelOrder", "cancelAllOrders", "getOrder",
    "placeOptionCombo", "exerciseOption",
}


# Preserve the original YAML's compact-where-possible style.
class _Dumper(yaml.SafeDumper):
    pass


def _str_repr(dumper, data):
    if "\n" in data:
        return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")
    return dumper.represent_scalar("tag:yaml.org,2002:str", data)


_Dumper.add_representer(str, _str_repr)
_Dumper.add_representer(
    OrderedDict,
    lambda dumper, data: dumper.represent_mapping(
        "tag:yaml.org,2002:map", data.items()
    ),
)


def main() -> int:
    with open(SPEC, encoding="utf-8") as fh:
        spec = yaml.safe_load(fh)

    refresh_ref = {"$ref": "#/components/parameters/RefreshQuery"}
    rate_limit_ref = {"$ref": "#/components/responses/RateLimitNear"}

    touched_refresh = 0
    touched_429 = 0

    for path, methods in spec.get("paths", {}).items():
        if not isinstance(methods, dict):
            continue
        for method, op in methods.items():
            if method not in {"get", "post", "delete", "put", "patch"}:
                continue
            if not isinstance(op, dict):
                continue
            op_id = op.get("operationId", "")

            if op_id in CACHEABLE_OPS:
                params = op.setdefault("parameters", [])
                already = any(
                    isinstance(p, dict)
                    and p.get("$ref") == refresh_ref["$ref"]
                    for p in params
                )
                if not already:
                    params.append(refresh_ref)
                    touched_refresh += 1

            if op_id in IBKR_OPS:
                responses = op.setdefault("responses", {})
                if "429" not in responses:
                    responses["429"] = rate_limit_ref
                    touched_429 += 1

    with open(SPEC, "w", encoding="utf-8") as fh:
        yaml.dump(
            spec, fh, Dumper=_Dumper, sort_keys=False, width=120, allow_unicode=True
        )

    print(f"patched: +refresh on {touched_refresh} ops, +429 on {touched_429} ops")
    return 0


if __name__ == "__main__":
    sys.exit(main())
