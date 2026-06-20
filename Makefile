.PHONY: help up down logs build status clean dev-image shell lint lint-fix format test pkg-lock pkg-add pkg-update pkg-upgrade pkg-remove pkg-lock-go pkg-add-go pkg-update-go pkg-upgrade-go pkg-remove-go audit audit-go audit-compose generate generate-api generate-api-check generate-client-go generate-client-python

# Image tags + run wrappers — everything dev-shaped runs INSIDE the dev
# container so the host stays clean. Per global rule 30-makefile-contract.

DEV_IMAGE = ibkr-httpapi-dev:local
DEV_RUN = docker run --rm \
    -v $(CURDIR):/app -w /app \
    --network none \
    $(DEV_IMAGE)

DEV_RUN_NET = docker run --rm \
    -v $(CURDIR):/app -w /app \
    $(DEV_IMAGE)

help: ## Show this help
	@awk 'BEGIN{FS=":.*## "; printf "Usage: make <target>\n\nTargets:\n"} /^[a-zA-Z_-]+:.*## /{printf "  %-20s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# ── Dev container ────────────────────────────────────────────────
dev-image: ## Build the dev container (lint/test/pkg-* tooling)
	docker build -f Dockerfile.dev -t $(DEV_IMAGE) .

shell: dev-image ## Drop into an interactive dev container shell
	docker run --rm -it -v $(CURDIR):/app -w /app $(DEV_IMAGE) bash

# ── Code generation ──────────────────────────────────────────────
# `make generate` is the umbrella — call this when ANY input the
# generators consume changes (today only `api/v1.yaml`; in the future
# repogen / x-constants / etc. land here too). NEVER hand-edit anything
# under `ibkrapi/api/_generated/` — per
# `~/.claude/rule-details/working-with-generated-code.md`.
generate: generate-api generate-client-go generate-client-python ## Run all generators (umbrella target)

# `api/v1.yaml` is the source of truth. Custom Jinja templates in
# `api/_templates/` patch fastapi-codegen's defaults to emit `async def`
# + delegate to `ibkrapi.api.impl.<operationId>`.
generate-api: dev-image ## Regenerate FastAPI route stubs + Pydantic models from api/v1.yaml
	$(DEV_RUN_NET) sh -c "rm -rf ibkrapi/api/_generated/* && \
		fastapi-codegen \
			--input api/v1.yaml \
			--output ibkrapi/api/_generated \
			--template-dir api/_templates \
			--generate-routers \
			--output-model-type pydantic_v2.BaseModel \
			--python-version 3.12 \
			--use-annotated \
			--reuse-model && \
		touch ibkrapi/api/_generated/__init__.py \
			ibkrapi/api/_generated/routers/__init__.py"

generate-api-check: generate-api ## CI gate — fail if generated files drift from spec
	@git diff --exit-code ibkrapi/api/_generated || (echo "Generated files drift from spec — run 'make generate' and commit"; exit 1)

# Go client. Output lands in pkg/clients/go/client.gen.go inside its own
# Go module (`pkg/clients/go/go.mod`) so other Go projects can:
#     go get github.com/psyb0t/ibkr-httpapi/pkg/clients/go@latest
# Update the module path in `pkg/clients/go/go.mod` if you fork/rename.
generate-client-go: dev-image ## Regenerate the typed Go client from api/v1.yaml
	$(DEV_RUN_NET) sh -c "oapi-codegen -config api/oapi-codegen-go.yaml api/v1.yaml && \
		cd pkg/clients/go && go mod tidy"

# Python client. Output lands in pkg/clients/python/ibkr-httpapi-client/
# with its own pyproject.toml so other projects can:
#     pip install "git+https://github.com/psyb0t/ibkr-httpapi.git#subdirectory=pkg/clients/python/ibkr-httpapi-client"
generate-client-python: dev-image ## Regenerate the typed Python client from api/v1.yaml
	$(DEV_RUN_NET) sh -c "rm -rf pkg/clients/python/ibkr-httpapi-client && \
		openapi-python-client generate --path api/v1.yaml --output-path pkg/clients/python/ibkr-httpapi-client --overwrite"

# ── Lint / format / type ─────────────────────────────────────────
lint: dev-image ## Run ruff + pyright + bandit
	$(DEV_RUN) sh -c "ruff check ibkrapi tests && pyright ibkrapi && bandit -r ibkrapi -q"

lint-fix: dev-image ## Apply ruff auto-fixes
	$(DEV_RUN) ruff check --fix ibkrapi tests

format: dev-image ## Format with ruff
	$(DEV_RUN) ruff format ibkrapi tests

# ── Tests ────────────────────────────────────────────────────────
test: dev-image ## Run pytest (unit + handler tests, ib_async mocked)
	$(DEV_RUN) pytest -ra

# ── Supply-chain / lockfile (Python) ─────────────────────────────
# Source of truth for the age-gate timestamp lives in pyproject.toml
# under [tool.uv] exclude-newer. `pkg-lock` reads it from there; the
# mutation targets (pkg-add / pkg-update / pkg-upgrade / pkg-remove)
# bump it via scripts/bump_exclude_newer.sh BEFORE the mutation, so
# the resulting lock is gated at today_utc - 7 days. Per
# ~/.claude/rule-details/managing-dependencies.md.
EXCLUDE_NEWER = $(shell grep -E '^exclude-newer\s*=' pyproject.toml | sed -E 's/.*"([^"]+)".*/\1/')
BUMP_HOST = bash scripts/bump_exclude_newer.sh pyproject.toml

