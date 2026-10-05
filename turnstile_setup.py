import json
import os
import urllib.error
import urllib.request

CF = os.environ["CLOUDFLARE_API_TOKEN"]
ACC = os.environ.get("CLOUDFLARE_ACCOUNT_ID", "d33504e28650ba4603dc9cafc46d0ec9")
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


# 1) create the Turnstile widget (managed mode)
st, res = api("POST", "/accounts/%s/challenges/widgets" % ACC, {
    "name": "offex-mail",
    "domains": ["mytemp-mail.online", "www.mytemp-mail.online"],
    "mode": "managed",
})
result = res.get("result") if isinstance(res, dict) else None
print("create status:", st, "success:", res.get("success") if isinstance(res, dict) else None)
if not result:
    print("create error:", json.dumps(res)[:600])
    raise SystemExit(1)

sitekey = result.get("sitekey")
secret = result.get("secret")
print("SITEKEY:", sitekey)

# 2) push the secret straight into the Worker (never printed)
st2, res2 = api("PUT", "/accounts/%s/workers/scripts/offex-api-proxy/secrets" % ACC,
                {"name": "TURNSTILE_SECRET", "text": secret, "type": "secret_text"})
print("worker secret:", st2, (res2.get("success") if isinstance(res2, dict) else None))
