import re

# 1) i18n.js -> only el_head and banner values
p = "public/i18n.js"
s = open(p, encoding="utf-8").read()

def sub_key(s, key):
    return re.sub("(" + key + ':")([^"]*)"',
                  lambda m: m.group(1) + m.group(2).replace("100%", "85%") + '"', s)

s = sub_key(s, "el_head")
s = sub_key(s, "banner")
open(p, "w", encoding="utf-8").write(s)

# 2) elevenlabs.html -> whole page is ElevenLabs
p = "public/elevenlabs.html"
s = open(p, encoding="utf-8").read()
open(p, "w", encoding="utf-8").write(s.replace("100%", "85%"))

# 3) index.html -> only ElevenLabs/11Labs lines
p = "public/index.html"
lines = open(p, encoding="utf-8").read().split("\n")
n = 0
for i, l in enumerate(lines):
    low = l.lower()
    if ("elevenlabs" in low or "11labs" in low) and "100%" in l:
        lines[i] = l.replace("100%", "85%")
        n += 1
open(p, "w", encoding="utf-8").write("\n".join(lines))

# verify
c = open("public/i18n.js", encoding="utf-8").read()
print("index lines changed:", n)
print("el_head/banner 100% left:", len(re.findall('(?:el_head|banner):"[^"]*100%', c)))
print("elevenlabs.html 100% left:", open("public/elevenlabs.html", encoding="utf-8").read().count("100%"))
