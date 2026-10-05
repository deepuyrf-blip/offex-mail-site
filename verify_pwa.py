import urllib.error
import urllib.request

UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0 Safari/537.36"


def req(url, method="GET", headers=None, data=None):
    h = {"User-Agent": UA}
    if headers:
        h.update(headers)
    r = urllib.request.Request(url, method=method, headers=h, data=data)
    try:
        with urllib.request.urlopen(r, timeout=45) as resp:
            return resp.status, resp.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace")
    except Exception as e:
        return 0, str(e)


st, h = req("https://mytemp-mail.online/")
print("site:", st, "len", len(h))
print("  manifest link:", "manifest.webmanifest" in h)
print("  turnstile widget:", "cf-turnstile" in h)
print("  sw register:", "serviceWorker" in h)
print("  install btn:", "pwaInstall" in h)

st, m = req("https://mytemp-mail.online/manifest.webmanifest")
print("manifest:", st, m[:70].replace("\n", " "))

st, s = req("https://mytemp-mail.online/sw.js")
print("sw.js:", st, "offex-pwa-v1" in s)

st, i = req("https://mytemp-mail.online/icons/icon-192.png")
print("icon-192:", st, "len", len(i))

st, b = req("https://api.mytemp-mail.online/api/inbox", "POST",
            {"Origin": "https://mytemp-mail.online", "Content-Type": "application/json"}, b"{}")
print("inbox POST (no captcha token):", st, b[:120])

st, b2 = req("https://api.mytemp-mail.online/api/status", "GET", {"Origin": "https://mytemp-mail.online"})
print("status GET:", st, b2[:80])
