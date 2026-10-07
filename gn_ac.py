# ============================================================================
#  gn_ac.py  -  v4.6  (NEW LAST WRITER, runs after gn_ab)
# ============================================================================
#  Applies the "offex_exact_reference_ui" patch so the home screen matches the
#  futuristic reference screenshot EXACTLY, while preserving every existing
#  view id / click handler / feature.
#
#  What this writer does:
#    * writes the patch's 8 drawables (screen_bg, inner, card, gradient_cta,
#      pill_live, bottom_nav, active_nav, delete) into res/drawable/,
#    * adds the patch's palette additions to colors.xml (existing names kept),
#    * nudges themes.xml to the reference dark navy,
#    * rewrites activity_main.xml to the reference structure (header -> address
#      card -> create card -> inbox -> native ad -> switch -> why -> bottom nav)
#      with EVERY id the generated Java looks up grafted back in, same names,
#      same widget types,
#    * rewrites item_message.xml to the reference message row (all MailAdapter
#      ids present),
#    * bumps 4.5 -> 4.6 (self-version + about strings).
#
#  NOTHING functional is touched: the same API endpoints/JSON fields, FCM push,
#  the support screen, the bundled notification sounds, the AdMob placements,
#  the notification-permission gate, multi-language support (all labels come
#  from @string/* so the 7 locales still switch), the install analytics, the OTP
#  precision fix, tappable verification links, the circular logo and the remote
#  appearance config (Ui.java still overrides accent/gradient/radius/titles).
#
#  The id reconciliation is explicit: the patch's own activity_main.xml drops a
#  large set of ids that MainActivity.java / Ui.java / Ads.java compile against
#  (R.id.heroBox, R.id.navBar, R.id.fi1..fi6, R.id.historyBox, ...). Writing the
#  patch verbatim would fail compilation. So this writer emits a merged layout
#  that keeps the patch's visual language AND re-attaches every required id.
# ============================================================================
import os, re

ROOT = "android"; APP = ROOT + "/app"
RES = APP + "/src/main/res"
J = APP + "/src/main/java/online/mytempmail/app"


def R(p):
    with open(p, encoding="utf-8") as f:
        return f.read()


def W(p, s):
    with open(p, "w", encoding="utf-8") as f:
        f.write(s)


def REP(path, old, new, tag, count=1):
    s = R(path)
    if s.count(old) != count:
        raise SystemExit("gn_ac: anchor %s not unique (%d, expected %d) in %s"
                         % (tag, s.count(old), count, path))
    W(path, s.replace(old, new))
    print("AC: patched %s (%s)" % (path, tag))


# ===========================================================================
# 1 : drawables  (verbatim from the patch)
# ===========================================================================
DRAWABLES = {
"screen_bg": """<?xml version="1.0" encoding="utf-8"?>
<layer-list xmlns:android="http://schemas.android.com/apk/res/android">
    <item>
        <shape>
            <gradient android:angle="90" android:startColor="#050A22"
                android:centerColor="#081544" android:endColor="#061E3D"/>
        </shape>
    </item>
</layer-list>
""",
"inner": """<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android">
    <solid android:color="#0A1538"/>
    <corners android:radius="15dp"/>
    <stroke android:width="1dp" android:color="#385C99"/>
</shape>
""",
"bottom_nav": """<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android">
    <solid android:color="#101A43"/>
    <corners android:radius="28dp"/>
    <stroke android:width="1dp" android:color="#345A9D"/>
</shape>
""",
"gradient_cta": """<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android">
    <gradient android:angle="0" android:startColor="#09D5FF"
        android:centerColor="#5862FF" android:endColor="#A53CFF"/>
    <corners android:radius="17dp"/>
</shape>
""",
"card": """<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android">
    <gradient android:angle="0" android:startColor="#152552"
        android:centerColor="#102047" android:endColor="#122A58"/>
    <corners android:radius="20dp"/>
    <stroke android:width="1dp" android:color="#267BC8"/>
</shape>
""",
"pill_live": """<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android">
    <solid android:color="#173C3B"/>
    <corners android:radius="50dp"/>
    <stroke android:width="1dp" android:color="#36DFA0"/>
</shape>
""",
"active_nav": """<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android">
    <gradient android:angle="0" android:startColor="#164DA0" android:endColor="#44269B"/>
    <corners android:radius="24dp"/>
</shape>
""",
"delete": """<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android">
    <solid android:color="#451A3D"/>
    <corners android:radius="16dp"/>
    <stroke android:width="1dp" android:color="#D84A77"/>
</shape>
""",
}
for name, body in DRAWABLES.items():
    W(RES + "/drawable/" + name + ".xml", body)
    print("AC: wrote drawable/%s.xml" % name)


