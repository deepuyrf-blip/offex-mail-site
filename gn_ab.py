# ============================================================================
#  gn_ab.py  -  v4.5  (NEW LAST WRITER, runs after gn_aa)
# ============================================================================
#  Premium dark navy/purple redesign of the Offex Mail home screen, matching
#  the approved reference: deep navy->dark purple vertical gradient with soft
#  blue/purple radial light flares, semi-transparent glass cards, a purple->blue
#  primary gradient, blue icons/secondary text, green Live/Active dots and a red
#  Delete.
#
#  This writer:
#    * rewrites the theme palette (dark = the new premium look, and the app now
#      defaults to dark so the reference is what a user sees on launch),
#    * rewrites activity_main.xml + item_message.xml to the reference layout,
#    * rewrites the glass/gradient drawables,
#    * rewrites Ui.java (remote-appearance driven, defaults now match the ref),
#    * rewrites MailAdapter.java (avatar initial + chevron),
#    * bumps 4.4 -> 4.5 (self-version + about strings).
#
#  Everything functional is preserved: every existing view id, the bottom nav
#  and its four tabs/behaviour, all API calls/endpoints/JSON fields, FCM push,
#  the support screen, the bundled notification sounds, the AdMob placements,
#  the notification-permission gate, multi-language support, the install
#  analytics, the OTP precision fix, tappable verification links, the circular
#  logo and the remote appearance config (accent/gradient/radius/titles/toggles
#  still override at runtime).
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
        raise SystemExit("gn_ab: anchor %s not unique (%d, expected %d) in %s"
                         % (tag, s.count(old), count, path))
    W(path, s.replace(old, new))
    print("AB: patched %s (%s)" % (path, tag))


# ===========================================================================
# 1 : colours.xml  -  brand -> purple/blue, keep semantic greens/reds.
# ===========================================================================
W(RES + "/values/colors.xml", """<?xml version="1.0" encoding="utf-8"?>
<resources>
    <!-- brand: purple -> blue primary gradient -->
    <color name="offex_purple">#6D4DFF</color>
    <color name="offex_purple2">#3B82F6</color>
    <color name="offex_purple_dark">#4C2FD6</color>
    <color name="offex_purple_soft">#EEF0FF</color>
    <color name="offex_cyan">#38BDF8</color>

    <!-- semantic accents -->
    <color name="offex_green">#22C55E</color>
    <color name="offex_green_soft">#E4F8EC</color>
    <color name="offex_red">#EF4444</color>
    <color name="offex_red_soft">#FDECEC</color>
    <color name="offex_red_soft_border">#F7C9C9</color>

    <!-- neutrals -->
    <color name="offex_white">#FFFFFF</color>
    <color name="offex_white_dim">#E7E3FF</color>
    <color name="offex_transparent">#00000000</color>

    <!-- concrete surface colours used by the two themes -->
    <color name="offex_bg_light">#F5F5FB</color>
    <color name="offex_bg_dark">#0A0B2E</color>

    <!-- light-theme fallbacks (kept so any stray reference still resolves) -->
    <color name="offex_bg">#F5F5FB</color>
    <color name="offex_bg2">#FFFFFF</color>
    <color name="offex_card">#FFFFFF</color>
    <color name="offex_line">#E7E4F2</color>
    <color name="offex_text">#171330</color>
    <color name="offex_text_dim">#5C5875</color>
    <color name="offex_text_mute">#9A96AD</color>
    <color name="offex_glass_border">#E7E3F7</color>
    <color name="offex_nav">#FFFFFF</color>
</resources>
""")
print("AB: wrote colors.xml")


# ===========================================================================
# 2 : themes.xml  -  dark = premium reference (default), light = purple variant.
# ===========================================================================
W(RES + "/values/themes.xml", """<?xml version="1.0" encoding="utf-8"?>
<resources xmlns:tools="http://schemas.android.com/tools">

    <!-- The premium dark navy/purple look is the DEFAULT (matches the reference). -->
    <style name="Theme.Offex" parent="Theme.MaterialComponents.NoActionBar">
        <item name="colorPrimary">@color/offex_purple</item>
        <item name="colorPrimaryVariant">@color/offex_purple_dark</item>
        <item name="colorOnPrimary">@color/offex_white</item>
        <item name="colorSecondary">@color/offex_purple2</item>
        <item name="colorOnSecondary">@color/offex_white</item>
        <item name="android:colorBackground">@color/offex_bg_dark</item>
        <item name="android:windowBackground">@color/offex_bg_dark</item>
        <item name="android:textColorPrimary">#F2F3F8</item>
        <item name="android:textColorSecondary">#AAB4DE</item>
        <item name="android:statusBarColor" tools:targetApi="l">#0A0B2E</item>
        <item name="android:navigationBarColor">#0A0B2E</item>
        <item name="android:windowLightStatusBar" tools:targetApi="m">false</item>
        <item name="android:windowLightNavigationBar" tools:targetApi="o">false</item>
        <item name="android:windowAnimationStyle">@style/Anim.Offex</item>

        <item name="oxBg">#0A0B2E</item>
        <item name="oxCard">#CC151A45</item>
        <item name="oxCardBorder">#33FFFFFF</item>
        <item name="oxText">#FFFFFF</item>
        <item name="oxTextDim">#AAB4DE</item>
        <item name="oxTextMute">#7B87B5</item>
        <item name="oxLine">#263061</item>
        <item name="oxNavBg">#0E1030</item>
        <item name="oxInputBg">#141A44</item>
        <item name="oxInputBorder">#2A3566</item>
        <item name="oxHeaderStart">#0A0B2E</item>
        <item name="oxHeaderCenter">#171236</item>
        <item name="oxHeaderEnd">#2D1B6B</item>
        <item name="oxChipBg">#3A2A7A</item>
        <item name="oxChipBorder">#6D4DFF</item>
        <item name="oxChipText">#C9B8FF</item>
        <item name="oxOnHeader">#FFFFFF</item>
        <item name="oxOnHeaderDim">#AAB4DE</item>
    </style>

    <!-- Light stays available; selected from More > Theme. -->
    <style name="Theme.Offex.Dark" parent="Theme.MaterialComponents.NoActionBar">
        <item name="colorPrimary">@color/offex_purple</item>
        <item name="colorPrimaryVariant">@color/offex_purple_dark</item>
        <item name="colorOnPrimary">@color/offex_white</item>
        <item name="colorSecondary">@color/offex_purple2</item>
        <item name="colorOnSecondary">@color/offex_white</item>
        <item name="android:colorBackground">@color/offex_bg_dark</item>
        <item name="android:windowBackground">@color/offex_bg_dark</item>
        <item name="android:textColorPrimary">#F2F3F8</item>
        <item name="android:textColorSecondary">#AAB4DE</item>
        <item name="android:statusBarColor" tools:targetApi="l">#0A0B2E</item>
        <item name="android:navigationBarColor">#0A0B2E</item>
        <item name="android:windowLightStatusBar" tools:targetApi="m">false</item>
        <item name="android:windowLightNavigationBar" tools:targetApi="o">false</item>
        <item name="android:windowAnimationStyle">@style/Anim.Offex</item>

        <item name="oxBg">#0A0B2E</item>
        <item name="oxCard">#CC151A45</item>
        <item name="oxCardBorder">#33FFFFFF</item>
        <item name="oxText">#FFFFFF</item>
        <item name="oxTextDim">#AAB4DE</item>
        <item name="oxTextMute">#7B87B5</item>
        <item name="oxLine">#263061</item>
        <item name="oxNavBg">#0E1030</item>
        <item name="oxInputBg">#141A44</item>
        <item name="oxInputBorder">#2A3566</item>
        <item name="oxHeaderStart">#0A0B2E</item>
        <item name="oxHeaderCenter">#171236</item>
        <item name="oxHeaderEnd">#2D1B6B</item>
        <item name="oxChipBg">#3A2A7A</item>
        <item name="oxChipBorder">#6D4DFF</item>
        <item name="oxChipText">#C9B8FF</item>
        <item name="oxOnHeader">#FFFFFF</item>
        <item name="oxOnHeaderDim">#AAB4DE</item>
    </style>

    <style name="Theme.Offex.Light" parent="Theme.MaterialComponents.Light.NoActionBar">
        <item name="colorPrimary">@color/offex_purple</item>
        <item name="colorPrimaryVariant">@color/offex_purple_dark</item>
        <item name="colorOnPrimary">@color/offex_white</item>
        <item name="colorSecondary">@color/offex_purple2</item>
        <item name="colorOnSecondary">@color/offex_white</item>
        <item name="android:colorBackground">@color/offex_bg_light</item>
        <item name="android:windowBackground">@color/offex_bg_light</item>
        <item name="android:textColorPrimary">@color/offex_text</item>
        <item name="android:textColorSecondary">@color/offex_text_dim</item>
        <item name="android:statusBarColor" tools:targetApi="l">@color/offex_bg_light</item>
        <item name="android:navigationBarColor">@color/offex_bg_light</item>
        <item name="android:windowLightStatusBar" tools:targetApi="m">true</item>
        <item name="android:windowLightNavigationBar" tools:targetApi="o">true</item>
        <item name="android:windowAnimationStyle">@style/Anim.Offex</item>

        <item name="oxBg">#F5F5FB</item>
        <item name="oxCard">#FFFFFF</item>
        <item name="oxCardBorder">#E7E3F7</item>
        <item name="oxText">#171330</item>
        <item name="oxTextDim">#5C5875</item>
        <item name="oxTextMute">#9A96AD</item>
        <item name="oxLine">#E7E4F2</item>
        <item name="oxNavBg">#FFFFFF</item>
        <item name="oxInputBg">#F3F1FB</item>
        <item name="oxInputBorder">#E3DFF2</item>
        <item name="oxHeaderStart">#FFFFFF</item>
        <item name="oxHeaderCenter">#F3F0FF</item>
        <item name="oxHeaderEnd">#EDE9FF</item>
        <item name="oxChipBg">#EEF0FF</item>
        <item name="oxChipBorder">#D9D2FF</item>
        <item name="oxChipText">#4C2FD6</item>
        <item name="oxOnHeader">#171330</item>
        <item name="oxOnHeaderDim">#5C5875</item>
    </style>

    <style name="Anim.Offex" parent="@android:style/Animation.Activity">
        <item name="android:activityOpenEnterAnimation">@anim/slide_up_fade</item>
        <item name="android:activityOpenExitAnimation">@anim/fade_out</item>
        <item name="android:activityCloseEnterAnimation">@anim/fade_in</item>
        <item name="android:activityCloseExitAnimation">@anim/fade_out</item>
    </style>
</resources>
""")
print("AB: wrote themes.xml")


