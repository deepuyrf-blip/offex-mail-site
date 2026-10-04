import os, json, urllib.request, urllib.error

TOKEN = os.environ["CLOUDFLARE_API_TOKEN"]
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


def zid(name):
    r = api("GET", "/zones?name=" + name)
    res = r.get("result") or []
    return res[0]["id"] if res else None


out = []
TARGET = "11lab.bond"

allz = api("GET", "/zones?per_page=100")
out.append("ZONES: " + json.dumps([z["name"] for z in (allz.get("result") or [])]))

info = api("GET", "/zones?name=" + TARGET)
zres = info.get("result") or []
out.append(TARGET + " zone: " + json.dumps([{"id": z["id"], "status": z["status"], "ns": z["name_servers"]} for z in zres]))
tid = zres[0]["id"] if zres else None

if tid:
    out.append("ER before: " + json.dumps(api("GET", "/zones/%s/email/routing" % tid)))
    out.append("ENABLE: " + json.dumps(api("POST", "/zones/%s/email/routing/enable" % tid)))
    out.append("ER after: " + json.dumps(api("GET", "/zones/%s/email/routing" % tid).get("result")))

tpl = None
for zn in ("offexmail.online", "mytemp-mail.online"):
    z = zid(zn)
    if z:
        ca = api("GET", "/zones/%s/email/routing/rules/catch_all" % z)
        out.append(zn + " catch_all: " + json.dumps(ca.get("result")))
        if tpl is None:
            tpl = ca.get("result")

if tid:
    action = {"type": "worker", "value": ["offex-mail-ingest"]}
    if tpl and tpl.get("actions"):
        a = tpl["actions"][0]
        if a.get("type") == "worker":
            action = {"type": "worker", "value": a.get("value") or ["offex-mail-ingest"]}
    body = {"actions": [action], "matchers": [{"type": "all"}], "enabled": True, "name": "Catch-all to worker"}
    out.append("SET catch_all: " + json.dumps(api("PUT", "/zones/%s/email/routing/rules/catch_all" % tid, body)))
    out.append("catch_all final: " + json.dumps(api("GET", "/zones/%s/email/routing/rules/catch_all" % tid).get("result")))

print("\n".join(out))