# ===========================================================================
# 2 : colours  -  keep every existing name (other screens + Java reference
#     them) and append the reference palette additions.
# ===========================================================================
COLORS_ADD = """
    <!-- ===== reference (futuristic dark) palette additions ===== -->
    <color name="offex_surface">#101A42</color>
    <color name="offex_surface2">#162653</color>
    <color name="offex_dim">#AAB7DD</color>
    <color name="offex_muted">#6F7DAA</color>
    <color name="offex_blue">#247CFF</color>
    <color name="offex_pink">#B33DFF</color>
</resources>
"""
cp = RES + "/values/colors.xml"
s = R(cp)
if "offex_surface" not in s:
    s = s.replace("</resources>", COLORS_ADD.strip() + "\n", 1)
    # the replace above already re-added </resources>; normalise
    W(cp, s)
    print("AC: appended reference colours to colors.xml")
else:
    print("AC: (skip) colors.xml already has reference colours")


# ===========================================================================
# 3 : theme  -  nudge the default dark theme to the reference navy + cyan
#     secondary. All ox* attributes and styles are left untouched.
# ===========================================================================
tp = RES + "/values/themes.xml"
s = R(tp)
s = s.replace("#0A0B2E", "#050A22")
s = s.replace("<item name=\"colorSecondary\">@color/offex_purple2</item>",
              "<item name=\"colorSecondary\">@color/offex_cyan</item>")
W(tp, s)
print("AC: retuned themes.xml to the reference navy/cyan")


# ===========================================================================
# 4 : activity_main.xml  -  reference structure + full id reconciliation.
# ===========================================================================
FEATURE_ROWS = ""
FEAT_GLYPHS = ["&#9889;", "&#128273;", "&#128279;", "&#128276;", "&#127760;", "&#9203;"]
for n in range(1, 7):
    mt = 10 if n == 1 else 4
    FEATURE_ROWS += """
                    <LinearLayout android:layout_width="match_parent" android:layout_height="wrap_content"
                        android:layout_marginTop="%ddp" android:background="@drawable/inner"
                        android:orientation="horizontal" android:gravity="center_vertical" android:padding="12dp">
                        <TextView android:id="@+id/fi%d" android:layout_width="42dp" android:layout_height="42dp"
                            android:gravity="center" android:text="%s" android:textColor="@color/offex_white"
                            android:textSize="19sp" android:background="@drawable/bg_logo"/>
                        <LinearLayout android:layout_width="0dp" android:layout_height="wrap_content"
                            android:layout_weight="1" android:orientation="vertical" android:layout_marginStart="12dp">
                            <TextView android:layout_width="match_parent" android:layout_height="wrap_content"
                                android:text="@string/feat%d_t" android:textColor="@color/offex_white"
                                android:textSize="14sp" android:textStyle="bold"/>
                            <TextView android:layout_width="match_parent" android:layout_height="wrap_content"
                                android:layout_marginTop="2dp" android:text="@string/feat%d_d"
                                android:textColor="@color/offex_dim" android:textSize="11sp"
                                android:lineSpacingExtra="2dp"/>
                        </LinearLayout>
                        <TextView android:layout_width="wrap_content" android:layout_height="wrap_content"
                            android:layout_marginStart="6dp" android:text="@string/glyph_chevron"
                            android:textColor="@color/offex_muted" android:textSize="20sp"/>
                    </LinearLayout>""" % (mt, n, FEAT_GLYPHS[n - 1], n, n)


