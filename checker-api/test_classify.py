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