# ===========================================================================
# 3 : drawables - glass cards, gradient buttons, glows.
# ===========================================================================
D = RES + "/drawable"

DRAW = {}

DRAW["bg_app"] = """<?xml version="1.0" encoding="utf-8"?>
<layer-list xmlns:android="http://schemas.android.com/apk/res/android">
    <item>
        <shape android:shape="rectangle">
            <gradient android:type="linear" android:angle="270"
                android:startColor="?attr/oxHeaderStart"
                android:centerColor="?attr/oxHeaderCenter"
                android:endColor="?attr/oxHeaderEnd" />
        </shape>
    </item>
    <item>
        <shape android:shape="rectangle">
            <gradient android:type="radial" android:gradientRadius="640dp"
                android:centerX="0.86" android:centerY="0.02"
                android:startColor="#3D4B7BFF" android:endColor="#004B7BFF" />
        </shape>
    </item>
    <item>
        <shape android:shape="rectangle">
            <gradient android:type="radial" android:gradientRadius="720dp"
                android:centerX="0.08" android:centerY="0.30"
                android:startColor="#339A6BFF" android:endColor="#009A6BFF" />
        </shape>
    </item>
</layer-list>
"""

DRAW["bg_card"] = """<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="rectangle">
    <solid android:color="?attr/oxCard" />
    <corners android:radius="22dp" />
    <stroke android:width="1dp" android:color="?attr/oxCardBorder" />
</shape>
"""

DRAW["bg_card_hero"] = """<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="rectangle">
    <solid android:color="?attr/oxCard" />
    <corners android:radius="24dp" />
    <stroke android:width="1dp" android:color="?attr/oxCardBorder" />
</shape>
"""

DRAW["bg_nested"] = """<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="rectangle">
    <solid android:color="?attr/oxInputBg" />
    <corners android:radius="16dp" />
    <stroke android:width="1dp" android:color="?attr/oxInputBorder" />
</shape>
"""

DRAW["bg_pill_address"] = """<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="rectangle">
    <solid android:color="?attr/oxInputBg" />
    <corners android:radius="14dp" />
    <stroke android:width="1dp" android:color="?attr/oxInputBorder" />
</shape>
"""

DRAW["bg_pill_row"] = """<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="rectangle">
    <solid android:color="?attr/oxInputBg" />
    <corners android:radius="14dp" />
    <stroke android:width="1dp" android:color="?attr/oxInputBorder" />
</shape>
"""

DRAW["bg_gear_btn"] = """<?xml version="1.0" encoding="utf-8"?>
<ripple xmlns:android="http://schemas.android.com/apk/res/android" android:color="#33FFFFFF">
    <item>
        <shape android:shape="oval">
            <solid android:color="#1FFFFFFF" />
            <stroke android:width="1dp" android:color="#33FFFFFF" />
        </shape>
    </item>
</ripple>
"""

DRAW["bg_sec_icon"] = """<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="oval">
    <gradient android:startColor="#6D4DFF" android:centerColor="#4F6BFF"
        android:endColor="#3B82F6" android:angle="315" />
</shape>
"""

DRAW["bg_logo_sq"] = """<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="rectangle">
    <gradient android:startColor="#6D4DFF" android:centerColor="#4F6BFF"
        android:endColor="#3B82F6" android:angle="315" />
    <corners android:radius="16dp" />
</shape>
"""

DRAW["bg_copy_btn"] = """<?xml version="1.0" encoding="utf-8"?>
<ripple xmlns:android="http://schemas.android.com/apk/res/android" android:color="#40FFFFFF">
    <item>
        <shape android:shape="rectangle">
            <solid android:color="#3B82F6" />
            <corners android:radius="12dp" />
        </shape>
    </item>
</ripple>
"""

DRAW["bg_btn_blue"] = """<?xml version="1.0" encoding="utf-8"?>
<ripple xmlns:android="http://schemas.android.com/apk/res/android" android:color="#40FFFFFF">
    <item>
        <shape android:shape="rectangle">
            <solid android:color="#3B82F6" />
            <corners android:radius="999dp" />
        </shape>
    </item>
</ripple>
"""

DRAW["bg_btn_darkblue"] = """<?xml version="1.0" encoding="utf-8"?>
<ripple xmlns:android="http://schemas.android.com/apk/res/android" android:color="#33FFFFFF">
    <item>
        <shape android:shape="rectangle">
            <solid android:color="#1E2A5E" />
            <corners android:radius="999dp" />
            <stroke android:width="1dp" android:color="#33FFFFFF" />
        </shape>
    </item>
</ripple>
"""

DRAW["bg_btn_red"] = """<?xml version="1.0" encoding="utf-8"?>
<ripple xmlns:android="http://schemas.android.com/apk/res/android" android:color="#40FFFFFF">
    <item>
        <shape android:shape="rectangle">
            <solid android:color="#EF4444" />
            <corners android:radius="999dp" />
        </shape>
    </item>
</ripple>
"""

DRAW["bg_btn_primary"] = """<?xml version="1.0" encoding="utf-8"?>
<ripple xmlns:android="http://schemas.android.com/apk/res/android" android:color="#40FFFFFF">
    <item>
        <shape android:shape="rectangle">
            <gradient android:startColor="#6D4DFF" android:centerColor="#4F6BFF"
                android:endColor="#3B82F6" android:angle="0" />
            <corners android:radius="999dp" />
        </shape>
    </item>
</ripple>
"""

DRAW["bg_btn_ghost"] = """<?xml version="1.0" encoding="utf-8"?>
<ripple xmlns:android="http://schemas.android.com/apk/res/android" android:color="#33FFFFFF">
    <item>
        <shape android:shape="rectangle">
            <solid android:color="?attr/oxInputBg" />
            <corners android:radius="999dp" />
            <stroke android:width="1dp" android:color="?attr/oxInputBorder" />
        </shape>
    </item>
</ripple>
"""

DRAW["bg_btn_danger"] = """<?xml version="1.0" encoding="utf-8"?>
<ripple xmlns:android="http://schemas.android.com/apk/res/android" android:color="#40FFFFFF">
    <item>
        <shape android:shape="rectangle">
            <solid android:color="#EF4444" />
            <corners android:radius="999dp" />
        </shape>
    </item>
</ripple>
"""

DRAW["bg_dot_green"] = """<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="oval">
    <solid android:color="#22C55E" />
</shape>
"""

DRAW["bg_pill_purple"] = """<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="rectangle">
    <solid android:color="#3A2A7A" />
    <corners android:radius="999dp" />
    <stroke android:width="1dp" android:color="#6D4DFF" />
</shape>
"""

DRAW["bg_tag_grey"] = """<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="rectangle">
    <solid android:color="#2A2F55" />
    <corners android:radius="999dp" />
</shape>
"""

DRAW["bg_nav"] = """<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="rectangle">
    <solid android:color="?attr/oxNavBg" />
    <corners android:topLeftRadius="26dp" android:topRightRadius="26dp" />
    <stroke android:width="1dp" android:color="?attr/oxCardBorder" />
</shape>
"""

DRAW["bg_indicator"] = """<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="rectangle">
    <gradient android:startColor="#6D4DFF" android:endColor="#3B82F6" android:angle="0" />
    <corners android:radius="999dp" />
</shape>
"""

DRAW["bg_chip"] = """<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="rectangle">
    <solid android:color="?attr/oxChipBg" />
    <corners android:radius="999dp" />
    <stroke android:width="1dp" android:color="?attr/oxChipBorder" />
</shape>
"""

DRAW["bg_chip_green"] = """<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="rectangle">
    <solid android:color="#3322C55E" />
    <corners android:radius="999dp" />
    <stroke android:width="1dp" android:color="#5522C55E" />
</shape>
"""

DRAW["bg_chip_red"] = """<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="rectangle">
    <solid android:color="#33EF4444" />
    <corners android:radius="999dp" />
</shape>
"""

DRAW["bg_input"] = """<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="rectangle">
    <solid android:color="?attr/oxInputBg" />
    <corners android:radius="16dp" />
    <stroke android:width="1dp" android:color="?attr/oxInputBorder" />
</shape>
"""

DRAW["bg_logo"] = """<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="oval">
    <gradient android:startColor="#6D4DFF" android:centerColor="#4F6BFF"
        android:endColor="#3B82F6" android:angle="315" />
</shape>
"""

