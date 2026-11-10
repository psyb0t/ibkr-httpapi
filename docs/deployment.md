---
title: "Deployment"
description: "The Docker Compose stack: ibgateway, api, nginx and wickworks services, their networks and ports, what state lives where, upgrades, backups and the daily gateway restart."
nav_order: 3
---

# Deployment

ibkr-httpapi runs as a Docker Compose stack built from [`docker-compose.yml.example`](https://github.com/psyb0t/ibkr-httpapi/blob/main/docker-compose.yml.example). There is no published image of the whole thing: the `api` image builds locally from [`Dockerfile.api`](https://github.com/psyb0t/ibkr-httpapi/blob/main/Dockerfile.api), and the gateway image is one you build or choose (see [Getting started](getting-started.md#2-pick-the-gateway-image)).

`run.sh` copies the example to `docker-compose.yml` on the first `make up` and never touches it again, so later changes to the example do not reach an existing deployment. Diff the two after you pull.

## Services

| Service | Image | Job |
| --- | --- | --- |
| `ibgateway` | `${IBKR_GATEWAY_IMAGE:-ghcr.io/gnzsnz/ib-gateway:stable}` | IB Gateway plus IBC. Logs in with `.env.ibkr`, serves the TWS API socket. |
| `api` | `ibkr-httpapi:local`, built from `Dockerfile.api` | The FastAPI app (`python -m ibkrapi`) on port 8889, REST under `/v1` and MCP at `/mcp`. |
| `nginx` | `nginx` 1.27-alpine, pinned by digest | Publishes the API on the host and proxies every path to `api:8889`. |
| `wickworks` | `psyb0t/docker-wickworks:latest` | TA sidecar for `POST .../rates/ta`. Remove the service and clear `wickworks.url` if you do not want it. |
| `cloudflared` | commented out | Tunnel to `http://nginx:80` for public access without a host port. |
| `tailscale` | commented out | Tailnet sidecar. |

Start order follows health checks: `api` waits for `ibgateway` to be healthy, `nginx` waits for `api`.

## Networks

| Network | Members | Notes |
| --- | --- | --- |
| `front` | nginx, api | The only network with a published port. |
| `backend` | api, ibgateway | ibgateway reaches IBKR's servers from here. |
| `internal` | api, wickworks | `internal: true`: no egress, so wickworks cannot reach the internet. |

The TWS API socket is never published on the host. Only `api` can reach it.

## Ports

| Host port | Service | Notes |
| --- | --- | --- |
| `${API_HOST_BIND:-127.0.0.1}:${API_HOST_PORT:-8889}` | nginx | The API. Loopback by default. |
| `127.0.0.1:5900` | ibgateway | VNC to the gateway desktop. Compose sets `VNC_SERVER_PASSWORD` to empty; set a password in the service environment to use it. |
| `127.0.0.1:8001` | ibgateway | Published on loopback by the example file. |

Inside the stack the API listens on `api:8889` and the gateway on 4002 (paper) or 4001 (live), set by `gateway.port` in `config.yaml`.

## State on disk

| Host path | Mounted at | Holds | Back it up |
| --- | --- | --- | --- |
| `config/` | `/app/config` (read-only) in api | `config.yaml` | Yes, it holds the API token. |
| `.env.ibkr` | env file of ibgateway | IBKR username, password, trading mode | Keep it out of Git. It already is. |
| `.data/ibgateway/` | `/home/ibgateway/Jts` in ibgateway | Gateway settings | Optional. |
| `.data/nginx/nginx.conf` | `/etc/nginx/nginx.conf` | nginx config, copied in by `run.sh` | No, it is regenerated. |
| `logs/` | `/app/logs` in api | `full.log`, every JSON log line | Optional. |
| `data/` | `/app/data` in api | `history/`: bars, tick snapshots, chains, executions, completed orders, cached contract metadata | Yes. Nothing else can recreate it. See [Pacing and history](pacing-and-history.md#what-lands-on-disk). |
| `.env` | read by compose | Values `run.sh` derives from `config.yaml` | No, `run.sh` rewrites it on every start. |

`make clean` stops the stack and deletes `.data/`, `logs/` and `run.log`. It leaves `data/` alone.

## Container hardening

- `api`, `nginx` and `wickworks` run with a read-only root filesystem, `tmpfs` for `/tmp` (`noexec,nosuid`), `cap_drop: [ALL]` and `no-new-privileges`. nginx gets back only `NET_BIND_SERVICE`, `CHOWN`, `SETUID` and `SETGID`.
- `ibgateway` keeps a writable filesystem and its capabilities because Xvfb, the JVM and IBC write all over it. It still gets `no-new-privileges`.
- Every service has memory, CPU and PID limits and `json-file` logs capped at 5 files of 10 MB.
- The `api` image runs as the unprivileged `app` user under `tini`, installs dependencies with `--require-hashes`, and uses a base image pinned by digest.

`make audit-compose` runs [`scripts/audit_compose.sh`](https://github.com/psyb0t/ibkr-httpapi/blob/main/scripts/audit_compose.sh) over every compose file in the repository root. It fails on `privileged: true`, host PID, IPC, network, user namespace or cgroup mode, a mounted Docker socket, or `SYS_ADMIN`. It warns about ports published without a bind address, image tags without a digest, and services missing hardening keys.

## Daily restart and 2FA

IBKR logs every session out once a day. The compose file sets `AUTO_RESTART_TIME: "11:59 PM"` (in `TIME_ZONE: Etc/UTC`), so IBC restarts the gateway itself, plus `TWOFA_TIMEOUT_ACTION: restart` and `RELOGIN_AFTER_TWOFA_TIMEOUT: "yes"` so an unanswered 2FA prompt leads to another login attempt instead of a dead gateway. Expect a 2FA push on IBKR Mobile about once a week.

While the gateway is away, the API keeps reconnecting with exponential backoff (`gateway.reconnect_backoff` up to `gateway.reconnect_max_backoff`). Requests that arrive during the gap wait for the reconnect instead of failing; see [troubleshooting](troubleshooting.md#requests-hang-and-then-return-504).

## Make targets for the stack

| Target | Runs |
| --- | --- |
| `make up` | `./run.sh` (described in [Getting started](getting-started.md#5-start-the-stack)) |
| `make down` | `docker compose down` |
| `make logs` | `docker compose logs -f` |
| `make status` | `docker compose ps` |
| `make build` | `docker compose build --no-cache` |
| `make clean` | `make down`, then delete `.data/`, `logs/` and `run.log` |

## Upgrading

```bash
git pull
diff docker-compose.yml.example docker-compose.yml
make build
make up
```

`make up` asks before it restarts a running stack. Read the [changelog](https://github.com/psyb0t/ibkr-httpapi/blob/main/CHANGELOG.md) first: minor versions before 1.0 can change the REST API and say so there.

## Browser access to the gateway desktop

[`Dockerfile.novnc`](https://github.com/psyb0t/ibkr-httpapi/blob/main/Dockerfile.novnc) builds a small noVNC proxy (websockify on port 8080, target `ibgateway:5900` by default, `VNC_PASSWORD` filled into the page so it connects without a prompt). It is not part of the compose file. Add it as a service on the `backend` network if you want to watch the gateway from a browser.

## Public exposure

The default binds the API to `127.0.0.1`. Read [Security](security.md) before you change `API_HOST_BIND` or enable the tunnel sidecars.
