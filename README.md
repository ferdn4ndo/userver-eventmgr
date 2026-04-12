# userver-eventmgr

[![Validate stack](https://github.com/ferdn4ndo/userver-eventmgr/actions/workflows/validate_stack.yml/badge.svg?branch=main)](https://github.com/ferdn4ndo/userver-eventmgr/actions/workflows/validate_stack.yml)
[![GitLeaks](https://github.com/ferdn4ndo/userver-eventmgr/actions/workflows/test_code_leaks.yml/badge.svg?branch=main)](https://github.com/ferdn4ndo/userver-eventmgr/actions/workflows/test_code_leaks.yml)
[![ShellCheck](https://github.com/ferdn4ndo/userver-eventmgr/actions/workflows/test_code_quality.yml/badge.svg?branch=main)](https://github.com/ferdn4ndo/userver-eventmgr/actions/workflows/test_code_quality.yml)
[![Release](https://img.shields.io/github/v/release/ferdn4ndo/userver-eventmgr)](https://github.com/ferdn4ndo/userver-eventmgr/releases)
[![MIT license](https://img.shields.io/badge/license-MIT-brightgreen.svg)](https://opensource.org/licenses/MIT)

Docker Compose stack for **MQTT** (Eclipse Mosquitto) and **AMQP** (RabbitMQ), designed to run alongside **[userver-web](https://github.com/ferdn4ndo/userver-web)** and **[nginx-proxy](https://github.com/nginx-proxy/nginx-proxy)** on a shared Docker network. Use it for event-style messaging: lightweight pub/sub over MQTT, routing and queues over RabbitMQ.

---

## Services

| Container            | Image                         | Role |
|----------------------|-------------------------------|------|
| `userver-mosquitto`  | `eclipse-mosquitto:alpine`    | MQTT broker: TCP **1883** on the Docker network; **WebSockets on 9001** for reverse-proxy access. |
| `userver-rabbitmq`   | `rabbitmq:4-management-alpine` | AMQP **5672** (apps), management UI **15672** (browser). |

Both services attach to the external network **`nginx-proxy`** so the proxy can discover them via container environment variables (for example `VIRTUAL_HOST_MULTIPORTS`).

### Mosquitto Service

- **Native MQTT:** `userver-mosquitto:1883` from any container on the `nginx-proxy` network. Not published on the host unless you add a `ports:` mapping in `docker-compose.yml`.
- **Web clients:** Connect with **MQTT over WebSockets**. TLS is terminated by nginx-proxy; the URL is typically `wss://<your-mqtt-host>/` on port **443**. The compose env maps the proxy to container port **9001** with `proto: http` so nginx can perform the WebSocket upgrade.
- **Authentication:** `allow_anonymous` is off; credentials are stored in `mosquitto/config/pwfile`. Populate it via `setup-users.env` on startup, or with a single bootstrap user from `MOSQUITTO_USERNAME` / `MOSQUITTO_PASSWORD` in `mosquitto/.env` when `setup-users.env` is absent (see [MQTT users](#mqtt-users)).
- **Logs:** `mosquitto.conf` uses `log_dest stdout`; use `docker logs userver-mosquitto`. The `mosquitto/log` bind mount remains for compatibility but is not used for the main log with the current config.

### RabbitMQ Service

- **AMQP clients:** `userver-rabbitmq:5672` on the Docker network, or **localhost:5672** when using the default compose `ports:` mapping.
- **Management UI:** **http://localhost:15672** locally, or via nginx-proxy using the hostname you set in `VIRTUAL_HOST_MULTIPORTS` (TLS on 443 in production).
- **Erlang node name:** The service sets `hostname: rabbitmq` so `RABBITMQ_NODENAME=rabbit@rabbitmq` resolves inside the container (required for `epmd`).
- **Cluster name:** `rabbitmq/conf.d/05-env-interpolation.conf` sets `cluster_name = deployment-$(DEPLOYMENT_ID)`. You must define **`DEPLOYMENT_ID`** in `rabbitmq/.env` (the template includes an example value).

`VIRTUAL_HOST_MULTIPORTS` should only list **HTTP** upstreams for nginx-proxy. The template maps the **management plugin (15672)**; **5672 is not proxied** through nginx-proxy’s HTTP layer.

**Production `wss://`:** The hostname in **`VIRTUAL_HOST_MULTIPORTS`** must be the same FQDN clients use (DNS + TLS SAN). Set **`LETSENCRYPT_HOST`** to that name for **acme-companion** (the **userver** deploy script sets it from **`USERVER_EVENTMGR_MQTT_HOSTNAME`.`USERVER_VIRTUAL_HOST`** or from **`USERVER_EVENTMGR_MQTT_WSS_HOST`** when defined). If that hostname is missing or nginx falls through to another app (Adminer, etc.), TLS may succeed but WebSocket upgrades will fail.

---

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) with Compose v2.
- An existing Docker network named **`nginx-proxy`** (same as userver-web). Create it once if needed:

  ```bash
  docker network create nginx-proxy
  ```

---

## Setup

1. **Clone** this repository and `cd` into it.

2. **Environment files** (not committed; use templates):

   ```bash
   cp mosquitto/.env.template mosquitto/.env
   cp rabbitmq/.env.template rabbitmq/.env
   ```

   Edit `mosquitto/.env` and `rabbitmq/.env`. Important variables:

   | File | Variables |
   |------|-----------|
   | `rabbitmq/.env` | `VIRTUAL_HOST_MULTIPORTS` (management UI behind nginx-proxy), **`DEPLOYMENT_ID`** (required; feeds `cluster_name` in `rabbitmq/conf.d/05-env-interpolation.conf`), `RABBITMQ_DEFAULT_USER` / `RABBITMQ_DEFAULT_PASS`, `RABBITMQ_NODENAME`, etc. See `rabbitmq/.env.template`. |
   | `mosquitto/.env` | `VIRTUAL_HOST_MULTIPORTS` (WebSocket listener for nginx-proxy), optional **`MOSQUITTO_USERNAME`** / **`MOSQUITTO_PASSWORD`** when you are not using `setup-users.env` (bootstrap single user). See `mosquitto/.env.template`. |

   Set `VIRTUAL_HOST_MULTIPORTS` to hostnames that match your DNS and nginx-proxy certificates.

3. **MQTT users** (`password_file` is always enabled in `mosquitto.conf`):

   **Option A — multiple users (recommended):**

   ```bash
   cp mosquitto/config/setup-users.env.template mosquitto/config/setup-users.env
   # Edit: one line per user, username=password
   ```

   On every container start, `mosquitto/init/container-entrypoint.sh` runs `mosquitto/init/setup-mqtt-users-inner.sh`, which adds any missing users from `mosquitto/config/setup-users.env`. To run the same logic manually against a running container:

   ```bash
   ./mosquitto/init/setup-mqtt-users.sh
   ```

   **Option B — single user, no `setup-users.env`:** leave `setup-users.env` out and set `MOSQUITTO_USERNAME` and `MOSQUITTO_PASSWORD` in `mosquitto/.env`. The entrypoint creates `pwfile` with that user on first start (defaults inside the script are `mqtt` / `password` if the variables are unset).

4. **Start the stack:**

   ```bash
   docker compose up --build --detach
   ```

---

## Usage

### RabbitMQ

- Open the management UI at **http://localhost:15672** (default user/password are seeded from `rabbitmq/.env` via `RABBITMQ_DEFAULT_USER` / `RABBITMQ_DEFAULT_PASS` and `rabbitmq/conf.d/05-env-interpolation.conf`; the broker cluster name is `deployment-<DEPLOYMENT_ID>` from the same file).
- From another container on `nginx-proxy`, use connection string host **`userver-rabbitmq`**, port **5672**.

### Mosquitto

- **From another container:** host `userver-mosquitto`, port **1883**, MQTT with TLS off (plain TCP on the overlay network).
- **From a browser or PWA:** `wss://<mqtt-hostname>/` using MQTT over WebSockets, with credentials from the users in `setup-users.env` or from your `MOSQUITTO_USERNAME` / `MOSQUITTO_PASSWORD` bootstrap user, and nginx-proxy in front.
- **From your workstation** (debugging): add host ports under `userver-mosquitto` in `docker-compose.yml`, for example `"1883:1883"` or `"9001:9001"`, then restart the stack.

### nginx-proxy

Containers expose the metadata nginx-proxy expects (for example `VIRTUAL_HOST_MULTIPORTS` in `.env`). Ensure **userver-nginx-proxy** (or your proxy) shares the **`nginx-proxy`** network and reloads when containers change. Long-lived WebSocket connections may need a higher `proxy_read_timeout` in a per-vhost snippet on the proxy; see comments in `mosquitto/.env.template`.

---

## Continuous integration

GitHub Actions run on pushes and pull requests to `main` / `master`:

- **Validate stack** — creates `nginx-proxy` if missing, seeds env from templates, runs `docker compose up --wait`, smoke-checks RabbitMQ and Mosquitto.
- **Codebase quality** — ShellCheck on shell scripts.
- **Code leaks** — Gitleaks on history.

You can trigger **Validate stack** and **Codebase quality** manually via the **Actions** tab (**workflow_dispatch**).

---

## Repository layout

| Path | Purpose |
|------|---------|
| `docker-compose.yml` | Service definitions, health checks, external `nginx-proxy` network; `env_file` points at `mosquitto/.env` and `rabbitmq/.env`. |
| `mosquitto/.env.template`, `rabbitmq/.env.template` | Copy to `.env` per service; document `VIRTUAL_HOST_MULTIPORTS`, `DEPLOYMENT_ID`, Mosquitto bootstrap vars, etc. |
| `mosquitto/config/mosquitto.conf` | Broker listeners, `password_file`, `log_dest stdout`. |
| `mosquitto/init/` | Custom entrypoint and MQTT user bootstrap scripts. |
| `rabbitmq/conf.d/` | RabbitMQ configuration (including `cluster_name` and credential interpolation in `05-env-interpolation.conf`). |

---

## License

MIT — see [LICENSE](LICENSE).