DRAW["bg_icon"] = """<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="oval">
    <gradient android:startColor="#6D4DFF" android:centerColor="#4F6BFF"
        android:endColor="#3B82F6" android:angle="315" />
</shape>
"""

DRAW["bg_avatar"] = """<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="oval">
    <gradient android:startColor="#EF4444" android:centerColor="#F97316"
        android:endColor="#FB923C" android:angle="315" />
</shape>
"""

DRAW["bg_hero"] = """<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="rectangle">
    <gradient android:type="linear" android:angle="270"
        android:startColor="?attr/oxHeaderStart"
        android:centerColor="?attr/oxHeaderCenter"
        android:endColor="?attr/oxHeaderEnd" />
</shape>
"""

DRAW["bg_header"] = """<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="rectangle">
    <gradient android:type="linear" android:angle="270"
        android:startColor="?attr/oxHeaderStart"
        android:centerColor="?attr/oxHeaderCenter"
        android:endColor="?attr/oxHeaderEnd" />
    <corners android:bottomLeftRadius="30dp" android:bottomRightRadius="30dp" />
</shape>
"""

for name, xml in DRAW.items():
    W(D + "/" + name + ".xml", xml)
print("AB: wrote %d drawables" % len(DRAW))


# ===========================================================================
# 4 : glyphs + strings (default locale only; other locales fall back).
# ===========================================================================
W(RES + "/values/glyphs.xml", """<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="glyph_mail">\\u2709</string>
    <string name="glyph_gear">\\u2699</string>
    <string name="glyph_inbox">\\u2261</string>
    <string name="glyph_switch">\\u21C4</string>
    <string name="glyph_more">\\u22EF</string>
    <string name="glyph_close">\\u2715</string>
    <string name="glyph_copy">\\u29C9</string>
    <string name="glyph_plus">\\uFF0B</string>
    <string name="glyph_back">\\u2190</string>
    <string name="glyph_crown">\\u265B</string>
    <string name="glyph_check">\\u2713</string>
    <string name="glyph_arrow">\\u2192</string>
    <string name="glyph_chevron">\\u203A</string>
</resources>
""")

sp = RES + "/values/strings.xml"
s = R(sp)
if '<string name="live">' not in s:
    extra = """
    <string name="live">Live</string>
    <string name="active_label">Active</string>
    <string name="create_sub">Custom name or random</string>
    <string name="new_suffix">new</string>
    <string name="view_all">View all</string>
"""
    s = s.replace("</resources>", extra + "</resources>")
# tagline -> the reference wording (bullet separator)
s = s.replace('<string name="tagline">Temp Mail - Instant Inbox</string>',
              '<string name="tagline">Temp Mail \u2022 Instant Inbox</string>')
W(sp, s)
print("AB: wrote strings.xml (added live/create_sub/new_suffix/view_all)")


