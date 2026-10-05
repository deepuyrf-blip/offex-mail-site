import json
import os
import urllib.error
import urllib.request

CF = os.environ["CLOUDFLARE_API_TOKEN"]
HF = os.environ["HF_TOKEN"]
ZID = "900aba0bd69a63d84d137029b15da481"  # mytemp-mail.online
HOST = "api.mytemp-mail.online"
ORIGIN = "factblink514-compiled.hf.space"
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0 Safari/537.36"


def api(method, path, body=None):
    data = json.dumps(body).encode() if body is not None else None
    h = {"Authorization": "Bearer " + CF, "Content-Type": "application/json", "User-Agent": UA}
    r = urllib.request.Request("https://api.cloudflare.com/client/v4" + path, method=method, headers=h, data=data)
    try:
        with urllib.request.urlopen(r, timeout=45) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read())
        except Exception:
            return e.code, {"raw": "err"}
    except Exception as e:
        return 0, {"exception": str(e)}


def err(res):
    if isinstance(res, dict) and res.get("errors"):
        return res["errors"][0].get("message")
    return None


out = []

# 1) proxied CNAME (create only if missing)
st, existing = api("GET", "/zones/%s/dns_records?name=%s" % (ZID, HOST))
has = bool((existing.get("result") or [])) if isinstance(existing, dict) else False
if has:
    out.append(("cname", "already-present"))
else:
    st, res = api("POST", "/zones/%s/dns_records" % ZID,
                  {"type": "CNAME", "name": HOST, "content": ORIGIN, "proxied": True, "ttl": 1})
    out.append(("cname", st, res.get("success"), err(res)))

# 2) Origin rule: route to hf origin with the right Host/SNI (fixes the 404)
ep2 = "/zones/%s/rulesets/phases/http_request_origin/entrypoint" % ZID
st, cur2 = api("GET", ep2)
rules2 = (cur2.get("result") or {}).get("rules") or [] if isinstance(cur2, dict) else []
clean2 = [{k: r[k] for k in ("action", "action_parameters", "expression", "description", "enabled") if k in r} for r in rules2]
clean2 = [r for r in clean2 if HOST not in (r.get("expression") or "")]
clean2.append({
    "action": "route",
    "action_parameters": {"host_header": ORIGIN, "origin": {"host": ORIGIN}},
    "expression": '(http.host eq "%s")' % HOST,
    "description": "api proxy origin -> hf space",
})
st, res = api("PUT", ep2, {"rules": clean2})
out.append(("origin", st, res.get("success"), err(res)))

# 3) Transform rule: inject the HF token server-side (browser never sees it)
ep = "/zones/%s/rulesets/phases/http_request_late_transform/entrypoint" % ZID
st, cur = api("GET", ep)
rules = (cur.get("result") or {}).get("rules") or [] if isinstance(cur, dict) else []
clean = [{k: r[k] for k in ("action", "action_parameters", "expression", "description", "enabled") if k in r} for r in rules]
clean = [r for r in clean if HOST not in (r.get("expression") or "")]
clean.append({
    "action": "rewrite",
    "action_parameters": {"headers": {"Authorization": {"operation": "set", "value": "Bearer " + HF}}},
    "expression": '(http.host eq "%s")' % HOST,
    "description": "inject HF token for api proxy",
})
st, res = api("PUT", ep, {"rules": clean})
out.append(("transform", st, res.get("success"), err(res)))

print(json.dumps(out, indent=1)[:4000])