def nav_item(nid, iid, glyph, label):
    return """
        <FrameLayout android:id="@+id/%(nid)s" android:layout_width="0dp" android:layout_height="56dp"
            android:layout_weight="1" android:clickable="true" android:focusable="true">
            <View android:id="@+id/%(iid)s" android:layout_width="match_parent" android:layout_height="match_parent"
                android:background="@drawable/active_nav" android:visibility="invisible"/>
            <LinearLayout android:layout_width="match_parent" android:layout_height="match_parent"
                android:gravity="center" android:orientation="vertical">
                <TextView android:id="@+id/navIcon%(sfx)s" android:layout_width="wrap_content"
                    android:layout_height="wrap_content" android:text="@string/%(glyph)s"
                    android:textSize="17sp" android:textColor="@color/offex_dim"/>
                <TextView android:layout_width="wrap_content" android:layout_height="wrap_content"
                    android:layout_marginTop="3dp" android:text="@string/%(label)s"
                    android:textSize="9sp" android:textColor="@color/offex_dim"/>
            </LinearLayout>
        </FrameLayout>""" % {"nid": nid, "iid": iid, "sfx": nid[3:], "glyph": glyph, "label": label}


NAV = ""
NAV += nav_item("navEmail", "navIndEmail", "glyph_mail", "nav_email")
NAV += nav_item("navInbox", "navIndInbox", "glyph_inbox", "nav_inbox")
NAV += nav_item("navSwitch", "navIndSwitch", "glyph_switch", "nav_switch")
NAV += nav_item("navMore", "navIndMore", "glyph_more", "nav_more")

