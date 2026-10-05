import json
import os
import urllib.error
import urllib.request

CF = os.environ["CLOUDFLARE_API_TOKEN"]
ACC = os.environ.get("CLOUDFLARE_ACCOUNT_ID", "d33504e28650ba4603dc9cafc46d0ec9")
HF = os.environ["HF_TOKEN"]
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


st, res = api("PUT", "/accounts/%s/workers/scripts/offex-api-proxy/secrets" % ACC,
              {"name": "HF_TOKEN", "text": HF, "type": "secret_text"})
print("secret put:", st, (res.get("success") if isinstance(res, dict) else None),
      (res.get("errors") if isinstance(res, dict) else None))