pkg-lock: dev-image ## Regenerate requirements.txt with hashes (honors current age-gate)
	$(DEV_RUN_NET) sh -c "pip install --no-cache-dir --quiet uv==0.5.11 && \
		uv pip compile requirements.in --generate-hashes --output-file requirements.txt \
		--python-version 3.12 --exclude-newer $(EXCLUDE_NEWER)"

pkg-add: dev-image ## Add a dep: make pkg-add PKG=foo==1.2.3
	@test -n "$(PKG)" || (echo "Usage: make pkg-add PKG=name==version" && exit 1)
	$(BUMP_HOST)
	echo "$(PKG)" >> requirements.in
	$(MAKE) pkg-lock

pkg-update: dev-image ## Re-lock with current age-gated upper bounds (bumps gate first)
	$(BUMP_HOST)
	$(MAKE) pkg-lock

pkg-upgrade: dev-image ## Upgrade a dep: make pkg-upgrade PKG=foo NEW=1.2.4
	@test -n "$(PKG)" -a -n "$(NEW)" || (echo "Usage: make pkg-upgrade PKG=name NEW=version" && exit 1)
	$(BUMP_HOST)
	sed -i -E "s/^$(PKG)==.*/$(PKG)==$(NEW)/" requirements.in
	$(MAKE) pkg-lock

pkg-remove: dev-image ## Remove a dep: make pkg-remove PKG=foo
	@test -n "$(PKG)" || (echo "Usage: make pkg-remove PKG=name" && exit 1)
	$(BUMP_HOST)
	sed -i -E "/^$(PKG)==/d" requirements.in
	$(MAKE) pkg-lock

# ── Supply-chain / CVE scan ──────────────────────────────────────
# Hash-verified pins + age-gate floor + CVE scan = the three layers.
# Run audit before every release tag + after every pkg-* mutation.
# pip-audit hits OSV/PyPI advisory DBs. Exit non-zero on any finding.
audit: dev-image ## OSV/CVE scan against requirements.txt
	$(DEV_RUN_NET) pip-audit -r requirements.txt --disable-pip --strict

# ── Supply-chain / Go client ─────────────────────────────────────
# Go has no native age-gate flag — scripts/check_go_age.sh hits the
# module proxy's .info endpoint + refuses pulls within 7 days. Only
# applies to the generated client under pkg/clients/go (1 runtime dep
# today: oapi-codegen/runtime). go.sum hash-verifies installs.
CHECK_GO_AGE = bash scripts/check_go_age.sh
GO_CLIENT_DIR = pkg/clients/go

pkg-lock-go: dev-image ## Refresh pkg/clients/go go.sum under existing pins
	$(DEV_RUN_NET) sh -c "cd $(GO_CLIENT_DIR) && go mod tidy"

pkg-add-go: ## Add a Go module to the client: make pkg-add-go PKG=mod@version
	@test -n "$(PKG)" || (echo "Usage: make pkg-add-go PKG=module@version" && exit 1)
	$(CHECK_GO_AGE) "$(PKG)"
	$(DEV_RUN_NET) sh -c "cd $(GO_CLIENT_DIR) && go get $(PKG) && go mod tidy"

pkg-update-go: pkg-lock-go ## Re-tidy go.sum under existing pins

pkg-upgrade-go: ## Upgrade a Go module to latest age-checked version
	@test -n "$(PKG)" || (echo "Usage: make pkg-upgrade-go PKG=module" && exit 1)
	@latest=$$($(DEV_RUN_NET) sh -c "cd $(GO_CLIENT_DIR) && go list -m -versions $(PKG)" | awk '{print $$NF}'); \
		$(CHECK_GO_AGE) "$(PKG)@$$latest" && \
		$(DEV_RUN_NET) sh -c "cd $(GO_CLIENT_DIR) && go get $(PKG)@$$latest && go mod tidy"

pkg-remove-go: ## Remove a Go module: make pkg-remove-go PKG=module
	@test -n "$(PKG)" || (echo "Usage: make pkg-remove-go PKG=module" && exit 1)
	$(DEV_RUN_NET) sh -c "cd $(GO_CLIENT_DIR) && go mod edit -droprequire=$(PKG) && go mod tidy"

audit-go: dev-image ## OSV/CVE scan against pkg/clients/go go.sum
	$(DEV_RUN_NET) sh -c "cd $(GO_CLIENT_DIR) && go install golang.org/x/vuln/cmd/govulncheck@latest && govulncheck ./..."

# ── Supply-chain / compose hardening ─────────────────────────────
# Per ~/.claude/rule-details/hardening-containers.md (compose section).
# Catches banned settings + unpinned images + non-loopback port binds.
# Wire into release gate alongside `audit` (Python) / `audit-go` (Go).
audit-compose: ## Audit docker-compose.yml.example for hardening violations
	@bash scripts/audit_compose.sh

# ── Prod stack ───────────────────────────────────────────────────
up: ## Bring up the IBKR HTTP API stack
	./run.sh

down: ## Stop the stack
	docker compose down

logs: ## Follow compose logs
	docker compose logs -f

build: ## Rebuild prod images
	docker compose build --no-cache

status: ## Show compose ps
	docker compose ps

clean: down ## Stop + remove .data / logs / run.log
	rm -rf .data logs run.log