ACTIVITY_MAIN = """<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent" android:layout_height="match_parent"
    android:orientation="vertical" android:background="@drawable/screen_bg">

    <!-- ===== HEADER (hero) ===== -->
    <LinearLayout android:id="@+id/heroBox" android:layout_width="match_parent"
        android:layout_height="72dp" android:orientation="horizontal"
        android:gravity="center_vertical" android:paddingStart="22dp" android:paddingEnd="14dp">
        <TextView android:id="@+id/heroLogo" android:layout_width="52dp" android:layout_height="52dp"
            android:gravity="center" android:text="@string/glyph_mail" android:textSize="27sp"
            android:textColor="@color/offex_white" android:background="@drawable/gradient_cta"/>
        <LinearLayout android:layout_width="0dp" android:layout_height="wrap_content"
            android:layout_weight="1" android:orientation="vertical" android:paddingStart="13dp">
            <TextView android:id="@+id/heroTitle" android:layout_width="wrap_content"
                android:layout_height="wrap_content" android:text="@string/app_name"
                android:textSize="25sp" android:textStyle="bold" android:textColor="@color/offex_white"/>
            <TextView android:id="@+id/heroTagline" android:layout_width="wrap_content"
                android:layout_height="wrap_content" android:text="@string/tagline"
                android:textSize="12sp" android:textColor="@color/offex_dim"/>
        </LinearLayout>
        <TextView android:id="@+id/settingsBtn" android:layout_width="52dp" android:layout_height="52dp"
            android:gravity="center" android:text="@string/glyph_gear" android:textSize="23sp"
            android:textColor="@color/offex_white" android:background="@drawable/inner"/>
    </LinearLayout>

    <!-- ===== remote banner (appearance-driven) ===== -->
    <TextView android:id="@+id/bannerText" android:layout_width="match_parent"
        android:layout_height="wrap_content" android:layout_marginStart="18dp" android:layout_marginEnd="18dp"
        android:layout_marginTop="2dp" android:background="@drawable/inner" android:gravity="center_vertical"
        android:padding="13dp" android:textColor="@color/offex_white" android:textSize="13sp"
        android:textStyle="bold" android:visibility="gone"/>

    <ScrollView android:id="@+id/rootScroll" android:layout_width="match_parent"
        android:layout_height="0dp" android:layout_weight="1" android:clipToPadding="false"
        android:scrollbars="none" android:paddingStart="18dp" android:paddingEnd="18dp"
        android:paddingBottom="14dp">
        <LinearLayout android:layout_width="match_parent" android:layout_height="wrap_content"
            android:orientation="vertical">

            <!-- ===== CARD 1 : your temporary address ===== -->
            <LinearLayout android:id="@+id/activeCard" android:layout_width="match_parent"
                android:layout_height="wrap_content" android:orientation="vertical" android:padding="15dp"
                android:layout_marginTop="5dp" android:background="@drawable/card" android:visibility="gone">
                <LinearLayout android:layout_width="match_parent" android:layout_height="32dp"
                    android:orientation="horizontal" android:gravity="center_vertical">
                    <TextView android:id="@+id/c1icon" android:layout_width="30dp" android:layout_height="30dp"
                        android:gravity="center" android:text="@string/glyph_check" android:textSize="14sp"
                        android:textColor="@color/offex_white" android:background="@drawable/gradient_cta"/>
                    <TextView android:id="@+id/heroLabel" android:layout_width="0dp"
                        android:layout_height="wrap_content" android:layout_weight="1" android:layout_marginStart="10dp"
                        android:text="@string/your_address" android:textSize="15sp" android:textStyle="bold"
                        android:textColor="@color/offex_white"/>
                    <LinearLayout android:layout_width="wrap_content" android:layout_height="wrap_content"
                        android:orientation="horizontal" android:gravity="center_vertical"
                        android:paddingStart="10dp" android:paddingEnd="10dp" android:paddingTop="6dp"
                        android:paddingBottom="6dp" android:background="@drawable/pill_live">
                        <View android:id="@+id/liveDot" android:layout_width="8dp" android:layout_height="8dp"
                            android:background="@drawable/bg_dot_green"/>
                        <TextView android:id="@+id/liveText" android:layout_width="wrap_content"
                            android:layout_height="wrap_content" android:layout_marginStart="6dp"
                            android:text="@string/live" android:textSize="11sp" android:textStyle="bold"
                            android:textColor="@color/offex_green"/>
                    </LinearLayout>
                </LinearLayout>

                <LinearLayout android:id="@+id/addrPill" android:layout_width="match_parent"
                    android:layout_height="56dp" android:layout_marginTop="8dp" android:orientation="horizontal"
                    android:gravity="center_vertical" android:paddingStart="15dp" android:paddingEnd="7dp"
                    android:background="@drawable/inner">
                    <TextView android:id="@+id/addrText" android:layout_width="0dp" android:layout_height="wrap_content"
                        android:layout_weight="1" android:textSize="15sp" android:textStyle="bold"
                        android:textColor="@color/offex_white" android:maxLines="1" android:ellipsize="end"/>
                    <TextView android:id="@+id/copyIconBtn" android:layout_width="43dp" android:layout_height="43dp"
                        android:gravity="center" android:text="@string/glyph_copy" android:textSize="22sp"
                        android:textColor="@color/offex_white" android:background="@drawable/gradient_cta"/>
                </LinearLayout>
                <TextView android:id="@+id/countdownText" android:layout_width="wrap_content"
                    android:layout_height="wrap_content" android:textSize="10sp" android:paddingTop="6dp"
                    android:textColor="@color/offex_muted"/>

                <LinearLayout android:layout_width="match_parent" android:layout_height="46dp"
                    android:layout_marginTop="6dp" android:orientation="horizontal">
                    <androidx.appcompat.widget.AppCompatButton android:id="@+id/copyBtn"
                        android:layout_width="0dp" android:layout_height="match_parent" android:layout_weight="1"
                        android:insetTop="0dp" android:insetBottom="0dp" android:text="@string/copy"
                        android:textAllCaps="false" android:textSize="12sp" android:textColor="@color/offex_white"
                        android:background="@drawable/gradient_cta"/>
                    <androidx.appcompat.widget.AppCompatButton android:id="@+id/refreshBtn"
                        android:layout_width="0dp" android:layout_height="match_parent" android:layout_weight="1"
                        android:layout_marginStart="7dp" android:insetTop="0dp" android:insetBottom="0dp"
                        android:text="@string/refresh" android:textAllCaps="false" android:textSize="12sp"
                        android:textColor="@color/offex_white" android:background="@drawable/inner"/>
                    <androidx.appcompat.widget.AppCompatButton android:id="@+id/deleteBtn"
                        android:layout_width="0dp" android:layout_height="match_parent" android:layout_weight="1"
                        android:layout_marginStart="7dp" android:insetTop="0dp" android:insetBottom="0dp"
                        android:text="@string/delete" android:textAllCaps="false" android:textSize="12sp"
                        android:textColor="#FF9BB4" android:background="@drawable/delete"/>
                </LinearLayout>
            </LinearLayout>

            <!-- ===== CARD 2 : create new email ===== -->
            <LinearLayout android:id="@+id/createCard" android:layout_width="match_parent"
                android:layout_height="wrap_content" android:orientation="vertical" android:padding="15dp"
                android:layout_marginTop="13dp" android:background="@drawable/card">
                <LinearLayout android:layout_width="match_parent" android:layout_height="36dp"
                    android:orientation="horizontal" android:gravity="center_vertical">
                    <TextView android:id="@+id/c2icon" android:layout_width="34dp" android:layout_height="34dp"
                        android:gravity="center" android:text="@string/glyph_plus" android:textSize="25sp"
                        android:textColor="@color/offex_white" android:background="@drawable/gradient_cta"/>
                    <LinearLayout android:layout_width="0dp" android:layout_height="wrap_content"
                        android:layout_weight="1" android:orientation="vertical" android:paddingStart="11dp">
                        <TextView android:id="@+id/createLabel" android:layout_width="wrap_content"
                            android:layout_height="wrap_content" android:text="@string/create_new_email"
                            android:textSize="15sp" android:textStyle="bold" android:textColor="@color/offex_white"/>
                        <TextView android:id="@+id/secCreateSub" android:layout_width="wrap_content"
                            android:layout_height="wrap_content" android:text="@string/create_sub"
                            android:textSize="10sp" android:textColor="@color/offex_dim"/>
                    </LinearLayout>
                </LinearLayout>
                <EditText android:id="@+id/nameBox" android:layout_width="match_parent"
                    android:layout_height="49dp" android:layout_marginTop="11dp" android:hint="@string/hint_name"
                    android:textColorHint="@color/offex_dim" android:textColor="@color/offex_white"
                    android:textSize="13sp" android:paddingStart="15dp" android:paddingEnd="15dp"
                    android:inputType="text" android:maxLines="1" android:background="@drawable/inner"/>
                <Spinner android:id="@+id/domainBox" android:layout_width="match_parent"
                    android:layout_height="49dp" android:layout_marginTop="8dp" android:background="@drawable/inner"/>
                <androidx.appcompat.widget.AppCompatButton android:id="@+id/createBtn"
                    android:layout_width="match_parent" android:layout_height="52dp" android:layout_marginTop="9dp"
                    android:insetTop="0dp" android:insetBottom="0dp" android:text="@string/create_inbox"
                    android:textAllCaps="false" android:textStyle="bold" android:textSize="14sp"
                    android:textColor="@color/offex_white" android:background="@drawable/gradient_cta"/>
            </LinearLayout>

            <!-- ===== CARD 3 : inbox ===== -->
            <LinearLayout android:id="@+id/inboxCard" android:layout_width="match_parent"
                android:layout_height="wrap_content" android:orientation="vertical" android:padding="15dp"
                android:layout_marginTop="13dp" android:background="@drawable/card">
                <LinearLayout android:layout_width="match_parent" android:layout_height="35dp"
                    android:orientation="horizontal" android:gravity="center_vertical">
                    <TextView android:id="@+id/c3icon" android:layout_width="35dp" android:layout_height="35dp"
                        android:gravity="center" android:text="@string/glyph_mail" android:textSize="19sp"
                        android:textColor="@color/offex_white" android:background="@drawable/inner"/>
                    <LinearLayout android:layout_width="0dp" android:layout_height="wrap_content"
                        android:layout_weight="1" android:orientation="vertical" android:paddingStart="10dp">
                        <TextView android:id="@+id/secInbox" android:layout_width="wrap_content"
                            android:layout_height="wrap_content" android:text="@string/inbox_title"
                            android:textSize="15sp" android:textStyle="bold" android:textColor="@color/offex_white"/>
                        <TextView android:id="@+id/inboxAddr" android:layout_width="wrap_content"
                            android:layout_height="wrap_content" android:textSize="9sp"
                            android:textColor="@color/offex_dim" android:maxLines="1" android:ellipsize="end"/>
                    </LinearLayout>
                    <TextView android:id="@+id/newPill" android:layout_width="wrap_content"
                        android:layout_height="wrap_content" android:textSize="10sp"
                        android:textColor="@color/offex_green" android:visibility="gone"/>
                </LinearLayout>
                <TextView android:id="@+id/emptyText" android:layout_width="match_parent"
                    android:layout_height="wrap_content" android:layout_marginTop="8dp"
                    android:text="@string/no_messages" android:textColor="@color/offex_dim"
                    android:textSize="11sp" android:background="@drawable/bg_nested" android:padding="14dp"
                    android:lineSpacingExtra="3dp"/>
                <androidx.recyclerview.widget.RecyclerView android:id="@+id/msgList"
                    android:layout_width="match_parent" android:layout_height="wrap_content"
                    android:layout_marginTop="4dp" android:nestedScrollingEnabled="false"/>
            </LinearLayout>

            <!-- ===== NATIVE AD ===== -->
            <LinearLayout android:id="@+id/nativeAdBox" android:layout_width="match_parent"
                android:layout_height="wrap_content" android:layout_marginTop="13dp"
                android:orientation="vertical" android:visibility="gone"/>

            <!-- ===== CARD 4 : switch email ===== -->
            <LinearLayout android:id="@+id/switchCard" android:layout_width="match_parent"
                android:layout_height="wrap_content" android:orientation="vertical" android:padding="15dp"
                android:layout_marginTop="13dp" android:background="@drawable/card">
                <LinearLayout android:layout_width="match_parent" android:layout_height="34dp"
                    android:orientation="horizontal" android:gravity="center_vertical">
                    <TextView android:id="@+id/c4icon" android:layout_width="35dp" android:layout_height="35dp"
                        android:gravity="center" android:text="@string/glyph_switch" android:textSize="20sp"
                        android:textColor="@color/offex_white" android:background="@drawable/inner"/>
                    <LinearLayout android:layout_width="0dp" android:layout_height="wrap_content"
                        android:layout_weight="1" android:orientation="vertical" android:paddingStart="10dp">
                        <TextView android:id="@+id/secSwitch" android:layout_width="wrap_content"
                            android:layout_height="wrap_content" android:text="@string/switch_title"
                            android:textSize="15sp" android:textStyle="bold" android:textColor="@color/offex_white"/>
                        <TextView android:id="@+id/secChoose" android:layout_width="wrap_content"
                            android:layout_height="wrap_content" android:text="@string/choose_email"
                            android:textSize="9sp" android:textColor="@color/offex_dim"/>
                    </LinearLayout>
                    <TextView android:id="@+id/viewAllBtn" android:layout_width="wrap_content"
                        android:layout_height="wrap_content" android:text="@string/view_all" android:textSize="10sp"
                        android:textColor="@color/offex_dim" android:paddingStart="11dp" android:paddingEnd="11dp"
                        android:paddingTop="7dp" android:paddingBottom="7dp" android:background="@drawable/inner"/>
                </LinearLayout>
                <TextView android:id="@+id/historyEmpty" android:layout_width="match_parent"
                    android:layout_height="wrap_content" android:layout_marginTop="9dp"
                    android:text="@string/history_empty" android:textColor="@color/offex_dim" android:textSize="11sp"
                    android:background="@drawable/bg_nested" android:padding="14dp" android:lineSpacingExtra="3dp"/>
                <LinearLayout android:id="@+id/historyBox" android:layout_width="match_parent"
                    android:layout_height="wrap_content" android:orientation="vertical"/>
            </LinearLayout>

            <!-- ===== CARD 5 : why offex mail ===== -->
            <LinearLayout android:id="@+id/featuresCard" android:layout_width="match_parent"
                android:layout_height="wrap_content" android:orientation="vertical" android:padding="15dp"
                android:layout_marginTop="13dp" android:background="@drawable/card">
                <TextView android:id="@+id/secFeatures" android:layout_width="wrap_content"
                    android:layout_height="wrap_content" android:text="@string/features_title"
                    android:textSize="16sp" android:textStyle="bold" android:textColor="@color/offex_white"/>
                <TextView android:id="@+id/secFeaturesSub" android:layout_width="match_parent"
                    android:layout_height="wrap_content" android:text="@string/features_sub"
                    android:textSize="10sp" android:textColor="@color/offex_dim"/>
                <LinearLayout android:id="@+id/featuresBox" android:layout_width="match_parent"
                    android:layout_height="wrap_content" android:orientation="vertical" android:layout_marginTop="6dp">%s
                </LinearLayout>
            </LinearLayout>
        </LinearLayout>
    </ScrollView>

    <!-- ===== BOTTOM NAV ===== -->
    <LinearLayout android:id="@+id/navBar" android:layout_width="match_parent"
        android:layout_height="65dp" android:layout_marginStart="12dp" android:layout_marginEnd="12dp"
        android:layout_marginBottom="9dp" android:background="@drawable/bottom_nav" android:gravity="center"
        android:orientation="horizontal">%s
    </LinearLayout>
</LinearLayout>
""" % (FEATURE_ROWS, NAV)

