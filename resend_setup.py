import json
import os
import time
import urllib.error
import urllib.request

RESEND = os.environ["RESEND_API_KEY"]
CF = os.environ["CLOUDFLARE_API_TOKEN"]
ZID = "5c5fca6f2e8bf44362a8ca850dbb3b76"  # offexmail.online
DOMAIN = "offexmail.online"


def req(url, method="GET", headers=None, body=None):
    data = json.dumps(body).encode() if body is not None else None
    r = urllib.request.Request(url, method=method, headers=headers or {}, data=data)
    try:
        with urllib.request.urlopen(r, timeout=45) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read())
        except Exception:
            return e.code, {"raw": "error"}


RH = {"Authorization": "Bearer " + RESEND, "Content-Type": "application/json"}
CH = {"Authorization": "Bearer " + CF, "Content-Type": "application/json"}

out = []

st, data = req("https://api.resend.com/domains", headers=RH)
dom = None
if isinstance(data, dict):
    for d in (data.get("data") or []):
        if d.get("name") == DOMAIN:
            dom = d
if not dom:
    st, data = req("https://api.resend.com/domains", "POST", RH, {"name": DOMAIN})
    out.append(("resend-create", st, data))
    dom = data if isinstance(data, dict) else {}
else:
    st, data = req("https://api.resend.com/domains/" + str(dom.get("id")), headers=RH)
    out.append(("resend-detail", st, data))
    if isinstance(data, dict) and data.get("id"):
        dom = data

out.append(("domain-id", dom.get("id"), "status", dom.get("status")))
records = dom.get("records") or []
out.append(("records", records))

for rec in records:
    nm = rec.get("name") or ""
    fqdn = nm if nm.endswith(DOMAIN) else ((nm + "." + DOMAIN) if nm else DOMAIN)
    rtype = rec.get("type")
    body = {"type": rtype, "name": fqdn, "content": rec.get("value"), "ttl": 1}
    if rtype == "MX":
        body["priority"] = rec.get("priority") or 10
    st, res = req("https://api.cloudflare.com/client/v4/zones/%s/dns_records" % ZID, "POST", CH, body)
    ok = res.get("success") if isinstance(res, dict) else None
    err = None
    if isinstance(res, dict) and res.get("errors"):
        err = res["errors"][0].get("message")
    out.append(("cf-add", rtype, fqdn, st, ok, err))

if dom.get("id"):
    st, v = req("https://api.resend.com/domains/%s/verify" % dom["id"], "POST", RH)
    out.append(("verify", st, v))
    time.sleep(25)
    st, dd = req("https://api.resend.com/domains/" + dom["id"], headers=RH)
    out.append(("final-status", dd.get("status") if isinstance(dd, dict) else dd))

print(json.dumps(out, indent=1)[:6000])
