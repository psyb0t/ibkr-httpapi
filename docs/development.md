---
title: "Development"
description: "Work on ibkr-httpapi: repository layout, the dev container, lint and tests, spec-first code generation, dependency rules, CI, the docs build and releases."
nav_order: 12
---

# Development

Everything that builds, lints, tests or generates code runs in a dev container built from [`Dockerfile.dev`](https://github.com/psyb0t/ibkr-httpapi/blob/main/Dockerfile.dev). The host needs Docker and Make, nothing else. `make help` lists every target.

## Layout

| Path | Contents |
| --- | --- |
| [`api/v1.yaml`](https://github.com/psyb0t/ibkr-httpapi/blob/main/api/v1.yaml) | OpenAPI 3.1.0 spec. Source of truth for routes, models and both clients. |
| [`api/_templates/`](https://github.com/psyb0t/ibkr-httpapi/tree/main/api/_templates) | Templates that make fastapi-code-generator emit `async def` handlers that call `impl`. |
| [`ibkrapi/server.py`](https://github.com/psyb0t/ibkr-httpapi/blob/main/ibkrapi/server.py) | App setup, auth and logging middleware, `/v1` and `/mcp` mounts. |
| [`ibkrapi/api/impl.py`](https://github.com/psyb0t/ibkr-httpapi/blob/main/ibkrapi/api/impl.py) | All endpoint logic. One function per `operationId`. |
| [`ibkrapi/api/_generated/`](https://github.com/psyb0t/ibkr-httpapi/tree/main/ibkrapi/api/_generated) | Generated routers and Pydantic models. Never edited by hand. |
| [`ibkrapi/ibclient.py`](https://github.com/psyb0t/ibkr-httpapi/blob/main/ibkrapi/ibclient.py) | The shared `ib_async` connection and its reconnect loop. |
| [`ibkrapi/contracts.py`](https://github.com/psyb0t/ibkr-httpapi/blob/main/ibkrapi/contracts.py), [`marketdata.py`](https://github.com/psyb0t/ibkr-httpapi/blob/main/ibkrapi/marketdata.py), [`serialize.py`](https://github.com/psyb0t/ibkr-httpapi/blob/main/ibkrapi/serialize.py) | Contract builders, IBKR data calls and the wickworks POST, SDK object to dict converters. |
| `ibkrapi/pacing.py`, `cache_*.py`, `historian.py`, `exec_history.py` | The pacing gate and the disk stores ([Pacing and history](pacing-and-history.md)). |
| [`ibkrapi/mcp_server.py`](https://github.com/psyb0t/ibkr-httpapi/blob/main/ibkrapi/mcp_server.py) | The MCP tools. |
| [`ibkrapi/config.py`](https://github.com/psyb0t/ibkr-httpapi/blob/main/ibkrapi/config.py), [`logger.py`](https://github.com/psyb0t/ibkr-httpapi/blob/main/ibkrapi/logger.py) | Config loading, JSON logging. |
| [`tests/`](https://github.com/psyb0t/ibkr-httpapi/tree/main/tests) | pytest suite with a mocked IB connection. |
| [`pkg/clients/`](https://github.com/psyb0t/ibkr-httpapi/tree/main/pkg/clients) | Generated Go and Python clients. |
| [`scripts/`](https://github.com/psyb0t/ibkr-httpapi/tree/main/scripts) | Age gate bump, Go module age check, compose audit, a one-time v0.3.0 spec patch. |
| `docs/` | This site. |
| [`.agents/`](https://github.com/psyb0t/ibkr-httpapi/tree/main/.agents) | Agent rules, the client skill, the OpenClaw plugin, marketplace manifests. |

Contributor and agent rules live in [`AGENTS.md`](https://github.com/psyb0t/ibkr-httpapi/blob/main/AGENTS.md) and [`.agents/rules/`](https://github.com/psyb0t/ibkr-httpapi/tree/main/.agents/rules).

## Lint and tests

```bash
make lint     # ruff check ibkrapi tests, pyright ibkrapi, bandit -r ibkrapi
make test     # pytest -ra
make format   # ruff format ibkrapi tests
make lint-fix # ruff check --fix ibkrapi tests
make shell    # interactive shell in the dev container
```

`make lint` and `make test` build the dev image first and then run with `--network none`, so they need no credentials and no network once the image exists. They are exactly what CI runs.

The tests never talk to a gateway. [`tests/conftest.py`](https://github.com/psyb0t/ibkr-httpapi/blob/main/tests/conftest.py) replaces `get_ib()` with a mock IB object, turns every disk store off and sets pacing limits high. HTTP tests use FastAPI's `TestClient` against `/v1/...`. Warnings are errors (`filterwarnings = ["error"]`).

Ruff skips `ibkrapi/api/_generated`, and pyright ignores diagnostics in it; the generated routers use FastAPI's `param: str = ...` idiom, which pyright flags.

## Code generation

The spec is the API. To add or change an endpoint:

1. Edit `api/v1.yaml`.
2. Run `make generate`. It runs `generate-api` (routers and models into `ibkrapi/api/_generated/`), `generate-client-go` (`pkg/clients/go/client.gen.go`) and `generate-client-python` (`pkg/clients/python/ibkr-httpapi-client/`). Each one deletes and rewrites its output.
3. Write or update the function in `ibkrapi/api/impl.py` named after the snake-cased `operationId`.
4. Run `make generate-api-check`, which regenerates and fails if `ibkrapi/api/_generated` differs from what is committed.

Generated handlers pass arguments to `impl` by position, in spec order: query parameters, then `refresh` where it exists, then the request `body` last. The impl function must take them in exactly that order. Pyright does not report a mismatch because it ignores the generated files, so cover each new route with a request in [`tests/test_server.py`](https://github.com/psyb0t/ibkr-httpapi/blob/main/tests/test_server.py).

A new IBKR call in `impl.py` goes inside `async with pacing.guard(<tier>, <key>)`.

## Dependencies

- Runtime pins are in [`requirements.in`](https://github.com/psyb0t/ibkr-httpapi/blob/main/requirements.in), locked with hashes into `requirements.txt`. Both Dockerfiles install with `--require-hashes`.
- Change them only through Make, which first moves the age gate (`[tool.uv] exclude-newer` in `pyproject.toml`) to seven days ago:

```bash
make pkg-add PKG=name==1.2.3
make pkg-upgrade PKG=name NEW=1.2.4
make pkg-remove PKG=name
make pkg-update
```

- The Go client has its own targets (`pkg-add-go`, `pkg-upgrade-go`, `pkg-remove-go`, `pkg-lock-go`); `scripts/check_go_age.sh` refuses module versions younger than seven days.
- Scans: `make audit` (pip-audit), `make audit-go` (govulncheck), `make audit-compose` (compose hardening).
- Dev tools are in `requirements-dev.txt`, only in the dev image.

## CI

[`.github/workflows/pipeline.yml`](https://github.com/psyb0t/ibkr-httpapi/blob/main/.github/workflows/pipeline.yml) runs on every push:

| Trigger | Jobs |
| --- | --- |
| Any branch | `code`: `make lint` and `make test` on a plain runner, through the shared code workflow. |
| `main` | `code`, then `badges` (version and license badges on the `badges` branch). |
| `v*` tag | `wait` for that commit's `main` run to pass, `release` (GitHub release from the annotated tag), `publish-to-clawhub` (the `ibkr-httpapi` skill and plugin), `badges`. |

No image is built in CI. The `api` image builds on the host through compose, and the gateway image cannot be redistributed.

Two more workflows run beside it: `mirror-and-archive.yml` mirrors the repository to GitLab and Codeberg and archives it, and `issue-pull.yml` copies issues from the mirrors back to GitHub.

## Docs

The site is `docs/`, built by GitHub Pages from `main` with the just-the-docs theme. Build it locally with the same image GitHub uses:

```bash
make docs
```

The output goes to a gitignored directory named by `DOCS_SITE` in the Makefile. Pages link to each other with relative `.md` paths and to repository files with full GitHub URLs.

## Releases

Every release gets a section in [`CHANGELOG.md`](https://github.com/psyb0t/ibkr-httpapi/blob/main/CHANGELOG.md) and an annotated `v*` tag on a commit that is already on `main`. Pushing the tag starts the release jobs above.
