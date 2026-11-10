# Spec-first code generation

- `api/v1.yaml` (OpenAPI 3.1.0) is the source of truth for every REST path, parameter and schema. Change the API by editing the spec, then run `make generate`.
- `make generate` runs three generators in the dev container:
  - `make generate-api`: fastapi-code-generator with the custom templates in `api/_templates/` writes `ibkrapi/api/_generated/` (`models.py`, `dependencies.py`, `main.py`, `routers/*.py`). It wipes the directory first.
  - `make generate-client-go`: oapi-codegen with `api/oapi-codegen-go.yaml` writes `pkg/clients/go/client.gen.go`, then `go mod tidy`.
  - `make generate-client-python`: openapi-python-client writes `pkg/clients/python/ibkr-httpapi-client/`. It deletes that directory first.
- Generated output: `ibkrapi/api/_generated/`, `pkg/clients/go/client.gen.go` and `pkg/clients/python/ibkr-httpapi-client/`. Ruff skips `_generated`, and pyright ignores its diagnostics.
- `make generate-api-check` regenerates and fails on `git diff` drift in `ibkrapi/api/_generated`.
- Every generated route is one line: `return await impl.<snake_case_operationId>(<args in spec order>)`. The arguments are positional, so the parameter order of each function in `ibkrapi/api/impl.py` must match the generated call exactly. Query parameters come first in spec order, then `refresh` where the spec has it, then `body` last. Read the generated router before you add or reorder an impl parameter; a mismatch type-checks only in the generated file, which pyright ignores, so add or extend a test in `tests/test_server.py` that calls the route.
- `ibkrapi/routers/_constants.py` holds shared string constants (sec types, order types, asset class aliases). It is not a router directory.
- `scripts/patch_spec_v030.py` was a one-time spec patch for v0.3.0. Do not run it again.
