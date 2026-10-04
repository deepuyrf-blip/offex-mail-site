import glob

FIXES = [
    ('rel="canonical" href="https://offexmail.online/', 'rel="canonical" href="https://mytemp-mail.online/'),
    ('property="og:url" content="https://offexmail.online/', 'property="og:url" content="https://mytemp-mail.online/'),
    ('"name":"Offex Mail","url":"https://offexmail.online/"', '"name":"Offex Mail","url":"https://mytemp-mail.online/"'),
]

total = 0
for f in glob.glob("public/**/*.html", recursive=True):
    s = open(f, encoding="utf-8").read()
    o = s
    for a, b in FIXES:
        s = s.replace(a, b)
    if s != o:
        open(f, "w", encoding="utf-8").write(s)
        total += 1
        print("fixed:", f)
print("files fixed:", total)