# ===========================================================================
# 5 : activity_main.xml  -  the reference layout (every old id preserved).
# ===========================================================================
MAIN_XML = """<?xml version="1.0" encoding="utf-8"?>
<FrameLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent" android:layout_height="match_parent"
    android:background="@drawable/bg_app">

    <ScrollView android:id="@+id/rootScroll"
        android:layout_width="match_parent" android:layout_height="match_parent"
        android:fillViewport="true" android:clipToPadding="false"
        android:scrollbars="none">

        <LinearLayout android:layout_width="match_parent" android:layout_height="wrap_content"
            android:orientation="vertical" android:paddingBottom="132dp">

            <!-- ===== remote banner (appearance-driven) ===== -->
            <TextView android:id="@+id/bannerText"
                android:layout_width="match_parent" android:layout_height="wrap_content"
                android:layout_marginStart="16dp" android:layout_marginEnd="16dp"
                android:layout_marginTop="14dp" android:background="@drawable/bg_banner"
                android:drawablePadding="8dp" android:elevation="4dp" android:gravity="center_vertical"
                android:padding="14dp" android:textColor="?attr/oxChipText"
                android:textSize="13sp" android:textStyle="bold" android:visibility="gone" />

            <!-- ===== HEADER ===== -->
            <LinearLayout android:id="@+id/heroBox" android:layout_width="match_parent"
                android:layout_height="wrap_content" android:orientation="horizontal"
                android:gravity="center_vertical" android:paddingStart="20dp"
                android:paddingEnd="20dp" android:paddingTop="18dp" android:paddingBottom="10dp">

                <TextView android:id="@+id/heroLogo" android:layout_width="52dp" android:layout_height="52dp"
                    android:background="@drawable/bg_logo_sq" android:elevation="8dp" android:gravity="center"
                    android:text="@string/glyph_mail" android:textColor="@color/offex_white"
                    android:textSize="24sp" />

                <LinearLayout android:layout_width="0dp" android:layout_height="wrap_content"
                    android:layout_weight="1" android:layout_marginStart="14dp" android:orientation="vertical">
                    <TextView android:id="@+id/heroTitle" android:layout_width="wrap_content"
                        android:layout_height="wrap_content" android:text="@string/app_name"
                        android:textColor="@color/offex_white" android:textSize="20sp"
                        android:textStyle="bold" android:fontFamily="sans-serif-black"
                        android:letterSpacing="0.01" />
                    <TextView android:id="@+id/heroTagline" android:layout_width="wrap_content"
                        android:layout_height="wrap_content" android:layout_marginTop="2dp"
                        android:text="@string/tagline" android:textColor="#AAB4DE" android:textSize="12sp" />
                </LinearLayout>

                <TextView android:id="@+id/settingsBtn" android:layout_width="44dp" android:layout_height="44dp"
                    android:background="@drawable/bg_gear_btn" android:gravity="center"
                    android:text="@string/glyph_gear" android:textColor="@color/offex_white"
                    android:textSize="20sp" />
            </LinearLayout>

            <!-- ===== CARD 1 : your temporary address ===== -->
            <LinearLayout android:id="@+id/activeCard" android:layout_width="match_parent"
                android:layout_height="wrap_content" android:layout_marginStart="16dp"
                android:layout_marginEnd="16dp" android:layout_marginTop="10dp"
                android:background="@drawable/bg_card" android:elevation="10dp"
                android:orientation="vertical" android:padding="18dp" android:visibility="gone">

                <LinearLayout android:layout_width="match_parent" android:layout_height="wrap_content"
                    android:orientation="horizontal" android:gravity="center_vertical">
                    <TextView android:id="@+id/c1icon" android:layout_width="30dp" android:layout_height="30dp"
                        android:background="@drawable/bg_sec_icon" android:gravity="center"
                        android:text="@string/glyph_check" android:textColor="@color/offex_white"
                        android:textSize="14sp" />
                    <TextView android:id="@+id/heroLabel" android:layout_width="0dp"
                        android:layout_height="wrap_content" android:layout_weight="1"
                        android:layout_marginStart="10dp" android:text="@string/your_address"
                        android:textColor="@color/offex_white" android:textSize="14sp"
                        android:textStyle="bold" />
                    <View android:id="@+id/liveDot" android:layout_width="8dp" android:layout_height="8dp"
                        android:background="@drawable/bg_dot_green" />
                    <TextView android:id="@+id/liveText" android:layout_width="wrap_content"
                        android:layout_height="wrap_content" android:layout_marginStart="6dp"
                        android:text="@string/live" android:textColor="#22C55E"
                        android:textSize="12sp" android:textStyle="bold" />
                </LinearLayout>

                <LinearLayout android:id="@+id/addrPill" android:layout_width="match_parent"
                    android:layout_height="wrap_content" android:layout_marginTop="14dp"
                    android:background="@drawable/bg_pill_address" android:gravity="center_vertical"
                    android:orientation="horizontal" android:paddingStart="16dp"
                    android:paddingEnd="8dp" android:paddingTop="6dp" android:paddingBottom="6dp">
                    <TextView android:id="@+id/addrText" android:layout_width="0dp"
                        android:layout_height="wrap_content" android:layout_weight="1"
                        android:textColor="?attr/oxText" android:textSize="16sp"
                        android:textStyle="bold" android:fontFamily="sans-serif-medium"
                        android:textIsSelectable="true" />
                    <TextView android:id="@+id/copyIconBtn" android:layout_width="38dp"
                        android:layout_height="38dp" android:layout_marginStart="8dp"
                        android:background="@drawable/bg_copy_btn" android:gravity="center"
                        android:text="@string/glyph_copy" android:textColor="@color/offex_white"
                        android:textSize="15sp" />
                </LinearLayout>

                <LinearLayout android:layout_width="match_parent" android:layout_height="wrap_content"
                    android:layout_marginTop="14dp" android:orientation="horizontal">
                    <androidx.appcompat.widget.AppCompatButton android:id="@+id/copyBtn"
                        android:layout_width="0dp" android:layout_height="46dp" android:layout_weight="1"
                        android:insetTop="0dp" android:insetBottom="0dp"
                        android:background="@drawable/bg_btn_blue" android:textColor="@color/offex_white"
                        android:textAllCaps="false" android:textSize="13sp" android:textStyle="bold"
                        android:text="@string/copy" />
                    <androidx.appcompat.widget.AppCompatButton android:id="@+id/refreshBtn"
                        android:layout_width="0dp" android:layout_height="46dp" android:layout_weight="1"
                        android:layout_marginStart="10dp" android:insetTop="0dp" android:insetBottom="0dp"
                        android:background="@drawable/bg_btn_darkblue" android:textColor="@color/offex_white"
                        android:textAllCaps="false" android:textSize="13sp"
                        android:text="@string/refresh" />
                    <androidx.appcompat.widget.AppCompatButton android:id="@+id/deleteBtn"
                        android:layout_width="0dp" android:layout_height="46dp" android:layout_weight="1"
                        android:layout_marginStart="10dp" android:insetTop="0dp" android:insetBottom="0dp"
                        android:background="@drawable/bg_btn_red" android:textColor="@color/offex_white"
                        android:textAllCaps="false" android:textSize="13sp"
                        android:text="@string/delete" />
                </LinearLayout>

                <TextView android:id="@+id/countdownText" android:layout_width="wrap_content"
                    android:layout_height="wrap_content" android:layout_marginTop="14dp"
                    android:background="@drawable/bg_chip" android:paddingStart="16dp" android:paddingEnd="16dp"
                    android:paddingTop="7dp" android:paddingBottom="7dp"
                    android:textColor="?attr/oxChipText" android:textSize="12sp" android:textStyle="bold" />
            </LinearLayout>

            <!-- ===== CARD 2 : create new email ===== -->
            <LinearLayout android:id="@+id/createCard" android:layout_width="match_parent"
                android:layout_height="wrap_content" android:layout_marginStart="16dp"
                android:layout_marginEnd="16dp" android:layout_marginTop="16dp"
                android:background="@drawable/bg_card" android:elevation="10dp"
                android:orientation="vertical" android:padding="18dp">

                <LinearLayout android:layout_width="match_parent" android:layout_height="wrap_content"
                    android:orientation="horizontal" android:gravity="center_vertical">
                    <TextView android:id="@+id/c2icon" android:layout_width="34dp" android:layout_height="34dp"
                        android:background="@drawable/bg_sec_icon" android:gravity="center"
                        android:text="@string/glyph_plus" android:textColor="@color/offex_white"
                        android:textSize="15sp" />
                    <LinearLayout android:layout_width="0dp" android:layout_height="wrap_content"
                        android:layout_weight="1" android:layout_marginStart="12dp" android:orientation="vertical">
                        <TextView android:id="@+id/createLabel" android:layout_width="wrap_content"
                            android:layout_height="wrap_content" android:text="@string/create_new_email"
                            android:textColor="?attr/oxText" android:textSize="16sp" android:textStyle="bold" />
                        <TextView android:id="@+id/secCreateSub" android:layout_width="wrap_content"
                            android:layout_height="wrap_content" android:layout_marginTop="2dp"
                            android:text="@string/create_sub" android:textColor="?attr/oxTextDim"
                            android:textSize="12sp" />
                    </LinearLayout>
                </LinearLayout>

                <EditText android:id="@+id/nameBox" android:layout_width="match_parent" android:layout_height="54dp"
                    android:layout_marginTop="14dp" android:background="@drawable/bg_input"
                    android:drawableStart="@drawable/bg_sec_icon" android:drawablePadding="10dp"
                    android:hint="@string/hint_name" android:inputType="text" android:maxLines="1"
                    android:paddingStart="16dp" android:paddingEnd="16dp"
                    android:textColorHint="?attr/oxTextMute" android:textColor="?attr/oxText"
                    android:textSize="15sp" />

                <Spinner android:id="@+id/domainBox" android:layout_width="match_parent"
                    android:layout_height="54dp" android:layout_marginTop="12dp"
                    android:background="@drawable/bg_input"
                    android:paddingStart="14dp" android:paddingEnd="14dp" />

                <androidx.appcompat.widget.AppCompatButton android:id="@+id/createBtn"
                    android:layout_width="match_parent" android:layout_height="56dp"
                    android:layout_marginTop="16dp" android:insetTop="0dp" android:insetBottom="0dp"
                    android:background="@drawable/bg_btn_primary" android:textColor="@color/offex_white"
                    android:textAllCaps="false" android:textSize="16sp" android:textStyle="bold"
                    android:fontFamily="sans-serif-medium" android:text="@string/create_inbox" />
            </LinearLayout>

            <!-- ===== CARD 3 : inbox ===== -->
            <LinearLayout android:id="@+id/inboxCard" android:layout_width="match_parent"
                android:layout_height="wrap_content" android:layout_marginStart="16dp"
                android:layout_marginEnd="16dp" android:layout_marginTop="16dp"
                android:background="@drawable/bg_card" android:elevation="10dp"
                android:orientation="vertical" android:padding="18dp">

                <LinearLayout android:layout_width="match_parent" android:layout_height="wrap_content"
                    android:orientation="horizontal" android:gravity="center_vertical">
                    <TextView android:id="@+id/c3icon" android:layout_width="34dp" android:layout_height="34dp"
                        android:background="@drawable/bg_sec_icon" android:gravity="center"
                        android:text="@string/glyph_mail" android:textColor="@color/offex_white"
                        android:textSize="15sp" />
                    <TextView android:id="@+id/secInbox" android:layout_width="0dp"
                        android:layout_height="wrap_content" android:layout_weight="1"
                        android:layout_marginStart="12dp" android:text="@string/inbox_title"
                        android:textColor="?attr/oxText" android:textSize="17sp"
                        android:textStyle="bold" android:fontFamily="sans-serif-medium" />
                    <TextView android:id="@+id/newPill" android:layout_width="wrap_content"
                        android:layout_height="wrap_content" android:background="@drawable/bg_pill_purple"
                        android:paddingStart="12dp" android:paddingEnd="12dp"
                        android:paddingTop="5dp" android:paddingBottom="5dp"
                        android:textColor="#C9B8FF" android:textSize="11sp" android:textStyle="bold"
                        android:visibility="gone" />
                </LinearLayout>

                <TextView android:id="@+id/inboxAddr" android:layout_width="match_parent"
                    android:layout_height="wrap_content" android:layout_marginTop="3dp"
                    android:textColor="?attr/oxTextDim" android:textSize="13sp" />

                <TextView android:id="@+id/emptyText" android:layout_width="match_parent"
                    android:layout_height="wrap_content" android:layout_marginTop="14dp"
                    android:background="@drawable/bg_nested" android:padding="20dp"
                    android:text="@string/no_messages" android:textColor="?attr/oxTextDim"
                    android:textSize="14sp" android:lineSpacingExtra="5dp" />

                <androidx.recyclerview.widget.RecyclerView android:id="@+id/msgList"
                    android:layout_width="match_parent" android:layout_height="wrap_content"
                    android:layout_marginTop="4dp" android:nestedScrollingEnabled="false" />
            </LinearLayout>

            <!-- ===== NATIVE AD ===== -->
            <LinearLayout android:id="@+id/nativeAdBox" android:layout_width="match_parent"
                android:layout_height="wrap_content" android:layout_marginStart="16dp"
                android:layout_marginEnd="16dp" android:layout_marginTop="16dp"
                android:orientation="vertical" android:visibility="gone" />

            <!-- ===== CARD 4 : switch email ===== -->
            <LinearLayout android:id="@+id/switchCard" android:layout_width="match_parent"
                android:layout_height="wrap_content" android:layout_marginStart="16dp"
                android:layout_marginEnd="16dp" android:layout_marginTop="16dp"
                android:background="@drawable/bg_card" android:elevation="10dp"
                android:orientation="vertical" android:padding="18dp">

                <LinearLayout android:layout_width="match_parent" android:layout_height="wrap_content"
                    android:orientation="horizontal" android:gravity="center_vertical">
                    <TextView android:id="@+id/c4icon" android:layout_width="34dp" android:layout_height="34dp"
                        android:background="@drawable/bg_sec_icon" android:gravity="center"
                        android:text="@string/glyph_switch" android:textColor="@color/offex_white"
                        android:textSize="15sp" />
                    <LinearLayout android:layout_width="0dp" android:layout_height="wrap_content"
                        android:layout_weight="1" android:layout_marginStart="12dp" android:orientation="vertical">
                        <TextView android:id="@+id/secSwitch" android:layout_width="wrap_content"
                            android:layout_height="wrap_content" android:text="@string/switch_title"
                            android:textColor="?attr/oxText" android:textSize="17sp"
                            android:textStyle="bold" android:fontFamily="sans-serif-medium" />
                        <TextView android:id="@+id/secChoose" android:layout_width="wrap_content"
                            android:layout_height="wrap_content" android:layout_marginTop="2dp"
                            android:text="@string/choose_email" android:textColor="?attr/oxTextDim"
                            android:textSize="12sp" />
                    </LinearLayout>
                    <TextView android:id="@+id/viewAllBtn" android:layout_width="wrap_content"
                        android:layout_height="wrap_content" android:background="@drawable/bg_chip"
                        android:paddingStart="14dp" android:paddingEnd="14dp"
                        android:paddingTop="7dp" android:paddingBottom="7dp"
                        android:text="@string/view_all" android:textColor="?attr/oxChipText"
                        android:textSize="12sp" android:textStyle="bold" />
                </LinearLayout>

                <TextView android:id="@+id/historyEmpty" android:layout_width="match_parent"
                    android:layout_height="wrap_content" android:layout_marginTop="14dp"
                    android:background="@drawable/bg_nested" android:padding="20dp"
                    android:text="@string/history_empty" android:textColor="?attr/oxTextDim"
                    android:textSize="14sp" />

                <LinearLayout android:id="@+id/historyBox" android:layout_width="match_parent"
                    android:layout_height="wrap_content" android:orientation="vertical" />
            </LinearLayout>

            <!-- ===== CARD 5 : why offex mail ===== -->
            <LinearLayout android:id="@+id/featuresCard" android:layout_width="match_parent"
                android:layout_height="wrap_content" android:layout_marginStart="16dp"
                android:layout_marginEnd="16dp" android:layout_marginTop="16dp"
                android:background="@drawable/bg_card" android:elevation="10dp"
                android:orientation="vertical" android:padding="18dp">

                <TextView android:id="@+id/secFeatures" android:layout_width="wrap_content"
                    android:layout_height="wrap_content" android:text="@string/features_title"
                    android:textColor="?attr/oxText" android:textSize="17sp"
                    android:textStyle="bold" android:fontFamily="sans-serif-medium" />
                <TextView android:id="@+id/secFeaturesSub" android:layout_width="match_parent"
                    android:layout_height="wrap_content" android:layout_marginTop="3dp"
                    android:text="@string/features_sub" android:textColor="?attr/oxTextDim"
                    android:textSize="13sp" />

                <LinearLayout android:id="@+id/featuresBox" android:layout_width="match_parent"
                    android:layout_height="wrap_content" android:layout_marginTop="6dp"
                    android:orientation="vertical">
                    <LinearLayout android:layout_width="match_parent" android:layout_height="wrap_content"
                        android:layout_marginTop="10dp" android:background="@drawable/bg_nested"
                        android:orientation="horizontal" android:gravity="center_vertical" android:padding="14dp">
                        <TextView android:id="@+id/fi1" android:layout_width="42dp" android:layout_height="42dp"
                            android:background="@drawable/bg_logo" android:gravity="center"
                            android:text="&#9889;" android:textColor="@color/offex_white" android:textSize="19sp" />
                        <LinearLayout android:layout_width="0dp" android:layout_height="wrap_content"
                            android:layout_weight="1" android:layout_marginStart="14dp" android:orientation="vertical">
                            <TextView android:layout_width="match_parent" android:layout_height="wrap_content"
                                android:text="@string/feat1_t" android:textColor="?attr/oxText"
                                android:textSize="14sp" android:textStyle="bold" />
                            <TextView android:layout_width="match_parent" android:layout_height="wrap_content"
                                android:layout_marginTop="2dp" android:text="@string/feat1_d"
                                android:textColor="?attr/oxTextDim" android:textSize="12.5sp" android:lineSpacingExtra="3dp" />
                        </LinearLayout>
                        <TextView android:layout_width="wrap_content" android:layout_height="wrap_content"
                            android:layout_marginStart="6dp" android:text="@string/glyph_chevron"
                            android:textColor="?attr/oxTextMute" android:textSize="20sp" />
                    </LinearLayout>
                    <LinearLayout android:layout_width="match_parent" android:layout_height="wrap_content"
                        android:layout_marginTop="10dp" android:background="@drawable/bg_nested"
                        android:orientation="horizontal" android:gravity="center_vertical" android:padding="14dp">
                        <TextView android:id="@+id/fi2" android:layout_width="42dp" android:layout_height="42dp"
                            android:background="@drawable/bg_logo" android:gravity="center"
                            android:text="&#128273;" android:textColor="@color/offex_white" android:textSize="19sp" />
                        <LinearLayout android:layout_width="0dp" android:layout_height="wrap_content"
                            android:layout_weight="1" android:layout_marginStart="14dp" android:orientation="vertical">
                            <TextView android:layout_width="match_parent" android:layout_height="wrap_content"
                                android:text="@string/feat2_t" android:textColor="?attr/oxText"
                                android:textSize="14sp" android:textStyle="bold" />
                            <TextView android:layout_width="match_parent" android:layout_height="wrap_content"
                                android:layout_marginTop="2dp" android:text="@string/feat2_d"
                                android:textColor="?attr/oxTextDim" android:textSize="12.5sp" android:lineSpacingExtra="3dp" />
                        </LinearLayout>
                        <TextView android:layout_width="wrap_content" android:layout_height="wrap_content"
                            android:layout_marginStart="6dp" android:text="@string/glyph_chevron"
                            android:textColor="?attr/oxTextMute" android:textSize="20sp" />
                    </LinearLayout>
                    <LinearLayout android:layout_width="match_parent" android:layout_height="wrap_content"
                        android:layout_marginTop="10dp" android:background="@drawable/bg_nested"
                        android:orientation="horizontal" android:gravity="center_vertical" android:padding="14dp">
                        <TextView android:id="@+id/fi3" android:layout_width="42dp" android:layout_height="42dp"
                            android:background="@drawable/bg_logo" android:gravity="center"
                            android:text="&#128279;" android:textColor="@color/offex_white" android:textSize="19sp" />
                        <LinearLayout android:layout_width="0dp" android:layout_height="wrap_content"
                            android:layout_weight="1" android:layout_marginStart="14dp" android:orientation="vertical">
                            <TextView android:layout_width="match_parent" android:layout_height="wrap_content"
                                android:text="@string/feat3_t" android:textColor="?attr/oxText"
                                android:textSize="14sp" android:textStyle="bold" />
                            <TextView android:layout_width="match_parent" android:layout_height="wrap_content"
                                android:layout_marginTop="2dp" android:text="@string/feat3_d"
                                android:textColor="?attr/oxTextDim" android:textSize="12.5sp" android:lineSpacingExtra="3dp" />
                        </LinearLayout>
                        <TextView android:layout_width="wrap_content" android:layout_height="wrap_content"
                            android:layout_marginStart="6dp" android:text="@string/glyph_chevron"
                            android:textColor="?attr/oxTextMute" android:textSize="20sp" />
                    </LinearLayout>
                    <LinearLayout android:layout_width="match_parent" android:layout_height="wrap_content"
                        android:layout_marginTop="10dp" android:background="@drawable/bg_nested"
                        android:orientation="horizontal" android:gravity="center_vertical" android:padding="14dp">
                        <TextView android:id="@+id/fi4" android:layout_width="42dp" android:layout_height="42dp"
                            android:background="@drawable/bg_logo" android:gravity="center"
                            android:text="&#128276;" android:textColor="@color/offex_white" android:textSize="19sp" />
                        <LinearLayout android:layout_width="0dp" android:layout_height="wrap_content"
                            android:layout_weight="1" android:layout_marginStart="14dp" android:orientation="vertical">
                            <TextView android:layout_width="match_parent" android:layout_height="wrap_content"
                                android:text="@string/feat4_t" android:textColor="?attr/oxText"
                                android:textSize="14sp" android:textStyle="bold" />
                            <TextView android:layout_width="match_parent" android:layout_height="wrap_content"
                                android:layout_marginTop="2dp" android:text="@string/feat4_d"
                                android:textColor="?attr/oxTextDim" android:textSize="12.5sp" android:lineSpacingExtra="3dp" />
                        </LinearLayout>
                        <TextView android:layout_width="wrap_content" android:layout_height="wrap_content"
                            android:layout_marginStart="6dp" android:text="@string/glyph_chevron"
                            android:textColor="?attr/oxTextMute" android:textSize="20sp" />
                    </LinearLayout>
                    <LinearLayout android:layout_width="match_parent" android:layout_height="wrap_content"
                        android:layout_marginTop="10dp" android:background="@drawable/bg_nested"
                        android:orientation="horizontal" android:gravity="center_vertical" android:padding="14dp">
                        <TextView android:id="@+id/fi5" android:layout_width="42dp" android:layout_height="42dp"
                            android:background="@drawable/bg_logo" android:gravity="center"
                            android:text="&#127760;" android:textColor="@color/offex_white" android:textSize="19sp" />
                        <LinearLayout android:layout_width="0dp" android:layout_height="wrap_content"
                            android:layout_weight="1" android:layout_marginStart="14dp" android:orientation="vertical">
                            <TextView android:layout_width="match_parent" android:layout_height="wrap_content"
                                android:text="@string/feat5_t" android:textColor="?attr/oxText"
                                android:textSize="14sp" android:textStyle="bold" />
                            <TextView android:layout_width="match_parent" android:layout_height="wrap_content"
                                android:layout_marginTop="2dp" android:text="@string/feat5_d"
                                android:textColor="?attr/oxTextDim" android:textSize="12.5sp" android:lineSpacingExtra="3dp" />
                        </LinearLayout>
                        <TextView android:layout_width="wrap_content" android:layout_height="wrap_content"
                            android:layout_marginStart="6dp" android:text="@string/glyph_chevron"
                            android:textColor="?attr/oxTextMute" android:textSize="20sp" />
                    </LinearLayout>
                    <LinearLayout android:layout_width="match_parent" android:layout_height="wrap_content"
                        android:layout_marginTop="10dp" android:background="@drawable/bg_nested"
                        android:orientation="horizontal" android:gravity="center_vertical" android:padding="14dp">
                        <TextView android:id="@+id/fi6" android:layout_width="42dp" android:layout_height="42dp"
                            android:background="@drawable/bg_logo" android:gravity="center"
                            android:text="&#9203;" android:textColor="@color/offex_white" android:textSize="19sp" />
                        <LinearLayout android:layout_width="0dp" android:layout_height="wrap_content"
                            android:layout_weight="1" android:layout_marginStart="14dp" android:orientation="vertical">
                            <TextView android:layout_width="match_parent" android:layout_height="wrap_content"
                                android:text="@string/feat6_t" android:textColor="?attr/oxText"
                                android:textSize="14sp" android:textStyle="bold" />
                            <TextView android:layout_width="match_parent" android:layout_height="wrap_content"
                                android:layout_marginTop="2dp" android:text="@string/feat6_d"
                                android:textColor="?attr/oxTextDim" android:textSize="12.5sp" android:lineSpacingExtra="3dp" />
                        </LinearLayout>
                        <TextView android:layout_width="wrap_content" android:layout_height="wrap_content"
                            android:layout_marginStart="6dp" android:text="@string/glyph_chevron"
                            android:textColor="?attr/oxTextMute" android:textSize="20sp" />
                    </LinearLayout>
                </LinearLayout>
            </LinearLayout>
        </LinearLayout>
    </ScrollView>

    <!-- ===== BOTTOM NAV ===== -->
    <LinearLayout android:id="@+id/navBar" android:layout_width="match_parent"
        android:layout_height="wrap_content" android:layout_gravity="bottom"
        android:background="@drawable/bg_nav" android:orientation="horizontal"
        android:elevation="20dp" android:paddingStart="8dp" android:paddingEnd="8dp"
        android:paddingTop="8dp" android:paddingBottom="12dp">

        <LinearLayout android:id="@+id/navEmail" android:layout_width="0dp" android:layout_height="wrap_content"
            android:layout_weight="1" android:orientation="vertical" android:gravity="center"
            android:clickable="true" android:focusable="true"
            android:background="?android:attr/selectableItemBackground"
            android:paddingTop="8dp" android:paddingBottom="6dp">
            <View android:id="@+id/navIndEmail" android:layout_width="26dp" android:layout_height="3dp"
                android:background="@drawable/bg_indicator" android:visibility="invisible" />
            <TextView android:id="@+id/navIconEmail" android:layout_width="wrap_content" android:layout_height="wrap_content"
                android:layout_marginTop="8dp" android:text="@string/glyph_mail" android:textSize="18sp"
                android:textColor="?attr/oxTextMute" />
            <TextView android:layout_width="wrap_content" android:layout_height="wrap_content"
                android:layout_marginTop="4dp" android:text="@string/nav_email" android:textSize="10sp"
                android:textColor="?attr/oxTextMute" />
        </LinearLayout>

        <LinearLayout android:id="@+id/navInbox" android:layout_width="0dp" android:layout_height="wrap_content"
            android:layout_weight="1" android:orientation="vertical" android:gravity="center"
            android:clickable="true" android:focusable="true"
            android:background="?android:attr/selectableItemBackground"
            android:paddingTop="8dp" android:paddingBottom="6dp">
            <View android:id="@+id/navIndInbox" android:layout_width="26dp" android:layout_height="3dp"
                android:background="@drawable/bg_indicator" android:visibility="invisible" />
            <TextView android:id="@+id/navIconInbox" android:layout_width="wrap_content" android:layout_height="wrap_content"
                android:layout_marginTop="8dp" android:text="@string/glyph_inbox" android:textSize="18sp"
                android:textColor="?attr/oxTextMute" />
            <TextView android:layout_width="wrap_content" android:layout_height="wrap_content"
                android:layout_marginTop="4dp" android:text="@string/nav_inbox" android:textSize="10sp"
                android:textColor="?attr/oxTextMute" />
        </LinearLayout>

        <LinearLayout android:id="@+id/navSwitch" android:layout_width="0dp" android:layout_height="wrap_content"
            android:layout_weight="1" android:orientation="vertical" android:gravity="center"
            android:clickable="true" android:focusable="true"
            android:background="?android:attr/selectableItemBackground"
            android:paddingTop="8dp" android:paddingBottom="6dp">
            <View android:id="@+id/navIndSwitch" android:layout_width="26dp" android:layout_height="3dp"
                android:background="@drawable/bg_indicator" android:visibility="invisible" />
            <TextView android:id="@+id/navIconSwitch" android:layout_width="wrap_content" android:layout_height="wrap_content"
                android:layout_marginTop="8dp" android:text="@string/glyph_switch" android:textSize="18sp"
                android:textColor="?attr/oxTextMute" />
            <TextView android:layout_width="wrap_content" android:layout_height="wrap_content"
                android:layout_marginTop="4dp" android:text="@string/nav_switch" android:textSize="10sp"
                android:textColor="?attr/oxTextMute" />
        </LinearLayout>

        <LinearLayout android:id="@+id/navMore" android:layout_width="0dp" android:layout_height="wrap_content"
            android:layout_weight="1" android:orientation="vertical" android:gravity="center"
            android:clickable="true" android:focusable="true"
            android:background="?android:attr/selectableItemBackground"
            android:paddingTop="8dp" android:paddingBottom="6dp">
            <View android:id="@+id/navIndMore" android:layout_width="26dp" android:layout_height="3dp"
                android:background="@drawable/bg_indicator" android:visibility="invisible" />
            <TextView android:id="@+id/navIconMore" android:layout_width="wrap_content" android:layout_height="wrap_content"
                android:layout_marginTop="8dp" android:text="@string/glyph_more" android:textSize="18sp"
                android:textColor="?attr/oxTextMute" />
            <TextView android:layout_width="wrap_content" android:layout_height="wrap_content"
                android:layout_marginTop="4dp" android:text="@string/nav_more" android:textSize="10sp"
                android:textColor="?attr/oxTextMute" />
        </LinearLayout>
    </LinearLayout>
</FrameLayout>
"""
W(RES + "/layout/activity_main.xml", MAIN_XML)
print("AB: wrote activity_main.xml")


