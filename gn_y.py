import os

# ---------------------------------------------------------------------------
# gn_y.py  (runs LAST, after gn_x, in the android.yml pipeline)
#
# v4.2 changes:
#
# BUG 1 - HTML ENTITY READ AS AN OTP.
#   The reader strips tags and then decoded only a few NAMED entities, so a
#   numeric entity such as &#8203; (zero-width space) survived as literal text
#   and its digits ("8203") matched the OTP regex -> an ElevenLabs verification
#   mail that had NO code showed "VERIFICATION CODE 8203".
#   Fix: before ANY OTP detection the HTML is now entity-hardened - every
#   &#NNN; / &#xHH; pattern is removed and the common named entities are
#   decoded (deent()). This runs in strip(), in findOtp() and in the reader's
#   HTML render path, so entity text / attribute digits / CSS digits never
#   reach the detector. The precise v4.1 rule (context word required, prices /
#   years / phones / URLs / e-mail ids rejected) is preserved.
#
# BUG 2 - VERIFICATION LINK NOT TAPPABLE.
#   Anchors (<a href>) and bare URLs now become tappable and open EXTERNALLY in
#   the browser. A custom SafeUrl span is used so only http/https is ever
#   opened (other schemes are ignored). fixEmptyAnchors() gives an <a> that
#   wraps only an image / styled markup visible text (the link itself) so the
#   tap target survives image stripping. Works for both the HTML-rendered body
#   and the plain-text fallback (Linkify covers bare URLs in both).
#
# Version 4.1 -> 4.2 (versionName / versionCode / self-version / strings).
#
# Everything emitted by gn_a..gn_x is preserved: API endpoints/JSON fields, the
# mail ingest path, FCM pushes, the support feature, the bundled notification
# sounds, the bottom nav, the ad placements, the mandatory notification gate,
# the circular logo, the Create-button loading animation, the features section,
# the multi-language support and the install-analytics reporting.
# ---------------------------------------------------------------------------

BS = chr(92)   # backslash
NL = chr(10)   # newline

J   = "android/app/src/main/java/online/mytempmail/app"
RES = "android/app/src/main/res"

NEW_VERSION      = "4.2"
NEW_VERSION_CODE = "32"


def R(p):
    return open(p, encoding="utf-8").read()


def W(p, c):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w", encoding="utf-8").write(c)


# ===========================================================================
# 1 : ReaderActivity -> entity hardening + tappable links
# ===========================================================================
rp = J + "/ReaderActivity.java"
lines = R(rp).split(NL)

# --- (a) extra imports ------------------------------------------------------
IMP_ANCHOR = "import android.text.util.Linkify;"
IMP_ADD = [
    "import android.content.Intent;",
    "import android.net.Uri;",
    "import android.text.Spannable;",
    "import android.text.SpannableString;",
    "import android.text.TextPaint;",
    "import android.text.style.ClickableSpan;",
    "import android.text.style.URLSpan;",
]
out, done = [], False
for ln in lines:
    out.append(ln)
    if (not done) and ln.strip() == IMP_ANCHOR:
        out.extend(IMP_ADD)
        done = True
if not done:
    raise SystemExit("gn_y: FATAL Linkify import anchor not found")
lines = out

# --- (b) entity-hardened decode line inside strip() -------------------------
DECODE_OLD_MARK = "&nbsp;"
HARDENED = r'''        s=s.replaceAll("(?i)&#x[0-9a-f]+;"," ");
        s=s.replaceAll("&#[0-9]+;"," ");
        s=s.replace("&nbsp;"," ").replace("&amp;","&").replace("&lt;","<").replace("&gt;",">").replace("&quot;","\"").replace("&#39;","'").replace("&apos;","'").replace("&mdash;","-").replace("&ndash;","-").replace("&hellip;","...").replace("&rsquo;","'").replace("&lsquo;","'").replace("&ldquo;","\"").replace("&rdquo;","\"").replace("&bull;","*").replace("&middot;",".");'''.split(NL)
out, done = [], False
for ln in lines:
    if (not done) and ln.strip().startswith("s=s.replace(") and DECODE_OLD_MARK in ln:
        out.extend(HARDENED)
        done = True
    else:
        out.append(ln)
if not done:
    raise SystemExit("gn_y: FATAL strip() decode line not found")
