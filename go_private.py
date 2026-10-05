import json
import os
import time
import urllib.error
import urllib.request

UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0 Safari/537.36"
HF = os.environ["HF_TOKEN"]
PROXY = "https://api.mytemp-mail.online"
DIRECT = "https://factblink514-compiled.hf.space"


def http(method, url, body=None, headers=None):
    data = json.dumps(body).encode() if body is not None else None
    h = {"User-Agent": UA}
    h.update(headers or {})
    r = urllib.request.Request(url, method=method, headers=h, data=data)
    try:
        with urllib.request.urlopen(r, timeout=45) as resp:
            return resp.status, resp.read().decode("utf-8", "replace")[:600]
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace")[:600]
    except Exception as e:
        return 0, str(e)[:300]


out = []
st, body = http("POST", PROXY + "/api/inbox", {"custom": "proxytest"}, {"Content-Type": "application/json"})
out.append(("proxy POST /api/inbox", st, body))
st2, body2 = http("GET", PROXY + "/api/status")
out.append(("proxy GET /api/status", st2, body2[:120]))

if st in (200, 201):
    from huggingface_hub import HfApi
    api = HfApi(token=HF)
    try:
        api.update_repo_settings("factblink514/Compiled", private=True)
        out.append(("space->private", "ok"))
    except Exception as e:
        out.append(("space->private FAILED", str(e)[:300]))
    time.sleep(25)
    out.append(("direct /api/status (should be 401)", *http("GET", DIRECT + "/api/status")))
    out.append(("proxy /api/status (should work)", *http("GET", PROXY + "/api/status")))
    out.append(("proxy POST after private", *http("POST", PROXY + "/api/inbox", {"custom": "proxytest2"}, {"Content-Type": "application/json"})))
else:
    out.append(("ABORT", "proxy POST failed -> NOT going private"))

print(json.dumps(out, indent=1)[:5000])