# ===========================================================================
# 6 : item_message.xml  -  avatar initial + sender + subject + tags + time + chevron.
# ===========================================================================
ITEM_XML = """<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent" android:layout_height="wrap_content"
    android:layout_marginTop="10dp" android:background="@drawable/bg_nested"
    android:orientation="horizontal" android:gravity="center_vertical" android:padding="14dp">

    <TextView android:id="@+id/mAvatar" android:layout_width="44dp" android:layout_height="44dp"
        android:background="@drawable/bg_avatar" android:gravity="center"
        android:textColor="@color/offex_white" android:textSize="17sp" android:textStyle="bold" />

    <LinearLayout android:layout_width="0dp" android:layout_height="wrap_content"
        android:layout_weight="1" android:layout_marginStart="13dp" android:orientation="vertical">

        <LinearLayout android:layout_width="match_parent" android:layout_height="wrap_content"
            android:orientation="horizontal" android:gravity="center_vertical">
            <TextView android:id="@+id/mSender" android:layout_width="0dp" android:layout_height="wrap_content"
                android:layout_weight="1" android:maxLines="1" android:ellipsize="end"
                android:textColor="?attr/oxText" android:textSize="14sp" android:textStyle="bold" />
            <TextView android:id="@+id/mTime" android:layout_width="wrap_content" android:layout_height="wrap_content"
                android:layout_marginStart="8dp" android:textColor="?attr/oxTextMute" android:textSize="11sp" />
        </LinearLayout>

        <TextView android:id="@+id/mSubject" android:layout_width="match_parent" android:layout_height="wrap_content"
            android:layout_marginTop="4dp" android:maxLines="2" android:ellipsize="end"
            android:textColor="?attr/oxTextDim" android:textSize="13sp" />

        <LinearLayout android:layout_width="match_parent" android:layout_height="wrap_content"
            android:layout_marginTop="9dp" android:orientation="horizontal" android:gravity="center_vertical">
            <TextView android:id="@+id/mService" android:layout_width="wrap_content" android:layout_height="wrap_content"
                android:background="@drawable/bg_chip_green" android:paddingStart="11dp" android:paddingEnd="11dp"
                android:paddingTop="4dp" android:paddingBottom="4dp"
                android:textColor="@color/offex_green" android:textSize="10sp" android:textStyle="bold"
                android:letterSpacing="0.06" android:text="@string/item_mail_label" />
            <TextView android:id="@+id/mOtp" android:layout_width="wrap_content" android:layout_height="wrap_content"
                android:layout_marginStart="8dp" android:background="@drawable/bg_tag_grey"
                android:paddingStart="11dp" android:paddingEnd="11dp" android:paddingTop="4dp" android:paddingBottom="4dp"
                android:textColor="?attr/oxTextDim" android:textSize="11sp" android:textStyle="bold"
                android:visibility="gone" />
        </LinearLayout>
    </LinearLayout>

    <TextView android:layout_width="wrap_content" android:layout_height="wrap_content"
        android:layout_marginStart="8dp" android:text="@string/glyph_chevron"
        android:textColor="?attr/oxTextMute" android:textSize="20sp" />
</LinearLayout>
"""
W(RES + "/layout/item_message.xml", ITEM_XML)
print("AB: wrote item_message.xml")


