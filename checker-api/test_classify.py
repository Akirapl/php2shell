from app import _classify
cases = [
 ({"x-powered-by":"PHP/8.3.10"}, [], "likely_vulnerable"),
 ({"x-powered-by":"PHP/8.3.36"}, [], "likely_patched"),
 ({"x-powered-by":"PHP/8.4.27"}, [], "likely_patched"),
 ({"x-powered-by":"PHP/8.5.11"}, [], "likely_vulnerable"),
 ({"x-powered-by":"PHP/8.2.7-1~deb12u1"}, [], "likely_vulnerable"),  # distro flag set
 ({"server":"Apache/2.4.52 (Ubuntu) PHP/8.1.2-1ubuntu2.14"}, [], "likely_vulnerable"),  # EOL + distro
 ({"x-powered-by":"PHP/7.4.33"}, [], "likely_vulnerable"),
 ({"x-powered-by":"PHP/8.6.0"}, [], "likely_patched"),
 ({"x-powered-by":"PHP/8.2"}, [], "php_detected_version_hidden"),
 ({"server":"nginx"}, ["PHPSESSID=abc; path=/"], "php_detected_version_hidden"),
 ({"server":"nginx", "x-powered-by":"Express"}, [], "no_php_detected"),
]
for h,c,exp in cases:
    php,v,cls,_,d = _classify(h,c)
    ok = "OK " if cls==exp else "FAIL"
    print(ok, h, c, "->", cls, v, "distro" if d.get("distro_build_suspected") else "", "EOL" if d.get("eol") else "")

# --- rate limits: per-client limit is the abuse control; the global cap answers "busy" (friendly 429) ---
import app as _app
from collections import deque as _dq
def _reset():
    _app._per_ip.clear(); _app._global.clear()
_reset()
res = [_app._allow("198.51.100.7") for _ in range(_app.PER_IP_LIMIT + 1)]
ok = all(r == (None, 0) for r in res[:-1]) and res[-1][0] == "rate_limited" and res[-1][1] >= 1
print("OK " if ok else "FAIL", f"per-client limit: {_app.PER_IP_LIMIT} allowed, then rate_limited (Retry-After {res[-1][1]}s)")
_reset()
allowed = sum(1 for i in range(_app.GLOBAL_LIMIT) if _app._allow(f"client-{i}") == (None, 0))
r = _app._allow("one-more-client")
ok = allowed == _app.GLOBAL_LIMIT and r[0] == "busy" and 1 <= r[1] <= 15
print("OK " if ok else "FAIL", f"global cap {_app.GLOBAL_LIMIT}/min reached -> busy (Retry-After {r[1]}s)")
ok = _app.GLOBAL_LIMIT >= 600 and _app.PER_IP_LIMIT == 10
print("OK " if ok else "FAIL", "limits: per-client 10/min kept, global raised to", _app.GLOBAL_LIMIT)
print("OK " if _app.CAVEATS[0] == _app.OWNERSHIP else "FAIL", "ownership notice is the first caveat")
_reset()
