import json
import os
import urllib.error
import urllib.request

TOKEN = os.environ["CLOUDFLARE_API_TOKEN"]
ZID = "5c5fca6f2e8bf44362a8ca850dbb3b76"  # offexmail.online
BASE = "https://api.cloudflare.com/client/v4"


def api(method, path, body=None):
    req = urllib.request.Request(
        BASE + path, method=method,
        headers={"Authorization": "Bearer " + TOKEN, "Content-Type": "application/json"},
        data=json.dumps(body).encode() if body is not None else None,
    )
    try:
        with urllib.request.urlopen(req, timeout=45) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        try:
            return json.loads(e.read())
        except Exception:
            return {"http_error": e.code}


ep = "/zones/%s/rulesets/phases/http_request_dynamic_redirect/entrypoint" % ZID
cur = api("GET", ep)
rules = (cur.get("result") or {}).get("rules") or []
print("EXISTING:", json.dumps([{"expr": r.get("expression"), "desc": r.get("description")} for r in rules]))

new_rule = {
    "action": "redirect",
    "action_parameters": {"from_value": {
        "status_code": 301,
        "target_url": {"expression": 'concat("https://offexmail.online", http.request.uri.path)'},
        "preserve_query_string": True,
    }},
    "expression": '(http.host eq "audio.offexmail.online") or (http.host eq "audia.offexmail.online")',
    "description": "audio/audia subdomain -> offexmail.online",
}

clean = []
for r in rules:
    c = {k: r[k] for k in ("action", "action_parameters", "expression", "description", "enabled") if k in r}
    clean.append(c)

if not any("audio.offexmail.online" in (r.get("expression") or "") for r in clean):
    clean.append(new_rule)
    print("adding new rule")
else:
    print("audio rule already present")

res = api("PUT", ep, {"rules": clean})
print("PUT success:", res.get("success"), "errors:", json.dumps(res.get("errors")))

after = api("GET", ep)
print("AFTER:", json.dumps([{"expr": r.get("expression"), "desc": r.get("description"), "target": (((r.get("action_parameters") or {}).get("from_value") or {}).get("target_url"))} for r in ((after.get("result") or {}).get("rules") or [])]))
