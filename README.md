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

### Mosquitto

- **Native MQTT:** `userver-mosquitto:1883` from any container on the `nginx-proxy` network. Not published on the host unless you add a `ports:` mapping in `docker-compose.yml`.
- **Web clients:** Connect with **MQTT over WebSockets**. TLS is terminated by nginx-proxy; the URL is typically `wss://<your-mqtt-host>/` on port **443**. The compose env maps the proxy to container port **9001** with `proto: http` so nginx can perform the WebSocket upgrade.
- **Authentication:** `allow_anonymous` is off; users live in `mosquitto/config/pwfile`, managed with `mosquitto_passwd` (see [MQTT users](#mqtt-users)).

### RabbitMQ

- **AMQP clients:** `userver-rabbitmq:5672` on the Docker network, or **localhost:5672** when using the default compose `ports:` mapping.
- **Management UI:** **http://localhost:15672** locally, or via nginx-proxy using the hostname you set in `VIRTUAL_HOST_MULTIPORTS` (TLS on 443 in production).
- **Erlang node name:** The service sets `hostname: rabbitmq` so `RABBITMQ_NODENAME=rabbit@rabbitmq` resolves inside the container (required for `epmd`).

`VIRTUAL_HOST_MULTIPORTS` should only list **HTTP** upstreams for nginx-proxy. The template maps the **management plugin (15672)**; **5672 is not proxied** through nginx-proxy’s HTTP layer.

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

   Edit `mosquitto/.env` and `rabbitmq/.env`. Set `VIRTUAL_HOST_MULTIPORTS` to hostnames that match your DNS and nginx-proxy certificates. See comments inside each template.

3. **MQTT users** (optional but required for clients if you keep `password_file` enabled):

   ```bash
   cp mosquitto/config/setup-users.env.template mosquitto/config/setup-users.env
   # Edit: one line per user, username=password
   ```

   On every container start, `mosquitto/init/container-entrypoint.sh` runs `mosquitto/init/setup-mqtt-users-inner.sh`, which adds any missing users from `mosquitto/config/setup-users.env`. To run the same logic manually against a running container:

   ```bash
   ./mosquitto/init/setup-mqtt-users.sh
   ```

4. **Start the stack:**

   ```bash
   docker compose up --build --detach
   ```

---

## Usage

### RabbitMQ

- Open the management UI at **http://localhost:15672** (default user/password are seeded from `rabbitmq/.env` via `RABBITMQ_DEFAULT_USER` / `RABBITMQ_DEFAULT_PASS` and `rabbitmq/rabbitmq.conf`).
- From another container on `nginx-proxy`, use connection string host **`userver-rabbitmq`**, port **5672**.

### Mosquitto

- **From another container:** host `userver-mosquitto`, port **1883**, MQTT with TLS off (plain TCP on the overlay network).
- **From a browser or PWA:** `wss://<mqtt-hostname>/` using MQTT over WebSockets, credentials from `setup-users.env`, with nginx-proxy in front.
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
| `docker-compose.yml` | Service definitions, health checks, external `nginx-proxy` network. |
| `mosquitto/config/mosquitto.conf` | Broker listeners and auth. |
| `mosquitto/init/` | Custom entrypoint and MQTT user bootstrap scripts. |
| `rabbitmq/rabbitmq.conf`, `rabbitmq/conf.d/` | RabbitMQ configuration. |

---

## License

MIT — see [LICENSE](LICENSE).
