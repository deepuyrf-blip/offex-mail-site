import glob, os, re

# ---- 1) URL consistency: .html -> extensionless ----
for f in glob.glob("audio/*.html"):
    s = open(f, encoding="utf-8").read()
    o = s
    s = re.sub(r'(https://offexmail\.online/)([A-Za-z0-9._-]+)\.html', r'\1\2', s)
    s = s.replace('href="index.html"', 'href="/"')
    s = re.sub(r'href="([A-Za-z0-9._-]+)\.html"', r'href="\1"', s)
    if s != o:
        open(f, "w", encoding="utf-8").write(s)
        print("url-fixed:", f)

# ---- 2) keywords meta on every page ----
KW = {
 "index.html": "offex audio, free online audio tools, silence remover, remove silence from audio, remove silence from mp3, audio enhancer, clean audio online, audio noise remover, background noise remover, denoise audio, voice isolator, vocal remover, bgm remover, remove music from audio, stem splitter, vocal separation, speech enhancer, podcast audio cleaner, browser audio editor",
 "blog.html": "audio editing guides, audio editing tutorials, podcast editing guide, learn audio editing, voice recording tips",
 "about.html": "about offex audio, free online audio editor, browser audio tools",
 "contact.html": "contact offex audio, audio tool support",
 "privacy.html": "offex audio privacy policy",
 "terms.html": "offex audio terms of service",
 "remove-silence-from-audio-guide.html": "remove silence from audio, silence remover, silence cutter, trim silence from mp3, remove dead air, cut pauses from audio",
 "clean-background-noise-voice-recordings.html": "clean background noise, remove background noise from audio, noise remover, denoise voice recording, reduce audio noise, hiss remover, background noise cleaner",
 "voice-bgm-separation-explained.html": "vocal remover, voice isolator, bgm remover, remove music from audio, stem splitter, acapella maker, karaoke maker, separate voice and music, ai stem separation",
 "podcast-editing-workflow-for-beginners.html": "podcast editing, podcast editor, edit podcast audio, podcast editing workflow, podcast production",
 "record-clean-voice.html": "record clean voice, clean voice recording, how to record voice audio, home voice recording",
 "remove-echo-reverb.html": "remove echo from audio, remove reverb, de-reverb audio, echo remover, reverb remover",
 "podcast-format-settings.html": "podcast audio settings, podcast bitrate, sample rate, mono vs stereo, audio format for podcast",
 "clean-interview-audio.html": "clean interview audio, interview audio cleanup, remove noise from interview, podcast interview editing",
}
for f, kw in KW.items():
    path = "audio/" + f
    s = open(path, encoding="utf-8").read()
    tag = '<meta name="keywords" content="%s">' % kw
    if 'name="keywords"' in s:
        s = re.sub(r'<meta name="keywords" content="[^"]*">', tag, s, count=1)
    else:
        m = re.search(r'</title>', s)
        s = s[:m.end()] + "\n" + tag + s[m.end():] if m else s
    open(path, "w", encoding="utf-8").write(s)
print("keywords added")

# ---- 3) sitemap with extensionless URLs ----
urls = []
for f in sorted(glob.glob("audio/*.html")):
    name = os.path.basename(f)[:-5]
    urls.append("https://offexmail.online/" if name == "index" else "https://offexmail.online/" + name)
out = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
for u in urls:
    pr = "1.0" if u == "https://offexmail.online/" else "0.8"
    out.append('  <url><loc>%s</loc><changefreq>weekly</changefreq><priority>%s</priority></url>' % (u, pr))
out.append('</urlset>')
open("audio/sitemap.xml", "w", encoding="utf-8").write("\n".join(out) + "\n")
print("sitemap urls:", len(urls))
