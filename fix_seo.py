import os, re, glob
from PIL import Image, ImageDraw

# 1) favicon.svg
SVG = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">'
       '<rect width="100" height="100" rx="24" fill="#6d4dff"/>'
       '<path d="M22 34h56v32H22z" fill="none" stroke="white" stroke-width="6" stroke-linejoin="round"/>'
       '<path d="M24 36l26 20 26-20" fill="none" stroke="white" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/>'
       '</svg>')
open("public/favicon.svg", "w", encoding="utf-8").write(SVG)

# 2) favicon.ico
S = 256
img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
d = ImageDraw.Draw(img)
d.rounded_rectangle([0, 0, S-1, S-1], radius=int(S*0.24), fill=(109, 77, 255, 255))
k = S / 100.0
d.rectangle([(22*k, 34*k), (78*k, 66*k)], outline=(255,255,255,255), width=int(6*k))
d.line([(24*k, 36*k), (50*k, 56*k)], fill=(255,255,255,255), width=int(6*k))
d.line([(50*k, 56*k), (76*k, 36*k)], fill=(255,255,255,255), width=int(6*k))
img.save("public/favicon.ico", sizes=[(16,16),(32,32),(48,48),(64,64)])

# 3) proper <link rel=icon> on every page
ICONS = '<link rel="icon" type="image/svg+xml" href="/favicon.svg"><link rel="icon" href="/favicon.ico" sizes="any">'
changed = 0
for f in glob.glob("public/**/*.html", recursive=True):
    s = open(f, encoding="utf-8").read()
    if 'rel="icon"' in s:
        s2 = re.sub(r'<link rel="icon"[^>]*>', ICONS, s, count=1)
    else:
        m = re.search(r'<meta charset="[^"]*">', s) or re.search(r'<head[^>]*>', s)
        s2 = (s[:m.end()] + ICONS + s[m.end():]) if m else s
    if s2 != s:
        open(f, "w", encoding="utf-8").write(s2)
        changed += 1
print("icons updated:", changed)

# 4) complete sitemap.xml
urls = []
for f in sorted(glob.glob("public/**/*.html", recursive=True)):
    rel = os.path.relpath(f, "public").replace(os.sep, "/")
    if rel.endswith(".html"):
        rel = rel[:-5]
    if rel == "index":
        loc = "/"
    elif rel.endswith("/index"):
        loc = "/" + rel[:-6] + "/"
    else:
        loc = "/" + rel
    urls.append("https://mytemp-mail.online" + loc)
seen = set()
uniq = []
for u in urls:
    if u not in seen:
        seen.add(u)
        uniq.append(u)
out = ['<?xml version="1.0" encoding="UTF-8"?>',
       '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
for u in uniq:
    pr = "1.0" if u == "https://mytemp-mail.online/" else "0.8"
    out.append('  <url><loc>%s</loc><changefreq>weekly</changefreq><priority>%s</priority></url>' % (u, pr))
out.append('</urlset>')
open("public/sitemap.xml", "w", encoding="utf-8").write("\n".join(out) + "\n")
print("sitemap urls:", len(uniq))
