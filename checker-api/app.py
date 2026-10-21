"""PHP2Shell-Live-Checker: a SAFE, passive PHP version-disclosure checker.

Defensive only. For one user-supplied URL it sends a single ordinary GET to the
ROOT path ("/") exactly like a browser, follows at most 2 redirects, and reads
only what the server voluntarily discloses: the Server / X-Powered-By headers
and whether a PHPSESSID cookie is set. It never sends payloads, never probes
other paths or ports, never scans.
"""
import hashlib, http.client, ipaddress, json, logging, os, re, socket, ssl, threading, time
import urllib.request
from collections import deque
from datetime import datetime, timezone
from urllib.parse import urlsplit, urljoin

from fastapi import FastAPI, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

UA = "PHP2Shell-Live-Checker/1.0 (defensive version check; +https://php2shell-live.surge.sh)"
TOTAL_TIMEOUT = 8.0
MAX_REDIRECTS = 2
MAX_BODY = 4096            # we read at most this many body bytes, then hang up
ALLOWED_PORTS = {80, 443}  # no arbitrary ports -> cannot be used as a port scanner
PER_IP_LIMIT, PER_IP_WINDOW = 10, 60
GLOBAL_LIMIT, GLOBAL_WINDOW = 120, 60

# Fixed upstream releases per branch (PHP2Shell advisories).
FIXED = {(8, 5): (8, 5, 12), (8, 4): (8, 4, 27), (8, 3): (8, 3, 36), (8, 2): (8, 2, 35)}

CAVEATS = [
    "This only reads the public banner (Server / X-Powered-By headers). It does not and cannot verify actual patch status.",
    "A hidden or missing banner is NOT evidence of safety. Many patched and unpatched servers hide their version (expose_php=Off).",
    "Linux distributions (Debian, Ubuntu, RHEL/AlmaLinux/Rocky, SUSE) backport security fixes WITHOUT changing the upstream version string, so a version that looks old may actually be fixed. Check your distro's security tracker / package changelog.",
    "Reverse proxies, CDNs and WAFs can strip, rewrite or fake these headers; the banner may describe a different machine than the one running your application.",
    "PHP below 8.2 is end-of-life upstream and receives no official fix; only a distro or vendor with extended support could have patched it.",
    "The only reliable check is on the server itself: `php -v` plus your package manager's changelog, against the official advisory.",
]

log = logging.getLogger("checker")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")

app = FastAPI(title="PHP2Shell-Live-Checker", version="1.0", docs_url=None, redoc_url=None, openapi_url=None)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://php2shell-live.surge.sh", "https://akirapl.github.io", "http://127.0.0.1:8765", "http://localhost:8765"],
    allow_origin_regex=r"https://[a-z0-9-]+\.surge\.sh",
    allow_methods=["GET"], allow_headers=["*"], max_age=600,
)

# ---------------------------------------------------------------- rate limits
_lock = threading.Lock()
_per_ip: dict = {}
_global: deque = deque()

def _allow(ip: str) -> bool:
    now = time.monotonic()
    with _lock:
        while _global and now - _global[0] > GLOBAL_WINDOW:
            _global.popleft()
        q = _per_ip.setdefault(ip, deque())
        while q and now - q[0] > PER_IP_WINDOW:
            q.popleft()
        if len(q) >= PER_IP_LIMIT or len(_global) >= GLOBAL_LIMIT:
            return False
        q.append(now); _global.append(now)
        if len(_per_ip) > 10000:  # bound memory
            for k in [k for k, v in _per_ip.items() if not v][:5000]:
                _per_ip.pop(k, None)
        return True

def _client_ip(req: Request) -> str:
    # The app listens on 127.0.0.1 only; the tunnel appends the real peer as the
    # LAST X-Forwarded-For hop, so take the rightmost value (client cannot forge it).
    xff = req.headers.get("x-forwarded-for")
    if xff:
        return xff.split(",")[-1].strip()
    return req.headers.get("x-real-ip") or (req.client.host if req.client else "?")

# --------------------------------------------------------------- SSRF guards
class Refused(Exception):
    def __init__(self, code, msg):
        super().__init__(msg); self.code = code; self.msg = msg