# ===========================================================================
# 7 : MailAdapter.java  -  bind the avatar initial.
# ===========================================================================
MAILADAPTER = """package online.mytempmail.app;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.TextView;
import androidx.annotation.NonNull;
import androidx.recyclerview.widget.RecyclerView;
import java.util.List;
public class MailAdapter extends RecyclerView.Adapter<MailAdapter.VH> {
    public interface OnClick { void click(Mail m); }
    private final List<Mail> data; private final OnClick cb;
    public MailAdapter(List<Mail> d, OnClick c){ data=d; cb=c; }
    @NonNull @Override public VH onCreateViewHolder(@NonNull ViewGroup p,int t){
        return new VH(LayoutInflater.from(p.getContext()).inflate(R.layout.item_message,p,false));
    }
    @Override public void onBindViewHolder(@NonNull VH h,int pos){
        Mail m=data.get(pos);
        h.service.setText(m.service==null||m.service.isEmpty()?"MAIL":m.service.toUpperCase());
        h.sender.setText(m.sender);
        h.subject.setText(m.subject);
        h.time.setText(m.receivedAt);
        boolean has=m.otp!=null&&!m.otp.isEmpty();
        h.otp.setVisibility(has?View.VISIBLE:View.GONE);
        h.otp.setText(m.otp);
        if(h.avatar!=null){
            String src = (m.sender==null||m.sender.isEmpty())? "?" : m.sender.trim();
            String initial = src.isEmpty()? "?" : src.substring(0,1).toUpperCase();
            h.avatar.setText(initial);
        }
        h.itemView.setOnClickListener(v->cb.click(m));
    }
    @Override public int getItemCount(){ return data.size(); }
    static class VH extends RecyclerView.ViewHolder {
        TextView service,sender,subject,time,otp,avatar;
        VH(View v){ super(v);
            service=v.findViewById(R.id.mService); sender=v.findViewById(R.id.mSender);
            subject=v.findViewById(R.id.mSubject); time=v.findViewById(R.id.mTime);
            otp=v.findViewById(R.id.mOtp); avatar=v.findViewById(R.id.mAvatar); }
    }
}
"""
W(J + "/MailAdapter.java", MAILADAPTER)
print("AB: wrote MailAdapter.java")