W(RES + "/layout/activity_main.xml", ACTIVITY_MAIN)
print("AC: wrote activity_main.xml (%d bytes)" % len(ACTIVITY_MAIN))


# ===========================================================================
# 5 : item_message.xml  -  reference message row (all MailAdapter ids present).
# ===========================================================================
ITEM_MESSAGE = """<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent" android:layout_height="wrap_content" android:orientation="vertical"
    android:padding="12dp" android:layout_marginTop="7dp" android:background="@drawable/inner">
    <LinearLayout android:layout_width="match_parent" android:layout_height="wrap_content"
        android:orientation="horizontal" android:gravity="center_vertical">
        <TextView android:id="@+id/mAvatar" android:layout_width="42dp" android:layout_height="42dp"
            android:gravity="center" android:text="E" android:textSize="18sp" android:textStyle="bold"
            android:textColor="@color/offex_white" android:background="@drawable/gradient_cta"/>
        <LinearLayout android:layout_width="0dp" android:layout_height="wrap_content"
            android:layout_weight="1" android:orientation="vertical" android:paddingStart="11dp">
            <TextView android:id="@+id/mSender" android:layout_width="match_parent" android:layout_height="wrap_content"
                android:textColor="@color/offex_white" android:textSize="12sp" android:textStyle="bold"
                android:maxLines="1" android:ellipsize="end"/>
            <TextView android:id="@+id/mSubject" android:layout_width="match_parent" android:layout_height="wrap_content"
                android:textColor="@color/offex_white" android:textSize="10sp" android:layout_marginTop="3dp"
                android:maxLines="2" android:ellipsize="end"/>
        </LinearLayout>
        <TextView android:id="@+id/mTime" android:layout_width="wrap_content" android:layout_height="wrap_content"
            android:textColor="@color/offex_dim" android:textSize="9sp" android:layout_marginStart="8dp"/>
        <TextView android:layout_width="20dp" android:layout_height="30dp" android:gravity="center"
            android:text="@string/glyph_chevron" android:textColor="@color/offex_white" android:textSize="24sp"/>
    </LinearLayout>
    <LinearLayout android:layout_width="wrap_content" android:layout_height="wrap_content"
        android:layout_marginStart="53dp" android:layout_marginTop="3dp" android:orientation="horizontal">
        <TextView android:id="@+id/mService" android:layout_width="wrap_content" android:layout_height="22dp"
            android:gravity="center" android:paddingStart="9dp" android:paddingEnd="9dp" android:textSize="8sp"
            android:textColor="@color/offex_white" android:background="@drawable/pill_live"/>
        <TextView android:id="@+id/mOtp" android:layout_width="wrap_content" android:layout_height="22dp"
            android:layout_marginStart="5dp" android:gravity="center" android:paddingStart="9dp"
            android:paddingEnd="9dp" android:textSize="8sp" android:textColor="#050A22"
            android:background="@drawable/gradient_cta" android:visibility="gone"/>
    </LinearLayout>
</LinearLayout>
"""
W(RES + "/layout/item_message.xml", ITEM_MESSAGE)
print("AC: wrote item_message.xml (%d bytes)" % len(ITEM_MESSAGE))


# ===========================================================================
# 6 : version bump 4.5 -> 4.6 (self-version + about strings).
# ===========================================================================
REP(J + "/Config.java",
    '            if(latest.equals("4.5")) return;',
    '            if(latest.equals("4.6")) return;',
    "self-version 4.6")

REP(J + "/SupportActivity.java",
    '    public static final String VERSION = "4.5";',
    '    public static final String VERSION = "4.6";',
    "support self-version 4.6")

for loc in ["", "-hi", "-es", "-pt", "-ar", "-ru", "-in"]:
    p = RES + "/values" + loc + "/strings.xml"
    if not os.path.exists(p):
        continue
    s = R(p)
    s2 = re.sub(r'(name="about_version">[^<]*?)4\.5(<)', r"\g<1>4.6\g<2>", s)
    if s2 == s:
        print("AC: (skip) about_version 4.5 not present in %s" % p)
    else:
        W(p, s2)
        print("AC: patched %s (about_version 4.6)" % p)

print("AC: done")
