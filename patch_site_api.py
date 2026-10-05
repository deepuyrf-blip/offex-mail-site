import sys

P = "public/index.html"
s = open(P, encoding="utf-8").read()
orig = s

OLD = 'var API_BASE = "https://factblink514-compiled.hf.space";'
NEW = 'var API_BASE = "https://api.mytemp-mail.online";'

c = s.count(OLD)
if c != 1:
    print("FAIL api_base count=%d" % c)
    sys.exit(2)
s = s.replace(OLD, NEW)

open(P, "w", encoding="utf-8").write(s)
print("changed:", s != orig, "size:", len(s))