# ===========================================================================
# 8 : Ui.java  -  remote-appearance driven; defaults match the reference.
# ===========================================================================
UI_JAVA = r'''package online.mytempmail.app;
import android.app.Activity;
import android.content.Intent;
import android.graphics.Color;
import android.graphics.drawable.GradientDrawable;
import android.net.Uri;
import android.view.View;
import android.widget.TextView;
import org.json.JSONObject;

/**
 * v4.5 - the whole app look is driven by the "appearance" object that the
 * admin panel pushes to /api/app-config. Ui.apply() reads it and applies the
 * theme mode, accent colours, corner radius, titles, button labels, section
 * toggles, banner and links to the already-inflated screen - so the look can
 * change WITHOUT a new APK and without a version bump.
 *
 * The built-in defaults now describe the premium dark navy/purple reference:
 * glass cards, a purple->blue accent gradient, blue icons/secondary text,
 * green Live/Active dots and a red Delete - all still overridable remotely.
 */
public class Ui {
    private static boolean heroShown = false;

    // reference defaults (purple -> blue)
    public static final int DEF_ACCENT  = 0xFF6D4DFF;
    public static final int DEF_ACCENT2 = 0xFF3B82F6;

    private static int dp(Activity a, int v){
        try { return (int)(a.getResources().getDisplayMetrics().density * v); } catch(Exception e){ return v; }
    }
    private static int col(String hex, int def){
        try { String s = hex == null ? "" : hex.trim(); if(s.isEmpty()) return def; return Color.parseColor(s); }
        catch(Exception e){ return def; }
    }
    public static int accent(){
        try { return col(Config.appearance().optString("accent", ""), DEF_ACCENT); }
        catch(Exception e){ return DEF_ACCENT; }
    }
    public static int navIdle(){ return Prefs.isDark() ? 0xFF7B87B5 : 0xFF9A96AD; }

    private static GradientDrawable grad(int a, int b, float radius){
        GradientDrawable g = new GradientDrawable(GradientDrawable.Orientation.LEFT_RIGHT, new int[]{a, b});
        g.setCornerRadius(radius);
        return g;
    }
    private static GradientDrawable gradRadii(int a, int b, float[] radii){
        GradientDrawable g = new GradientDrawable(GradientDrawable.Orientation.LEFT_RIGHT, new int[]{a, b});
        g.setCornerRadii(radii);
        return g;
    }
    private static GradientDrawable solid(int color, float radius, int stroke, int sw){
        GradientDrawable g = new GradientDrawable();
        g.setColor(color); g.setCornerRadius(radius);
        if(sw > 0) g.setStroke(sw, stroke);
        return g;
    }
    private static GradientDrawable solidRadii(int color, float[] radii, int stroke, int sw){
        GradientDrawable g = new GradientDrawable();
        g.setColor(color); g.setCornerRadii(radii);
        if(sw > 0) g.setStroke(sw, stroke);
        return g;
    }
    private static void setBg(Activity a, int id, android.graphics.drawable.Drawable d){
        try { View v = a.findViewById(id); if(v != null) v.setBackground(d); } catch(Exception e){}
    }
    private static void setText(Activity a, int id, String s){
        try { if(s == null || s.trim().isEmpty()) return; View v = a.findViewById(id);
              if(v instanceof TextView) ((TextView) v).setText(s); } catch(Exception e){}
    }
    private static void setColor(Activity a, int id, int c){
        try { View v = a.findViewById(id); if(v instanceof TextView) ((TextView) v).setTextColor(c); } catch(Exception e){}
    }
    private static void vis(Activity a, int id, boolean show){
        try { View v = a.findViewById(id); if(v != null) v.setVisibility(show ? View.VISIBLE : View.GONE); } catch(Exception e){}
    }

    /** Title + body of the empty inbox state, both remote-driven. */
    public static void setEmptyText(Activity a){
        try {
            TextView t = a.findViewById(R.id.emptyText);
            if(t == null) return;
            String title = Config.appStr("empty_title", "No mail yet");
            String body = Config.str("inbox_empty", Config.appStr("empty_body", a.getString(R.string.no_messages)));
            t.setText(title + "\n\n" + body);
        } catch(Exception e){}
    }

    /** If the panel changed the default theme mode and the user never picked
     *  one themselves, switch to it and rebuild the screen. */
    public static void applyTheme(Activity a){
        try {
            String mode = Config.appearance().optString("theme_mode", "");
            if(mode.isEmpty()) return;
            if(Prefs.themeChosen()) return;
            if(!mode.equals(Prefs.themeMode())){ Prefs.setThemeMode(mode); a.recreate(); }
        } catch(Exception e){}
    }

    public static void apply(Activity a){
        try { applyTheme(a); } catch(Exception e){}
        try {
            JSONObject ap = Config.appearance();
            int accent  = col(ap.optString("accent", ""), DEF_ACCENT);
            int accent2 = col(ap.optString("accent2", ""), DEF_ACCENT2);
            int gs = col(ap.optString("gradient_start", ""), accent);
            int ge = col(ap.optString("gradient_end", ""), accent2);
            int radius = ap.optInt("radius", 22);
            if(radius < 0) radius = 0;
            float r = dp(a, radius > 0 ? radius : 22);
            float pill = dp(a, 999);
            boolean dark = Prefs.isDark();

            int card        = dark ? 0xCC151A45 : 0xFFFFFFFF;
            int cardBorder  = dark ? 0x33FFFFFF : 0xFFE7E3F7;
            int text        = dark ? 0xFFFFFFFF : 0xFF171330;
            int textDim     = dark ? 0xFFAAB4DE : 0xFF5C5875;
            int nested      = dark ? 0xFF141A44 : 0xFFF3F1FB;
            int nestedBord  = dark ? 0xFF2A3566 : 0xFFE3DFF2;
            int darkBlue    = dark ? 0xFF1E2A5E : 0xFFE3E8FF;
            int red         = 0xFFEF4444;
            int chipBg      = dark ? 0xFF3A2A7A : 0xFFEEF0FF;
            int chipBorder  = dark ? accent : 0xFFD9D2FF;
            int chipText    = dark ? 0xFFC9B8FF : 0xFF4C2FD6;
            int navBg       = dark ? 0xFF0E1030 : 0xFFFFFFFF;

            // header
            setColor(a, R.id.heroTitle, 0xFFFFFFFF);
            setColor(a, R.id.heroTagline, 0xFFAAB4DE);
            setBg(a, R.id.heroLogo, gradRadii(gs, ge, new float[]{
                    dp(a,16), dp(a,16), dp(a,16), dp(a,16), dp(a,16), dp(a,16), dp(a,16), dp(a,16)}));
            setBg(a, R.id.settingsBtn, solid(0x1FFFFFFF, pill, 0x33FFFFFF, dp(a,1)));

            // card 1 - your temporary address
            setBg(a, R.id.activeCard, solid(card, r, cardBorder, dp(a,1)));
            setColor(a, R.id.heroLabel, 0xFFFFFFFF);
            setBg(a, R.id.c1icon, grad(gs, ge, dp(a,999)));
            setBg(a, R.id.liveDot, solid(0xFF22C55E, dp(a,999), 0, 0));
            setColor(a, R.id.liveText, 0xFF22C55E);
            setBg(a, R.id.addrPill, solid(nested, dp(a,14), nestedBord, dp(a,1)));
            setColor(a, R.id.addrText, text);
            setBg(a, R.id.copyIconBtn, solid(accent2, dp(a,12), 0, 0));
            setBg(a, R.id.copyBtn, solid(accent2, pill, 0, 0));
            setBg(a, R.id.refreshBtn, solid(darkBlue, pill, cardBorder, dp(a,1)));
            setBg(a, R.id.deleteBtn, solid(red, pill, 0, 0));
            setBg(a, R.id.countdownText, solid(chipBg, pill, chipBorder, dp(a,1)));
            setColor(a, R.id.countdownText, chipText);

            // card 2 - create new email
            setBg(a, R.id.createCard, solid(card, r, cardBorder, dp(a,1)));
            setBg(a, R.id.c2icon, grad(gs, ge, dp(a,999)));
            setColor(a, R.id.createLabel, text);
            setColor(a, R.id.secCreateSub, textDim);
            setBg(a, R.id.nameBox, solid(nested, dp(a,16), nestedBord, dp(a,1)));
            setBg(a, R.id.domainBox, solid(nested, dp(a,16), nestedBord, dp(a,1)));
            setBg(a, R.id.createBtn, grad(gs, ge, pill));

            // card 3 - inbox
            setBg(a, R.id.inboxCard, solid(card, r, cardBorder, dp(a,1)));
            setBg(a, R.id.c3icon, grad(gs, ge, dp(a,999)));
            setColor(a, R.id.secInbox, text);
            setColor(a, R.id.inboxAddr, textDim);
            setBg(a, R.id.newPill, solid(chipBg, pill, chipBorder, dp(a,1)));
            setColor(a, R.id.newPill, chipText);
            setBg(a, R.id.emptyText, solid(nested, dp(a,16), nestedBord, dp(a,1)));
            setColor(a, R.id.emptyText, textDim);

            // card 4 - switch email
            setBg(a, R.id.switchCard, solid(card, r, cardBorder, dp(a,1)));
            setBg(a, R.id.c4icon, grad(gs, ge, dp(a,999)));
            setColor(a, R.id.secSwitch, text);
            setColor(a, R.id.secChoose, textDim);
            setBg(a, R.id.viewAllBtn, solid(chipBg, pill, chipBorder, dp(a,1)));
            setColor(a, R.id.viewAllBtn, chipText);
            setBg(a, R.id.historyEmpty, solid(nested, dp(a,16), nestedBord, dp(a,1)));
            setColor(a, R.id.historyEmpty, textDim);

            // card 5 - why offex mail
            setBg(a, R.id.featuresCard, solid(card, r, cardBorder, dp(a,1)));
            setColor(a, R.id.secFeatures, text);
            setColor(a, R.id.secFeaturesSub, textDim);
            int[] fi = {R.id.fi1, R.id.fi2, R.id.fi3, R.id.fi4, R.id.fi5, R.id.fi6};
            for(int id : fi) setBg(a, id, grad(gs, ge, dp(a, 999)));

            // bottom nav
            setBg(a, R.id.navBar, solidRadii(navBg,
                    new float[]{r, r, r, r, 0, 0, 0, 0}, cardBorder, dp(a,1)));

            // remote titles / labels (unchanged keys)
            setText(a, R.id.heroTitle, Config.appStr("hero_title", a.getString(R.string.app_name)));
            setText(a, R.id.heroTagline, Config.appStr("hero_tagline", a.getString(R.string.tagline)));
            setText(a, R.id.heroLabel, Config.appStr("hero_label", a.getString(R.string.your_address)));
            setText(a, R.id.createLabel, Config.appStr("create_title", a.getString(R.string.create_new_email)));
            setText(a, R.id.secCreateSub, Config.appStr("create_sub", a.getString(R.string.create_sub)));
            setText(a, R.id.createBtn, "\u2726  " + Config.appStr("create_label", a.getString(R.string.create_inbox)) + "   \u2192");
            setText(a, R.id.copyBtn, "\u29C9  " + Config.appStr("copy_label", a.getString(R.string.copy)));
            setText(a, R.id.refreshBtn, "\u27F3  " + Config.appStr("refresh_label", a.getString(R.string.refresh)));
            setText(a, R.id.deleteBtn, "\uD83D\uDDD1  " + Config.appStr("delete_label", a.getString(R.string.delete)));
            setText(a, R.id.secInbox, Config.appStr("inbox_title", a.getString(R.string.inbox_title)));
            setText(a, R.id.secSwitch, Config.appStr("switch_title", a.getString(R.string.switch_title)));
            setText(a, R.id.secChoose, Config.appStr("switch_sub", a.getString(R.string.choose_email)));
            setText(a, R.id.viewAllBtn, Config.appStr("view_all_label", a.getString(R.string.view_all)));
            setText(a, R.id.secFeatures, Config.appStr("features_title", a.getString(R.string.features_title)));
            setText(a, R.id.secFeaturesSub, Config.appStr("features_sub", a.getString(R.string.features_sub)));
            setText(a, R.id.liveText, Config.appStr("live_label", a.getString(R.string.live)));
            setEmptyText(a);

            boolean showHero = Config.flag("show_hero", true);
            vis(a, R.id.heroBox, showHero);
            boolean showSwitch = Config.flag("show_switch", true);
            vis(a, R.id.secSwitch, showSwitch);
            vis(a, R.id.secChoose, showSwitch);
            vis(a, R.id.switchCard, showSwitch);
            if(!showSwitch) vis(a, R.id.historyBox, false);

            TextView banner = a.findViewById(R.id.bannerText);
            if(banner != null){
                boolean on = ap.optBoolean("banner_on", false) && Config.appFlag("show_banner", true);
                String bt = ap.optString("banner_text", "");
                if(on && bt != null && !bt.trim().isEmpty()){
                    banner.setText(bt);
                    final String url = ap.optString("banner_url", "");
                    banner.setOnClickListener(v -> openUrl(a, url));
                    banner.setVisibility(View.VISIBLE);
                    banner.setAlpha(0f);
                    banner.animate().alpha(1f).setDuration(260).start();
                } else {
                    banner.setVisibility(View.GONE);
                }
            }

            if(!heroShown){
                heroShown = true;
                View hero = a.findViewById(R.id.heroBox);
                if(hero != null){
                    hero.setAlpha(0f);
                    hero.setTranslationY(dp(a, 12));
                    hero.animate().alpha(1f).translationY(0f).setDuration(340).start();
                }
            }
        } catch(Exception e){}
    }

    private static void openUrl(Activity a, String url){
        try {
            if(url == null) return;
            String u = url.trim();
            if(!(u.startsWith("http://") || u.startsWith("https://"))) return;
            a.startActivity(new Intent(Intent.ACTION_VIEW, Uri.parse(u)));
        } catch(Exception e){}
    }
}
'''
W(J + "/Ui.java", UI_JAVA)
print("AB: wrote Ui.java")


