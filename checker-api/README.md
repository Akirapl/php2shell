# PHP2Shell-Live-Checker API

Passive, defensive PHP banner checker behind the "Am I affected?" widget on the live center
(<https://akirapl.github.io/php2shell/#sec-checker>).

> **Check only systems you own or are authorised to test.**
> Sprawdzaj tylko własne systemy lub takie, na których test masz zgodę.
> Prüfen Sie nur eigene Systeme oder solche, für deren Test Sie eine Erlaubnis haben.

## API

- `GET /check?url=…` returns JSON `{input, resolved_host, resolved_ip, php_detected, version, classification, classification_label, details, caveats, checked_at}`. A refusal adds `error` and `message`. The first entry of `caveats` is always the ownership notice above.
- `GET /health` is the liveness probe.

`classification` is one of `likely_vulnerable`, `likely_patched`, `php_detected_version_hidden`, `no_php_detected` or `host_unreachable`.
Fixed upstream versions: 8.5.12 / 8.4.27 / 8.3.36 / 8.2.35. Anything below 8.2 is end-of-life (no official fixed release; source-only upstream backports exist for 7.4/8.0/8.1) and is classed as `likely_vulnerable`, with the `eol` and `distro_build_suspected` flags set where they apply.

The result only reflects the public banner. Distributions backport fixes without changing the version string. Proxies and CDNs can hide or rewrite the headers. The reliable check is `php -v` on the server, plus your package changelog.

## Safety

- Only http and https, only ports 80 and 443, only the root path `/`.
- Private, loopback, link-local, reserved and CGNAT addresses are refused. This applies to every resolved address and to every redirect hop. The connection is pinned to the validated IP, so DNS rebinding cannot redirect it.
- At most 2 redirects, 8 s in total, and at most 4 KB of the body is read.
- User agent: `PHP2Shell-Live-Checker/1.0`.
- No payloads, no scanning, no other paths.
- Rate limits:
  - **10 checks per minute per client IP.** This is the abuse control. Going over it returns `429` with `error: "rate_limited"`.
  - **600 checks per minute across the service.** This only protects the instance from overload. Going over it returns a friendly `429` with `error: "busy"`, the message "busy, try again shortly" and a short `Retry-After` of 15 s or less.
- Logs hold only a hashed client IP, the host and the result.

## Run and deploy

- Tests: `python test_classify.py` (classification and rate-limit checks).
- Container: `Dockerfile` (listens on `$PORT`). Deployment: `render.yaml` in the repository root (Render, auto-deploy on commit) or `fly.toml`.
- Resolver: `CHECKER_RESOLVER=auto|system|doh` (default `system` in the container). `auto` uses system DNS and falls back to DNS-over-HTTPS when the answers are fake-IP placeholders from `198.18.0.0/15`, which some egress proxies return.
- The site reads the API base URL from `data/checker-config.json` (`{"api_base": "https://…"}`).