_HOST_RE = re.compile(r"^(?=.{1,253}$)([a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?)(\.[a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?)*$")

def _ip_ok(ip: ipaddress._BaseAddress) -> bool:
    if isinstance(ip, ipaddress.IPv6Address) and ip.ipv4_mapped:
        ip = ip.ipv4_mapped
    if (ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_multicast or ip.is_reserved
            or ip.is_unspecified or not ip.is_global):
        return False
    # explicit belt-and-braces ranges (CGNAT, benchmarking, 6to4/teredo, NAT64, docs)
    for net in ("100.64.0.0/10", "198.18.0.0/15", "192.0.0.0/24", "192.0.2.0/24", "198.51.100.0/24",
                "203.0.113.0/24", "240.0.0.0/4", "0.0.0.0/8", "2002::/16", "2001::/32", "64:ff9b::/96",
                "fc00::/7", "fe80::/10", "::/128", "::1/128"):
        n = ipaddress.ip_network(net)
        if ip.version == n.version and ip in n:
            return False
    return True

RESOLVER = os.environ.get("CHECKER_RESOLVER", "auto")  # auto | system | doh
_FAKE_IP = ipaddress.ip_network("198.18.0.0/15")  # sandbox egress fake-IP DNS
_DOH = ["https://dns.google/resolve", "https://cloudflare-dns.com/dns-query"]

def _doh(host):
    out = set()
    for qtype in ("A", "AAAA"):
        for ep in _DOH:
            try:
                req = urllib.request.Request(f"{ep}?name={host}&type={qtype}",
                                             headers={"Accept": "application/dns-json", "User-Agent": UA})
                with urllib.request.urlopen(req, timeout=3) as r:
                    data = json.loads(r.read(65536))
                for a in data.get("Answer", []):
                    if a.get("type") in (1, 28):
                        out.add(ipaddress.ip_address(a["data"]))
                break
            except Exception:
                continue
    return list(out)

def _resolve(host, port):
    """System DNS; if it returns only sandbox fake-IPs (or RESOLVER=doh), ask a public
    DNS-over-HTTPS resolver for the real records. Every address is validated by the caller
    and the connection is pinned to a validated address (no DNS-rebinding window)."""
    addrs = []
    if RESOLVER != "doh":
        try:
            infos = socket.getaddrinfo(host, port, proto=socket.IPPROTO_TCP)
            addrs = list({ipaddress.ip_address(i[4][0].split("%")[0]) for i in infos})
        except socket.gaierror:
            addrs = []
    if RESOLVER == "doh" or (RESOLVER == "auto" and (not addrs or all(a in _FAKE_IP for a in addrs))):
        addrs = _doh(host)
    if not addrs:
        raise Refused("unresolvable", "Hostname does not resolve.")
    return addrs

def _validate(url: str):
    """Returns (scheme, host, port, pinned_ip) or raises Refused."""
    try:
        u = urlsplit(url)
    except ValueError:
        raise Refused("bad_url", "Malformed URL.")
    scheme = (u.scheme or "").lower()
    if scheme not in ("http", "https"):
        raise Refused("bad_scheme", "Only http:// and https:// URLs are allowed.")
    if u.username or u.password:
        raise Refused("bad_url", "Credentials in URLs are not allowed.")
    host = (u.hostname or "").rstrip(".").lower()
    try:
        port = u.port or (443 if scheme == "https" else 80)
    except ValueError:
        raise Refused("bad_url", "Invalid port.")
    if port not in ALLOWED_PORTS:
        raise Refused("bad_port", "Only the default ports 80/443 are checked.")
    if not host:
        raise Refused("bad_url", "Missing hostname.")
    if host == "localhost" or host.endswith((".localhost", ".local", ".internal", ".lan", ".home.arpa", ".onion")):
        raise Refused("blocked_host", "Local / internal hostnames are refused.")
    try:
        literal = ipaddress.ip_address(host)
    except ValueError:
        literal = None
        try:
            host.encode("idna")
        except Exception:
            raise Refused("bad_url", "Invalid hostname.")
        if not _HOST_RE.match(host.encode("idna").decode()) or "." not in host:
            raise Refused("bad_url", "Invalid hostname (a public domain name is required).")
    if literal is not None:
        addrs = [literal]
    else:
        addrs = _resolve(host.encode("idna").decode(), port)
    if not addrs:
        raise Refused("unresolvable", "Hostname does not resolve.")
    # refuse if ANY resolved address is non-public (defeats mixed-record tricks)
    if not all(_ip_ok(a) for a in addrs):
        raise Refused("blocked_ip", "Target resolves to a private, loopback, link-local or reserved address; refused.")
    pinned = sorted(addrs, key=lambda a: a.version)[0]  # prefer IPv4
    return scheme, host, port, str(pinned)