# ===========================================================================
# 9 : MainActivity - "N new" pill + reference switch rows (targeted patches).
# ===========================================================================
MAIN = J + "/MainActivity.java"

REP(MAIN,
    "    private LinearLayout activeCard, historyBox; private TextView addrText,countdownText,emptyText,historyEmpty,inboxAddr;",
    "    private LinearLayout activeCard, historyBox; private TextView addrText,countdownText,emptyText,historyEmpty,inboxAddr,newPill;",
    "newPill field")

REP(MAIN,
    "        inboxAddr=findViewById(R.id.inboxAddr);",
    "        inboxAddr=findViewById(R.id.inboxAddr);\n        newPill=findViewById(R.id.newPill);",
    "newPill bind")

REP(MAIN,
    "                    emptyText.setVisibility(mails.isEmpty()?View.VISIBLE:View.GONE);",
    "                    emptyText.setVisibility(mails.isEmpty()?View.VISIBLE:View.GONE);\n"
    "                    if(newPill!=null){ int nn=mails.size(); newPill.setText(nn+\" \"+getString(R.string.new_suffix)); newPill.setVisibility(nn>0?View.VISIBLE:View.GONE); }",
    "newPill update")

REP(MAIN,
    "                row.setBackgroundResource(R.drawable.bg_card);",
    "                row.setBackgroundResource(R.drawable.bg_pill_row);",
    "switch row pill bg")

REP(MAIN,
    '                t.setText(addr+(addr.equals(cur)?"  \\u2022 active":""));',
    '                t.setText(addr+(addr.equals(cur)?"   \\u25CF Active":""));',
    "switch row active label")

REP(MAIN,
    "                t.setTextSize(14); t.setTextColor(addr.equals(cur)?Ui.accent():resolveText());",
    "                t.setTextSize(14); t.setTextColor(addr.equals(cur)?0xFF22C55E:resolveText());",
    "switch row active colour")

REP(MAIN,
    '                del.setText("\\u2715"); del.setTextSize(16); del.setTextColor(0xFFE5484D);',
    '                del.setText("\\u2715"); del.setTextSize(16); del.setTextColor(0xFF8B5CF6);',
    "switch row delete colour")


# ===========================================================================
# 10 : default to the dark premium theme (reference is what a user sees).
# ===========================================================================
REP(J + "/Prefs.java",
    '    public static String themeMode(){ return sp.getString("theme","light"); }',
    '    public static String themeMode(){ return sp.getString("theme","dark"); }',
    "default theme -> dark")

# Skin: the "dark" style is the premium reference theme.
REP(J + "/Skin.java",
    "        a.setTheme(Prefs.isDark() ? R.style.Theme_Offex_Dark : R.style.Theme_Offex);",
    "        a.setTheme(Prefs.isDark() ? R.style.Theme_Offex_Dark : R.style.Theme_Offex_Light);",
    "skin -> light variant")


# ===========================================================================
# 11 : version bump 4.4 -> 4.5.
# ===========================================================================
REP(J + "/Config.java",
    '            if(latest.equals("4.4")) return;',
    '            if(latest.equals("4.5")) return;',
    "self-version 4.5")

REP(J + "/SupportActivity.java",
    '    public static final String VERSION = "4.4";',
    '    public static final String VERSION = "4.5";',
    "support self-version 4.5")

for loc in ["", "-hi", "-es", "-pt", "-ar", "-ru", "-in"]:
    p = RES + "/values" + loc + "/strings.xml"
    if not os.path.exists(p):
        continue
    s = R(p)
    s2 = re.sub(r'(name="about_version">[^<]*?)4\.4(<)', r"\g<1>4.5\g<2>", s)
    if s2 == s:
        print("AB: (skip) about_version 4.4 not present in %s" % p)
    else:
        W(p, s2)
        print("AB: patched %s (about_version 4.5)" % p)

UI = J + "/Ui.java"
s = R(UI)
s2 = s.replace(" * v4.5 - the whole app look", " * v4.5 - the whole app look", 1)
if s2 != s:
    W(UI, s2)

print("AB: done")