lines = out

# --- (c) deent() call inside findOtp() before the OTP regex -----------------
out, done = [], False
for ln in lines:
    out.append(ln)
    if (not done) and ln.strip().startswith("src=src.replaceAll") and "[^>]+" in ln:
        out.append("            src=deent(src);")
        done = True
if not done:
    raise SystemExit("gn_y: FATAL findOtp tag-strip line not found")
lines = out

# --- (d) render(): fix anchors that wrap only an image ----------------------
out, done = [], False
for ln in lines:
    if (not done) and "<(link|meta|svg|img|iframe" in ln:
        out.append("                cleaned=fixEmptyAnchors(cleaned);")
        done = True
    out.append(ln)
if not done:
    raise SystemExit("gn_y: FATAL render() img-strip line not found")
lines = out

# --- (e) onCreate(): linkify the body ---------------------------------------
start = end = None
for i, ln in enumerate(lines):
    if start is None and ln.strip() == "bodyBox.setText(body);":
        start = i
    if start is not None and "Linkify.addLinks(bodyBox" in ln:
        end = i
        break
if start is None or end is None or end < start:
    raise SystemExit("gn_y: FATAL reader link-setup block not found")
NEW_SET = [
    "                    bodyBox.setText(linkify(body));",
    "                    bodyBox.setMovementMethod(LinkMovementMethod.getInstance());",
    "                    bodyBox.setLinksClickable(true);",
]
lines = lines[:start] + NEW_SET + lines[end + 1:]

s = NL.join(lines)

# --- (f) helper methods, inserted before the final class brace --------------
HELPERS = r'''
    // ---- HTML entity hardening (BUG 1) --------------------------------------
    // Remove/decode HTML entities BEFORE any OTP detection, so entity text such
    // as &#8203; (zero-width space) can never be read as a code. The entity
    // marker is dropped before its digits can reach the OTP regex.
    private static String deent(String s){
        if(s==null) return "";
        s=s.replaceAll("(?i)&#x[0-9a-f]+;"," ");
        s=s.replaceAll("&#[0-9]+;"," ");
        s=s.replace("&nbsp;"," ").replace("&amp;","&").replace("&lt;","<").replace("&gt;",">")
           .replace("&quot;","\"").replace("&#39;","'").replace("&apos;","'")
           .replace("&mdash;","-").replace("&ndash;","-").replace("&hellip;","...")
           .replace("&rsquo;","'").replace("&lsquo;","'").replace("&ldquo;","\"").replace("&rdquo;","\"")
           .replace("&bull;","*").replace("&middot;",".");
        return s;
    }

    // ---- link handling (BUG 2) ---------------------------------------------
    // Anchors and bare URLs become tappable and open EXTERNALLY in the browser.
    // Only http/https is ever opened; any other scheme is ignored.
    static class SafeUrl extends ClickableSpan {
        private final String url;
        SafeUrl(String u){ url=u; }
        @Override public void onClick(View w){
            try {
                String u=url;
                if(u==null) return;
                if(!(u.startsWith("http://")||u.startsWith("https://"))) return;
                Intent i=new Intent(Intent.ACTION_VIEW,Uri.parse(u));
                i.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
                w.getContext().startActivity(i);
            } catch(Exception e){}
        }
        @Override public void updateDrawState(TextPaint ds){
            super.updateDrawState(ds);
            ds.setUnderlineText(true);
            ds.setColor(0xFF1565C0);
        }
    }

    private static CharSequence linkify(CharSequence text){
        try {
            SpannableString ss=new SpannableString(text==null?"":text);
            java.util.ArrayList<int[]> pos=new java.util.ArrayList<int[]>();
            java.util.ArrayList<String> urls=new java.util.ArrayList<String>();
            URLSpan[] pre=ss.getSpans(0,ss.length(),URLSpan.class);
            for(URLSpan sp:pre){ pos.add(new int[]{ss.getSpanStart(sp),ss.getSpanEnd(sp)}); urls.add(sp.getURL()==null?"":sp.getURL()); }
            try { Linkify.addLinks(ss,Linkify.WEB_URLS); } catch(Exception e){}
            URLSpan[] post=ss.getSpans(0,ss.length(),URLSpan.class);
            for(URLSpan sp:post){ pos.add(new int[]{ss.getSpanStart(sp),ss.getSpanEnd(sp)}); urls.add(sp.getURL()==null?"":sp.getURL()); ss.removeSpan(sp); }
            for(URLSpan sp:pre){ ss.removeSpan(sp); }
            java.util.HashSet<String> seen=new java.util.HashSet<String>();
            for(int i=0;i<pos.size();i++){
                int a=pos.get(i)[0], b=pos.get(i)[1]; String u=urls.get(i);
                if(a<0||b<=a) continue;
                if(!seen.add(a+":"+b+":"+u)) continue;
                if(u.startsWith("http://")||u.startsWith("https://")){
                    ss.setSpan(new SafeUrl(u),a,b,Spannable.SPAN_EXCLUSIVE_EXCLUSIVE);
                }
            }
            return ss;
        } catch(Exception e){ return text; }
    }

    // An email "button" is often an <a> wrapping only an image or styled markup.
    // Give such anchors visible, tappable text (the link itself) so the tap
    // target survives image stripping.
    private static String fixEmptyAnchors(String html){
        try {
            Pattern p=Pattern.compile("(?is)<a\\b([^>]*)>(.*?)</a>");
            Matcher m=p.matcher(html);
            StringBuffer sb=new StringBuffer();
            while(m.find()){
                String attrs=m.group(1), inner=m.group(2);
                String visible=inner.replaceAll("(?is)<[^>]+>","").replace("&nbsp;"," ").trim();
                String repl=m.group(0);
                if(visible.isEmpty()){
                    String href="";
                    Matcher hm=Pattern.compile("(?is)href\\s*=\\s*[\"']([^\"']+)[\"']").matcher(attrs);
                    if(hm.find()) href=hm.group(1);
                    String label=href.isEmpty()?"Open link":href;
                    repl="<a"+attrs+">"+label+"</a>";
                }
                m.appendReplacement(sb,Matcher.quoteReplacement(repl));
            }
            m.appendTail(sb);
            return sb.toString();
        } catch(Exception e){ return html; }
    }
'''
s2 = s.rstrip()
if not s2.endswith("}"):
    raise SystemExit("gn_y: FATAL class closing brace not found")
