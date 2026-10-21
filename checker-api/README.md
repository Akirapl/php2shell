# PHP2Shell-Live-Checker API
Passive, defensive PHP banner checker. `GET /check?url=…` → JSON `{input, resolved_host, resolved_ip, php_detected, version, classification, classification_label, details, caveats, checked_at}` (+ `error`, `message` on refusal). `GET /health`.

classification ∈ likely_vulnerable | likely_patched | php_detected_version_hidden | no_php_detected | host_unreachable
Fixed: 8.5.12 / 8.4.27 / 8.3.36 / 8.2.35; < 8.2 = EOL → likely_vulnerable (+ `eol`, `distro_build_suspected` flags).

Run locally: `./run.sh` (127.0.0.1:8799). Tests: `.venv/bin/python test_classify.py`, `python3 uitest.py`.
Env: `CHECKER_RESOLVER=auto|system|doh`. auto = system DNS, but on this box DNS returns sandbox fake-IPs (198.18/15), so it falls back to DoH (dns.google / cloudflare-dns) and connects to the validated real IP.
Host anywhere with Docker: `Dockerfile` (uses `$PORT`), `render.yaml`, `fly.toml`. After deploy: set `site/data/checker-config.json` → `{"api_base":"https://<host>"}` and redeploy the site.
Safety: http/https only, ports 80/443 only, root path only, refuses private/loopback/link-local/reserved/CGNAT IPs (all resolved addresses, every redirect hop, IP pinned so DNS can't be rebound), ≤2 redirects, 8 s total, ≤4 KB body read, UA `PHP2Shell-Live-Checker/1.0`, 10/min per IP + 120/min global, logs only hashed client IP + host + result.