# ---------------------------------------------------- pinned-IP HTTP(S) fetch
class _PinnedHTTP(http.client.HTTPConnection):
    def __init__(self, host, ip, port, timeout):
        super().__init__(host, port, timeout=timeout); self._ip = ip
    def connect(self):
        self.sock = socket.create_connection((self._ip, self.port), self.timeout)

class _PinnedHTTPS(http.client.HTTPSConnection):
    def __init__(self, host, ip, port, timeout):
        super().__init__(host, port, timeout=timeout, context=ssl.create_default_context()); self._ip = ip
    def connect(self):
        raw = socket.create_connection((self._ip, self.port), self.timeout)
        self.sock = self._context.wrap_socket(raw, server_hostname=self.host)

def _fetch_root(url: str, deadline: float):
    hops = []
    current = url
    for hop in range(MAX_REDIRECTS + 1):
        scheme, host, port, ip = _validate(current)  # re-checked on every hop
        remaining = deadline - time.monotonic()
        if remaining <= 0.2:
            raise TimeoutError("total timeout")
        path = urlsplit(current).path or "/"
        if hop == 0:
            path = "/"  # the user's URL: root only, never a supplied path or query
        cls = _PinnedHTTPS if scheme == "https" else _PinnedHTTP
        conn = cls(host, ip, port, timeout=min(remaining, TOTAL_TIMEOUT))
        try:
            conn.request("GET", path, headers={
                "Host": host if port in (80, 443) else f"{host}:{port}",
                "User-Agent": UA, "Accept": "text/html,*/*;q=0.5",
                "Accept-Encoding": "identity", "Connection": "close"})
            r = conn.getresponse()
            r.read(MAX_BODY)  # cap; we do not parse the body
            headers = {k.lower(): v for k, v in r.getheaders() if k.lower() != "set-cookie"}
            cookies = r.msg.get_all("Set-Cookie") or []
            hops.append({"url": f"{scheme}://{host}{'' if port in (80, 443) else ':'+str(port)}{path}",
                         "ip": ip, "status": r.status})
            if r.status in (301, 302, 303, 307, 308) and r.getheader("Location"):
                if hop == MAX_REDIRECTS:
                    return r.status, headers, cookies, hops, True
                nxt = urljoin(f"{scheme}://{host}{path}", r.getheader("Location"))
                current = nxt.split("#")[0]
                continue
            return r.status, headers, cookies, hops, False
        finally:
            conn.close()

# ------------------------------------------------------------ classification
_PHP_RE = re.compile(r"PHP/(\d+)\.(\d+)(?:\.(\d+))?([^\s;,()]*)", re.I)
_DISTRO_RE = re.compile(r"(deb\d*u?\d*|ubuntu|\+deb|~deb|\.el\d|el\d+|suse|sury|\-\d+[a-z~+])", re.I)