s = s2[:-1] + HELPERS + NL + "}" + NL
W(rp, s)
print("Y: ReaderActivity -> entity hardening (deent) + tappable http/https links (SafeUrl)")

# ===========================================================================
# 2 : version 4.1 -> 4.2  (build.gradle, Config.java, SupportActivity.java)
# ===========================================================================
bp = "android/app/build.gradle"
s = R(bp)
s = s.replace('versionName "4.1"', 'versionName "4.2"')
s = s.replace('versionCode 31', 'versionCode 32')
W(bp, s)

cp = J + "/Config.java"
s = R(cp)
s = s.replace('latest.equals("4.1")', 'latest.equals("4.2")')
s = s.replace('latest.equals("4.0")', 'latest.equals("4.2")')
W(cp, s)

sp = J + "/SupportActivity.java"
s = R(sp)
s = s.replace('public static final String VERSION = "4.1";',
              'public static final String VERSION = "4.2";')
s = s.replace('public static final String VERSION = "4.0";',
              'public static final String VERSION = "4.2";')
W(sp, s)
print("Y: version 4.1 -> 4.2 (build.gradle / Config.java / SupportActivity.java)")

# ===========================================================================
# 3 : version-bearing strings in every locale (about_version, admin_latest_hint)
# ===========================================================================
def bump_version_key(xml, key):
    a = xml.find('<string name="' + key + '">')
    if a < 0:
        return xml
    b = xml.find("</string>", a)
    seg = xml[a:b]
    seg2 = seg.replace("4.1", "4.2")
    return xml[:a] + seg2 + xml[b:]

for loc in ["values", "values-hi", "values-es", "values-pt", "values-ar", "values-ru", "values-in"]:
    p = RES + "/" + loc + "/strings.xml"
    if not os.path.exists(p):
        continue
    t = R(p)
    t = bump_version_key(t, "about_version")
    t = bump_version_key(t, "admin_latest_hint")
    W(p, t)
    print("Y: %s/strings.xml -> version 4.2" % loc)

print("Y: applied v4.2 (entity-hardened OTP detection; tappable links; version 4.1 -> 4.2)")
