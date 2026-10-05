import sys

P = "public/index.html"
s = open(P, encoding="utf-8").read()
orig = s


def rep(old, new, n=1, tag=""):
    global s
    c = s.count(old)
    if c != n:
        print("FAIL [%s] count=%d expected=%d :: %r" % (tag, c, n, old[:90]))
        sys.exit(2)
    s = s.replace(old, new)
    print("ok", tag)


rep(
    '<select class="suffix" id="domainSuffix" title="Mail domain" aria-label="Mail domain">'
    '<option value="offexmail.online">@offexmail.online</option></select>',
    '<select class="suffix" id="domainSuffix" title="Mail domain" aria-label="Mail domain">'
    '<option value="">\U0001f3b2 Random (auto)</option>'
    '<option value="offexmail.online">@offexmail.online</option></select>',
    1, "select-init",
)

rep(
    "sel.innerHTML = s.domains.map(function(d){ return '<option value=\"'+esc(d)+'\">@'+esc(d)+'</option>'; }).join(\"\");",
    "sel.innerHTML = '<option value=\"\">\U0001f3b2 Random (auto)</option>' + "
    "s.domains.map(function(d){ return '<option value=\"'+esc(d)+'\">@'+esc(d)+'</option>'; }).join(\"\");",
    1, "select-status",
)

open(P, "w", encoding="utf-8").write(s)
print("changed:", s != orig, "size:", len(s))