def _classify(headers: dict, cookies: list):
    xpb = headers.get("x-powered-by", "")
    server = headers.get("server", "")
    phpsess = any(c.strip().upper().startswith("PHPSESSID=") for c in cookies)
    m = _PHP_RE.search(xpb) or _PHP_RE.search(server)
    php_hint = bool(m) or "php" in xpb.lower() or "php" in server.lower() or phpsess
    details = {"server_header": server or None, "x_powered_by": xpb or None, "phpsessid_cookie": phpsess}
    if not m:
        if php_hint:
            return True, None, "php_detected_version_hidden", "PHP detected but version hidden - unknown", details
        return False, None, "no_php_detected", "no PHP detected / unknown", details
    maj, mnr, pat = int(m.group(1)), int(m.group(2)), int(m.group(3) or 0)
    suffix = m.group(4) or ""
    version = f"{maj}.{mnr}.{pat}" if m.group(3) else f"{maj}.{mnr}"
    distro = bool(suffix and _DISTRO_RE.search(suffix)) or bool(re.search(r"debian|ubuntu|red hat|centos|rhel|almalinux|rocky|suse", server, re.I))
    details["raw_version_string"] = m.group(0)
    details["distro_build_suspected"] = distro
    v = (maj, mnr, pat)
    if (maj, mnr) in FIXED:
        fx = FIXED[(maj, mnr)]
        details["fixed_in_branch"] = ".".join(map(str, fx))
        if not m.group(3):
            details["note"] = "Only major.minor is disclosed; patch level unknown."
            return True, version, "php_detected_version_hidden", "PHP detected but version hidden - unknown", details
        if v >= fx:
            return True, version, "likely_patched", "likely patched version", details
        details["note"] = ("Upstream version is older than the fix" +
                           ("; distro build suspected - may be backported, verify with your distro tracker." if distro else "."))
        return True, version, "likely_vulnerable", "likely vulnerable version", details
    if (maj, mnr) > (8, 5):
        details["note"] = "Branch newer than any affected branch listed in the advisories."
        return True, version, "likely_patched", "likely patched version", details
    details["note"] = ("PHP < 8.2 is end-of-life upstream: no official fix exists" +
                       ("; distro build suspected - an extended-support backport is possible, verify with your vendor." if distro else "."))
    details["eol"] = True
    return True, version, "likely_vulnerable", "likely vulnerable version", details

# ------------------------------------------------------------------ endpoints
@app.get("/health")
def health():
    return {"ok": True, "service": "PHP2Shell-Live-Checker", "version": "1.0"}

@app.get("/check")
def check(request: Request, url: str = Query(..., max_length=2048)):
    now = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
    ip = _client_ip(request)
    ip_tag = hashlib.sha256(ip.encode()).hexdigest()[:10]
    base = {"input": url, "resolved_host": None, "php_detected": False, "version": None,
            "classification": None, "classification_label": None, "details": {}, "caveats": CAVEATS, "checked_at": now}
    if not _allow(ip):
        log.info("ratelimited client=%s", ip_tag)
        return JSONResponse({**base, "error": "rate_limited", "message": "Too many checks; try again in a minute."},
                            status_code=429, headers={"Retry-After": "60"})
    u = url.strip()
    if "://" not in u:
        u = "https://" + u
    deadline = time.monotonic() + TOTAL_TIMEOUT
    try:
        status, headers, cookies, hops, too_many = _fetch_root(u, deadline)
    except Refused as e:
        if e.code == "unresolvable":
            return JSONResponse({**base, "classification": "host_unreachable", "classification_label": "host unreachable",
                                 "error": e.code, "message": e.msg, "details": {"reason": "dns"}}, status_code=200)
        log.info("refused client=%s code=%s", ip_tag, e.code)
        return JSONResponse({**base, "error": e.code, "message": e.msg}, status_code=400)
    except (OSError, TimeoutError, http.client.HTTPException, ssl.SSLError) as e:
        host = urlsplit(u).hostname
        log.info("unreachable client=%s host=%s", ip_tag, host)
        return {**base, "resolved_host": host, "classification": "host_unreachable",
                "classification_label": "host unreachable", "details": {"reason": type(e).__name__}}
    php, version, cls, label, details = _classify(headers, cookies)
    details["http_status"] = status
    details["hops"] = hops
    if too_many:
        details["redirects_truncated"] = True
    log.info("checked client=%s host=%s cls=%s", ip_tag, hops[-1]["url"].split("/")[2], cls)
    return {**base, "resolved_host": hops[-1]["url"].split("/")[2], "resolved_ip": hops[-1]["ip"],
            "php_detected": php, "version": version, "classification": cls,
            "classification_label": label, "details": details}
