import os

# ---------------------------------------------------------------------------
# gn_x.py  (runs LAST, after gn_w, in the android.yml pipeline)
#
# v4.1 change - PRECISE OTP DETECTION:
#   The reader used to fall back to "the first standalone 4-8 digit number" when
#   no keyword was found, so it flagged toll-free numbers, prices, years and
#   order ids as OTPs ("ye har kisi ko OTP samajh raha"). findOtp now:
#     * only accepts a 4-8 digit code that stands alone (not glued to more
#       digits, and not a price/amount/percentage or a bare year), AND
#     * only when an OTP-indicating word sits near it (code / otp / pin /
#       verification / one-time ... in English, Hinglish and Hindi), and
#     * picks the candidate closest to its context word when several qualify.
#   This matches the backend detect_otp() and the website detectOtp() exactly.
#
#   Version 4.0 -> 4.1 (versionName / versionCode / self-version / strings).
#
# Everything emitted by gn_a..gn_w is preserved: API endpoints/JSON fields, the
# mail ingest path, FCM pushes, the support feature, the bundled notification
# sounds, the bottom nav, the ad placements, the mandatory notification gate,
# the circular logo, the Create-button loading animation, the features section,
# the multi-language support and the install-analytics reporting.
# ---------------------------------------------------------------------------

BS = chr(92)   # backslash
NL = chr(10)   # newline

J   = "android/app/src/main/java/online/mytempmail/app"
RES = "android/app/src/main/res"

NEW_VERSION      = "4.1"
NEW_VERSION_CODE = "31"


def R(p):
    return open(p, encoding="utf-8").read()


def W(p, c):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w", encoding="utf-8").write(c)


# --- the new OTP pattern declarations (replaces the old single Pattern line) --
OTP_DECL = r'''    private static final Pattern OTP=Pattern.compile("@BS@@BS@d{4,8}");
    private static final Pattern OTPCTX=Pattern.compile(
        "(?:@BS@@BS@b(?:otp|code|pin|passcode|password|verification|verify|verifying|auth|authentication)@BS@@BS@b"
        + "|one[@BS@@BS@s-]?time(?:[@BS@@BS@s-]?(?:code|pin|password))?"
        + "|security@BS@@BS@s+code|confirmation@BS@@BS@s+code|login@BS@@BS@s+code|access@BS@@BS@s+code"
        + "|@BS@u0938@BS@u0924@BS@u094d@BS@u092f@BS@u093e@BS@u092a@BS@u0928|@BS@u0915@BS@u094b@BS@u0921|@BS@u0913@BS@u091f@BS@u0940@BS@u092a@BS@u0940"
        + "|@BS@u0935@BS@u0947@BS@u0930@BS@u093f@BS@u092b@BS@u093f@BS@u0915@BS@u0947@BS@u0936@BS@u0928|@BS@u092a@BS@u093f@BS@u0928|@BS@u092a@BS@u093e@BS@u0938@BS@u0915@BS@u094b@BS@u0921)",
        Pattern.CASE_INSENSITIVE);'''.replace("@BS@", BS)

