# Dependencies and supply chain

- Runtime deps: direct pins in `requirements.in`, hash-locked into `requirements.txt` by `uv pip compile --generate-hashes`. Both images install with `pip install --require-hashes`.
- Change deps only through the Make targets, which bump the age gate first: `make pkg-add PKG=name==x.y.z`, `make pkg-upgrade PKG=name NEW=x.y.z`, `make pkg-remove PKG=name`, `make pkg-update`. `make pkg-lock` re-locks under the current gate.
- The age gate is `[tool.uv] exclude-newer` in `pyproject.toml`. `scripts/bump_exclude_newer.sh` sets it to today (UTC midnight) minus 7 days before each mutation, so a release published in the last week cannot enter the lock.
- Dev tools live in `requirements-dev.txt`, pinned but not hash-locked, and only in `Dockerfile.dev`.
- The Go client under `pkg/clients/go` is its own module. Use `make pkg-add-go`, `make pkg-upgrade-go` and friends; `scripts/check_go_age.sh` refuses a module version younger than 7 days.
- Scans: `make audit` (pip-audit on `requirements.txt`), `make audit-go` (govulncheck on the Go client), `make audit-compose` (`scripts/audit_compose.sh` on the compose files).
- Each base image digest has a "digest captured" comment next to it; update it with the digest.
- Do not add `httpx` or `requests` as a direct dependency. `httpx` arrives with `mcp` and is used only for the in-process ASGI transport.
