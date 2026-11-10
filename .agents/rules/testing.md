# Testing and lint

- Everything runs in the dev container built from `Dockerfile.dev` (`ibkr-httpapi-dev:local`). The host needs only Docker and Make.
- `make lint` runs `ruff check ibkrapi tests`, `pyright ibkrapi` and `bandit -r ibkrapi -q`, with `--network none`. `make test` runs `pytest -ra`, also with `--network none`. CI runs exactly these two targets.
- Tests never touch a real gateway. The `mock_ib` fixture in `tests/conftest.py` replaces `ibclient.get_ib` and `marketdata.get_ib` with a `MagicMock` IB whose async methods are `AsyncMock`s. Set return values per test.
- An autouse fixture turns every disk cache off and configures pacing with very high limits. Tests for a cache or for pacing re-enable their own module with `tmp_path`.
- HTTP tests go through `fastapi.testclient.TestClient`. `API_TOKEN` is read at import time, so `tests/test_server.py` reloads `ibkrapi.config` and `ibkrapi.server` after setting the environment. Keep that pattern for any test that depends on a config constant.
- `pytest` runs with `filterwarnings = ["error"]`: a new deprecation warning fails the suite.
- The wickworks URL from a local `config/config.yaml` leaks into tests through `ibkrapi.config`. Monkeypatch `ibkrapi.marketdata.WICKWORKS_URL` in any test that depends on it.
- Ruff config: line length 100, rules `E F W I UP B S C4 SIM RUF`, `ibkrapi/api/_generated` excluded. Format with `make format`.