# --- the new findOtp() method ------------------------------------------------
FINDOTP = r'''    private static String findOtp(String html,String txt){
        try {
            String plain=strip(html==null?"":html);
            String src=(plain!=null&&!plain.trim().isEmpty())?plain:(txt==null?"":txt);
            src=src.replaceAll("(?is)<[^>]+>"," ");
            src=src.replaceAll("(?i)@BS@@BS@b(?:https?://|www@BS@@BS@.)@BS@@BS@S+"," ");
            src=src.replaceAll("(?i)@BS@@BS@b[@BS@@BS@w.+-]+@[@BS@@BS@w-]+@BS@@BS@.[@BS@@BS@w.-]+"," ");
            java.util.ArrayList<int[]> ctx=new java.util.ArrayList<int[]>();
            java.util.regex.Matcher cm=OTPCTX.matcher(src);
            while(cm.find()) ctx.add(new int[]{cm.start(),cm.end()});
            java.util.regex.Matcher m=OTP.matcher(src);
            String bestCode=null; int bestScore=Integer.MIN_VALUE; int bestStart=Integer.MAX_VALUE;
            while(m.find()){
                int s=m.start(), e=m.end();
                String code=m.group();
                if(s>0&&Character.isDigit(src.charAt(s-1))) continue;
                if(e<src.length()&&Character.isDigit(src.charAt(e))) continue;
                if(s>0){ char p=src.charAt(s-1); if("@BS@u20b9$@BS@u20ac@BS@u00a3@BS@u00a5".indexOf(p)>=0||p=='%') continue; }
                if(s>1&&(src.charAt(s-1)==','||src.charAt(s-1)=='.')&&Character.isDigit(src.charAt(s-2))) continue;
                if(e<src.length()&&src.charAt(e)=='%') continue;
                if(e+1<src.length()&&(src.charAt(e)==','||src.charAt(e)=='.')&&Character.isDigit(src.charAt(e+1))) continue;
                int dist=Integer.MAX_VALUE;
                for(int i=0;i<ctx.size();i++){
                    int cs=ctx.get(i)[0], ce=ctx.get(i)[1];
                    if(ce<=s){ int d=s-ce; if(d<=40&&d<dist) dist=d; }
                    else if(cs>=e){ int d=cs-e; if(d<=20&&d<dist) dist=d; }
                }
                if(dist==Integer.MAX_VALUE) continue;
                if(code.length()==4){
                    int n=Integer.parseInt(code);
                    if(n>=1900&&n<=2099){
                        boolean near=false;
                        for(int i=0;i<ctx.size();i++){ if(ctx.get(i)[1]<=s&&s-ctx.get(i)[1]>=0&&s-ctx.get(i)[1]<=12){ near=true; break; } }
                        if(!near) continue;
                    }
                }
                int score=1000-dist;
                if(score>bestScore||(score==bestScore&&s<bestStart)){ bestScore=score; bestStart=s; bestCode=code; }
            }
            return bestCode;
        } catch(Exception e){ return null; }
    }
    '''.replace("@BS@", BS)

# ===========================================================================
# 1 : ReaderActivity -> precise OTP detection
# ===========================================================================
rp = J + "/ReaderActivity.java"
lines = R(rp).split(NL)
out, done = [], False
for ln in lines:
    if (not done) and ("Pattern OTP=Pattern.compile(" in ln):
        out.append(OTP_DECL)
        done = True
    else:
        out.append(ln)
if not done:
    raise SystemExit("gn_x: FATAL OTP pattern declaration not found")
s = NL.join(out)
a = s.index("private static String findOtp(String html,String txt){")
b = s.index("private static String strip(String h){")
s = s[:a] + FINDOTP + s[b:]
W(rp, s)
print("X: ReaderActivity -> precise OTP detection (context required, prices/years/ids rejected)")

# ===========================================================================
# 2 : version 4.0 -> 4.1  (build.gradle, Config.java, SupportActivity.java)
# ===========================================================================
bp = "android/app/build.gradle"
s = R(bp)
s = s.replace('versionName "4.0"', 'versionName "4.1"')
s = s.replace('versionCode 30', 'versionCode 31')
W(bp, s)

cp = J + "/Config.java"
s = R(cp)
s = s.replace('latest.equals("4.0")', 'latest.equals("4.1")')
s = s.replace('latest.equals("3.9")', 'latest.equals("4.1")')
W(cp, s)

sp = J + "/SupportActivity.java"
s = R(sp)
s = s.replace('public static final String VERSION = "4.0";',
              'public static final String VERSION = "4.1";')
s = s.replace('public static final String VERSION = "3.9";',
              'public static final String VERSION = "4.1";')
W(sp, s)
print("X: version 4.0 -> 4.1 (build.gradle / Config.java / SupportActivity.java)")

# ===========================================================================
# 3 : version-bearing strings in every locale (about_version, admin_latest_hint)
# ===========================================================================
def bump_version_key(xml, key):
    a = xml.find('<string name="' + key + '">')
    if a < 0:
        return xml
    b = xml.find("</string>", a)
    seg = xml[a:b]
    seg2 = seg.replace("4.0", "4.1")
    return xml[:a] + seg2 + xml[b:]

for loc in ["values", "values-hi", "values-es", "values-pt", "values-ar", "values-ru", "values-in"]:
    p = RES + "/" + loc + "/strings.xml"
    if not os.path.exists(p):
        continue
    t = R(p)
    t = bump_version_key(t, "about_version")
    t = bump_version_key(t, "admin_latest_hint")
    W(p, t)
    print("X: %s/strings.xml -> version 4.1" % loc)

print("X: applied v4.1 (precise OTP detection; version 4.0 -> 4.1)")
