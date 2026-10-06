import os
ROOT="android"; RES=ROOT+"/app/src/main/res"
JAVA="android/app/src/main/java/online/mytempmail/app"
F={}

# ---------------------------------------------------------------- colors
# Static palette. Brand accent = Offex purple (#6D4DFF), used on the site and
# in the app's own original screens. Theme-dependent surfaces live in attrs
# (see attrs.xml / themes.xml) so the app can run light (default) or dark.
F["values/colors.xml"]="""<?xml version="1.0" encoding="utf-8"?>
<resources>
    <!-- brand -->
    <color name="offex_purple">#6D4DFF</color>
    <color name="offex_purple2">#8B6CFF</color>
    <color name="offex_purple_dark">#4B2FD6</color>
    <color name="offex_purple_soft">#EFEAFF</color>
    <color name="offex_cyan">#00C2FF</color>

    <!-- semantic accents -->
    <color name="offex_green">#1DBF73</color>
    <color name="offex_green_soft">#E3F7EE</color>
    <color name="offex_red">#E5484D</color>
    <color name="offex_red_soft">#FDE9EB</color>
    <color name="offex_red_soft_border">#F6CDD2</color>

    <!-- neutrals -->
    <color name="offex_white">#FFFFFF</color>
    <color name="offex_white_dim">#E7E3FF</color>
    <color name="offex_transparent">#00000000</color>

    <!-- concrete surface colours used by the two themes -->
    <color name="offex_bg_light">#F5F5FB</color>
    <color name="offex_bg_dark">#0E0F16</color>

    <!-- light-theme fallbacks (kept so any stray reference still resolves) -->
    <color name="offex_bg">#F5F5FB</color>
    <color name="offex_bg2">#FFFFFF</color>
    <color name="offex_card">#FFFFFF</color>
    <color name="offex_line">#E7E4F2</color>
    <color name="offex_text">#1B1730</color>
    <color name="offex_text_dim">#5C5875</color>
    <color name="offex_text_mute">#9A96AD</color>
    <color name="offex_glass_border">#EDEAF7</color>
    <color name="offex_nav">#FFFFFF</color>
</resources>
"""

# ---------------------------------------------------------------- attrs
F["values/attrs.xml"]="""<?xml version="1.0" encoding="utf-8"?>
<resources>
    <attr name="oxBg" format="color" />
    <attr name="oxCard" format="color" />
    <attr name="oxCardBorder" format="color" />
    <attr name="oxText" format="color" />
    <attr name="oxTextDim" format="color" />
    <attr name="oxTextMute" format="color" />
    <attr name="oxLine" format="color" />
    <attr name="oxNavBg" format="color" />
    <attr name="oxInputBg" format="color" />
    <attr name="oxInputBorder" format="color" />
    <attr name="oxHeaderStart" format="color" />
    <attr name="oxHeaderCenter" format="color" />
    <attr name="oxHeaderEnd" format="color" />
    <attr name="oxChipBg" format="color" />
    <attr name="oxChipBorder" format="color" />
    <attr name="oxChipText" format="color" />
    <attr name="oxOnHeader" format="color" />
    <attr name="oxOnHeaderDim" format="color" />
</resources>
"""

# ---------------------------------------------------------------- glyphs
F["values/glyphs.xml"]="""<?xml version="1.0" encoding="utf-8"?>
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
</resources>
"""

# ---------------------------------------------------------------- themes
F["values/themes.xml"]="""<?xml version="1.0" encoding="utf-8"?>
<resources xmlns:tools="http://schemas.android.com/tools">

    <!-- LIGHT is the default theme on first launch. -->
    <style name="Theme.Offex" parent="Theme.MaterialComponents.Light.NoActionBar">
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

        <item name="oxBg">@color/offex_bg_light</item>
        <item name="oxCard">#FFFFFF</item>
        <item name="oxCardBorder">#EDEAF7</item>
        <item name="oxText">#1B1730</item>
        <item name="oxTextDim">#5C5875</item>
        <item name="oxTextMute">#9A96AD</item>
        <item name="oxLine">#E7E4F2</item>
        <item name="oxNavBg">#FFFFFF</item>
        <item name="oxInputBg">#F3F1FB</item>
        <item name="oxInputBorder">#E3DFF2</item>
        <item name="oxHeaderStart">#FFFFFF</item>
        <item name="oxHeaderCenter">#F3F0FF</item>
        <item name="oxHeaderEnd">#F5F5FB</item>
        <item name="oxChipBg">#EFEAFF</item>
        <item name="oxChipBorder">#DED4FF</item>
        <item name="oxChipText">#4B2FD6</item>
        <item name="oxOnHeader">#1B1730</item>
        <item name="oxOnHeaderDim">#5C5875</item>
    </style>

    <!-- Dark stays available; selected from More > Theme. -->
    <style name="Theme.Offex.Dark" parent="Theme.MaterialComponents.NoActionBar">
        <item name="colorPrimary">@color/offex_purple</item>
        <item name="colorPrimaryVariant">@color/offex_purple_dark</item>
        <item name="colorOnPrimary">@color/offex_white</item>
        <item name="colorSecondary">@color/offex_purple2</item>
        <item name="colorOnSecondary">@color/offex_white</item>
        <item name="android:colorBackground">@color/offex_bg_dark</item>
        <item name="android:windowBackground">@color/offex_bg_dark</item>
        <item name="android:textColorPrimary">#F2F3F8</item>
        <item name="android:textColorSecondary">#A6ABC0</item>
        <item name="android:statusBarColor" tools:targetApi="l">@color/offex_bg_dark</item>
        <item name="android:navigationBarColor">@color/offex_bg_dark</item>
        <item name="android:windowLightStatusBar" tools:targetApi="m">false</item>
        <item name="android:windowLightNavigationBar" tools:targetApi="o">false</item>
        <item name="android:windowAnimationStyle">@style/Anim.Offex</item>

        <item name="oxBg">@color/offex_bg_dark</item>
        <item name="oxCard">#1A1C27</item>
        <item name="oxCardBorder">#2A2D3D</item>
        <item name="oxText">#F2F3F8</item>
        <item name="oxTextDim">#A6ABC0</item>
        <item name="oxTextMute">#6E7390</item>
        <item name="oxLine">#2A2D3D</item>
        <item name="oxNavBg">#14161F</item>
        <item name="oxInputBg">#1A1C27</item>
        <item name="oxInputBorder">#2A2D3D</item>
        <item name="oxHeaderStart">#241A55</item>
        <item name="oxHeaderCenter">#171233</item>
        <item name="oxHeaderEnd">#0E0F16</item>
        <item name="oxChipBg">#241E4D</item>
        <item name="oxChipBorder">#3A3178</item>
        <item name="oxChipText">#B9A8FF</item>
        <item name="oxOnHeader">#F2F3F8</item>
        <item name="oxOnHeaderDim">#A6ABC0</item>
    </style>

    <style name="Anim.Offex" parent="@android:style/Animation.Activity">
        <item name="android:activityOpenEnterAnimation">@anim/slide_up_fade</item>
        <item name="android:activityOpenExitAnimation">@anim/fade_out</item>
        <item name="android:activityCloseEnterAnimation">@anim/fade_in</item>
        <item name="android:activityCloseExitAnimation">@anim/fade_out</item>
    </style>
</resources>
"""

# ---------------------------------------------------------------- anim
F["anim/fade_in.xml"]="""<?xml version="1.0" encoding="utf-8"?>
<alpha xmlns:android="http://schemas.android.com/apk/res/android"
    android:fromAlpha="0.0" android:toAlpha="1.0" android:duration="200" />
"""
F["anim/fade_out.xml"]="""<?xml version="1.0" encoding="utf-8"?>
<alpha xmlns:android="http://schemas.android.com/apk/res/android"
    android:fromAlpha="1.0" android:toAlpha="0.0" android:duration="180" />
"""
F["anim/slide_up_fade.xml"]="""<?xml version="1.0" encoding="utf-8"?>
<set xmlns:android="http://schemas.android.com/apk/res/android"
    android:interpolator="@android:anim/decelerate_interpolator">
    <alpha android:fromAlpha="0.0" android:toAlpha="1.0" android:duration="240" />
    <translate android:fromYDelta="6%p" android:toYDelta="0" android:duration="240" />
</set>
"""

# ---------------------------------------------------------------- drawables
F["drawable/bg_header.xml"]="""<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="rectangle">
    <gradient android:type="linear" android:angle="270"
        android:startColor="?attr/oxHeaderStart"
        android:centerColor="?attr/oxHeaderCenter"
        android:endColor="?attr/oxHeaderEnd" />
    <corners android:bottomLeftRadius="30dp" android:bottomRightRadius="30dp" />
</shape>
"""

F["drawable/bg_onboard.xml"]="""<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="rectangle">
    <gradient android:type="linear" android:angle="270"
        android:startColor="?attr/oxHeaderStart"
        android:centerColor="?attr/oxHeaderCenter"
        android:endColor="?attr/oxHeaderEnd" />
</shape>
"""

F["drawable/bg_card.xml"]="""<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="rectangle">
    <solid android:color="?attr/oxCard" />
    <corners android:radius="20dp" />
    <stroke android:width="1dp" android:color="?attr/oxCardBorder" />
</shape>
"""

F["drawable/bg_card_hero.xml"]="""<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="rectangle">
    <solid android:color="?attr/oxCard" />
    <corners android:radius="24dp" />
    <stroke android:width="1dp" android:color="?attr/oxCardBorder" />
</shape>
"""

F["drawable/bg_input.xml"]="""<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="rectangle">
    <solid android:color="?attr/oxInputBg" />
    <corners android:radius="16dp" />
    <stroke android:width="1dp" android:color="?attr/oxInputBorder" />
</shape>
"""

F["drawable/bg_chip.xml"]="""<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="rectangle">
    <solid android:color="?attr/oxChipBg" />
    <corners android:radius="999dp" />
    <stroke android:width="1dp" android:color="?attr/oxChipBorder" />
</shape>
"""

F["drawable/bg_chip_green.xml"]="""<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="rectangle">
    <solid android:color="@color/offex_green_soft" />
    <corners android:radius="999dp" />
</shape>
"""

F["drawable/bg_chip_red.xml"]="""<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="rectangle">
    <solid android:color="@color/offex_red_soft" />
    <corners android:radius="999dp" />
</shape>
"""

F["drawable/bg_logo.xml"]="""<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="oval">
    <gradient android:startColor="#6D4DFF" android:centerColor="#7E5BFF" android:endColor="#9B6DFF" android:angle="315" />
</shape>
"""

F["drawable/bg_avatar.xml"]="""<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="oval">
    <gradient android:startColor="#6D4DFF" android:centerColor="#7E5BFF" android:endColor="#9B6DFF" android:angle="315" />
</shape>
"""

F["drawable/bg_btn_primary.xml"]="""<?xml version="1.0" encoding="utf-8"?>
<ripple xmlns:android="http://schemas.android.com/apk/res/android" android:color="#40FFFFFF">
    <item>
        <shape android:shape="rectangle">
            <gradient android:startColor="#6D4DFF" android:centerColor="#5F51FF" android:endColor="#8B6CFF" android:angle="0" />
            <corners android:radius="999dp" />
        </shape>
    </item>
</ripple>
"""

F["drawable/bg_btn_soft.xml"]="""<?xml version="1.0" encoding="utf-8"?>
<ripple xmlns:android="http://schemas.android.com/apk/res/android" android:color="#336D4DFF">
    <item>
        <shape android:shape="rectangle">
            <solid android:color="?attr/oxChipBg" />
            <corners android:radius="999dp" />
            <stroke android:width="1dp" android:color="?attr/oxChipBorder" />
        </shape>
    </item>
</ripple>
"""

F["drawable/bg_btn_ghost.xml"]="""<?xml version="1.0" encoding="utf-8"?>
<ripple xmlns:android="http://schemas.android.com/apk/res/android" android:color="#336D4DFF">
    <item>
        <shape android:shape="rectangle">
            <solid android:color="?attr/oxInputBg" />
            <corners android:radius="999dp" />
            <stroke android:width="1dp" android:color="?attr/oxInputBorder" />
        </shape>
    </item>
</ripple>
"""

F["drawable/bg_btn_danger.xml"]="""<?xml version="1.0" encoding="utf-8"?>
<ripple xmlns:android="http://schemas.android.com/apk/res/android" android:color="#33E5484D">
    <item>
        <shape android:shape="rectangle">
            <solid android:color="@color/offex_red_soft" />
            <corners android:radius="999dp" />
            <stroke android:width="1dp" android:color="@color/offex_red_soft_border" />
        </shape>
    </item>
</ripple>
"""

F["drawable/bg_indicator.xml"]="""<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="rectangle">
    <gradient android:startColor="#6D4DFF" android:endColor="#9B6DFF" android:angle="0" />
    <corners android:radius="999dp" />
</shape>
"""

F["drawable/bg_nav.xml"]="""<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="rectangle">
    <solid android:color="?attr/oxNavBg" />
    <corners android:topLeftRadius="26dp" android:topRightRadius="26dp" />
    <stroke android:width="1dp" android:color="?attr/oxCardBorder" />
</shape>
"""

F["drawable/bg_divider.xml"]="""<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="rectangle">
    <solid android:color="?attr/oxLine" />
    <corners android:radius="999dp" />
</shape>
"""

F["drawable/bg_premium.xml"]="""<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="rectangle">
    <gradient android:startColor="#6D4DFF" android:centerColor="#7E5BFF" android:endColor="#9B6DFF" android:angle="0" />
    <corners android:radius="22dp" />
</shape>
"""

# ---------------------------------------------------------------- main layout
# Email (top) -> Inbox (messages) -> Switch (saved addresses) -> More (nav).
F["layout/activity_main.xml"]="""<?xml version="1.0" encoding="utf-8"?>
<FrameLayout xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    android:layout_width="match_parent" android:layout_height="match_parent"
    android:background="?attr/oxBg">

    <ScrollView android:id="@+id/rootScroll"
        android:layout_width="match_parent" android:layout_height="match_parent"
        android:fillViewport="true" android:clipToPadding="false"
        android:scrollbars="none">

        <LinearLayout android:layout_width="match_parent" android:layout_height="wrap_content"
            android:orientation="vertical" android:paddingBottom="120dp">

            <!-- ============ EMAIL : hero header + address ============ -->
            <LinearLayout android:layout_width="match_parent" android:layout_height="wrap_content"
                android:background="@drawable/bg_header" android:orientation="vertical"
                android:paddingStart="22dp" android:paddingEnd="22dp"
                android:paddingTop="28dp" android:paddingBottom="30dp">

                <LinearLayout android:layout_width="match_parent" android:layout_height="wrap_content"
                    android:orientation="horizontal" android:gravity="center_vertical">
                    <TextView android:layout_width="46dp" android:layout_height="46dp"
                        android:background="@drawable/bg_logo" android:gravity="center"
                        android:text="@string/glyph_mail" android:textColor="@color/offex_white"
                        android:textSize="21sp" android:elevation="6dp" />
                    <LinearLayout android:layout_width="0dp" android:layout_height="wrap_content"
                        android:layout_weight="1" android:orientation="vertical" android:layout_marginStart="14dp">
                        <TextView android:layout_width="wrap_content" android:layout_height="wrap_content"
                            android:text="@string/app_name" android:textColor="?attr/oxOnHeader"
                            android:textSize="21sp" android:textStyle="bold"
                            android:fontFamily="sans-serif-black" android:letterSpacing="0.01" />
                        <TextView android:layout_width="wrap_content" android:layout_height="wrap_content"
                            android:layout_marginTop="1dp" android:text="@string/tagline"
                            android:textColor="?attr/oxOnHeaderDim" android:textSize="12sp" />
                    </LinearLayout>
                    <androidx.appcompat.widget.AppCompatButton android:id="@+id/settingsBtn"
                        android:layout_width="46dp" android:layout_height="46dp"
                        android:insetTop="0dp" android:insetBottom="0dp" android:padding="0dp"
                        android:background="@drawable/bg_btn_ghost" android:text="@string/glyph_gear"
                        android:textColor="?attr/oxText" android:textSize="18sp" />
                </LinearLayout>

                <TextView android:layout_width="wrap_content" android:layout_height="wrap_content"
                    android:layout_marginTop="22dp" android:text="@string/your_address"
                    android:textColor="@color/offex_purple" android:textSize="12sp"
                    android:textStyle="bold" android:letterSpacing="0.10" />

                <LinearLayout android:id="@+id/activeCard" android:layout_width="match_parent"
                    android:layout_height="wrap_content" android:layout_marginTop="10dp"
                    android:background="@drawable/bg_card_hero" android:elevation="10dp"
                    android:orientation="vertical" android:padding="18dp" android:visibility="gone">

                    <TextView android:id="@+id/addrText" android:layout_width="match_parent" android:layout_height="wrap_content"
                        android:textColor="?attr/oxText" android:textSize="19sp" android:textStyle="bold"
                        android:fontFamily="sans-serif-medium" android:textIsSelectable="true" />

                    <LinearLayout android:layout_width="match_parent" android:layout_height="wrap_content"
                        android:layout_marginTop="14dp" android:orientation="horizontal">
                        <androidx.appcompat.widget.AppCompatButton android:id="@+id/copyBtn"
                            android:layout_width="0dp" android:layout_height="46dp" android:layout_weight="1"
                            android:insetTop="0dp" android:insetBottom="0dp"
                            android:background="@drawable/bg_btn_primary" android:textColor="@color/offex_white"
                            android:textAllCaps="false" android:textSize="14sp" android:textStyle="bold"
                            android:text="@string/copy" />
                        <androidx.appcompat.widget.AppCompatButton android:id="@+id/refreshBtn"
                            android:layout_width="0dp" android:layout_height="46dp" android:layout_weight="1"
                            android:layout_marginStart="10dp" android:insetTop="0dp" android:insetBottom="0dp"
                            android:background="@drawable/bg_btn_ghost" android:textColor="?attr/oxText"
                            android:textAllCaps="false" android:textSize="14sp" android:text="@string/refresh" />
                        <androidx.appcompat.widget.AppCompatButton android:id="@+id/deleteBtn"
                            android:layout_width="0dp" android:layout_height="46dp" android:layout_weight="1"
                            android:layout_marginStart="10dp" android:insetTop="0dp" android:insetBottom="0dp"
                            android:background="@drawable/bg_btn_danger" android:textColor="@color/offex_red"
                            android:textAllCaps="false" android:textSize="14sp" android:text="@string/delete" />
                    </LinearLayout>

                    <TextView android:id="@+id/countdownText" android:layout_width="wrap_content"
                        android:layout_height="wrap_content" android:layout_marginTop="14dp"
                        android:background="@drawable/bg_chip" android:paddingStart="14dp" android:paddingEnd="14dp"
                        android:paddingTop="6dp" android:paddingBottom="6dp"
                        android:textColor="?attr/oxChipText" android:textSize="12sp" android:textStyle="bold" />
                </LinearLayout>

                <!-- create form -->
                <TextView android:layout_width="wrap_content" android:layout_height="wrap_content"
                    android:layout_marginTop="26dp" android:text="@string/create_new_email"
                    android:textColor="@color/offex_purple" android:textSize="12sp"
                    android:textStyle="bold" android:letterSpacing="0.10" />

                <EditText android:id="@+id/nameBox" android:layout_width="match_parent" android:layout_height="54dp"
                    android:layout_marginTop="10dp" android:background="@drawable/bg_input"
                    android:hint="@string/hint_name" android:inputType="text" android:maxLines="1"
                    android:paddingStart="18dp" android:paddingEnd="18dp"
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

            <!-- ============ INBOX ============ -->
            <TextView android:layout_width="wrap_content" android:layout_height="wrap_content"
                android:layout_marginStart="20dp" android:layout_marginTop="26dp" android:text="@string/inbox_title"
                android:textColor="?attr/oxText" android:textSize="18sp" android:textStyle="bold"
                android:fontFamily="sans-serif-medium" />

            <TextView android:id="@+id/inboxAddr" android:layout_width="match_parent" android:layout_height="wrap_content"
                android:layout_marginStart="20dp" android:layout_marginEnd="20dp" android:layout_marginTop="3dp"
                android:textColor="?attr/oxTextDim" android:textSize="13sp" />

            <TextView android:id="@+id/emptyText" android:layout_width="match_parent" android:layout_height="wrap_content"
                android:layout_marginStart="20dp" android:layout_marginEnd="20dp" android:layout_marginTop="12dp"
                android:background="@drawable/bg_card" android:padding="20dp"
                android:text="@string/no_messages" android:textColor="?attr/oxTextDim"
                android:textSize="14sp" android:lineSpacingExtra="4dp" />

            <androidx.recyclerview.widget.RecyclerView android:id="@+id/msgList"
                android:layout_width="match_parent" android:layout_height="wrap_content"
                android:layout_marginStart="16dp" android:layout_marginEnd="16dp"
                android:layout_marginTop="6dp" android:nestedScrollingEnabled="false" />

            <!-- ============ SWITCH EMAIL ============ -->
            <TextView android:layout_width="wrap_content" android:layout_height="wrap_content"
                android:layout_marginStart="20dp" android:layout_marginTop="26dp" android:text="@string/switch_title"
                android:textColor="?attr/oxText" android:textSize="18sp" android:textStyle="bold"
                android:fontFamily="sans-serif-medium" />

            <TextView android:layout_width="match_parent" android:layout_height="wrap_content"
                android:layout_marginStart="20dp" android:layout_marginEnd="20dp" android:layout_marginTop="3dp"
                android:text="@string/choose_email" android:textColor="?attr/oxTextDim" android:textSize="13sp" />

            <TextView android:id="@+id/historyEmpty" android:layout_width="match_parent" android:layout_height="wrap_content"
                android:layout_marginStart="20dp" android:layout_marginEnd="20dp" android:layout_marginTop="12dp"
                android:background="@drawable/bg_card" android:padding="18dp"
                android:text="@string/history_empty" android:textColor="?attr/oxTextDim" android:textSize="14sp" />

            <LinearLayout android:id="@+id/historyBox" android:layout_width="match_parent"
                android:layout_height="wrap_content" android:layout_marginStart="16dp" android:layout_marginEnd="16dp"
                android:orientation="vertical" />
        </LinearLayout>
    </ScrollView>

    <!-- ============ BOTTOM NAV ============ -->
    <LinearLayout android:id="@+id/navBar" android:layout_width="match_parent"
        android:layout_height="wrap_content" android:layout_gravity="bottom"
        android:background="@drawable/bg_nav" android:orientation="horizontal"
        android:elevation="18dp" android:paddingStart="8dp" android:paddingEnd="8dp"
        android:paddingTop="8dp" android:paddingBottom="12dp">

        <LinearLayout android:id="@+id/navEmail" android:layout_width="0dp" android:layout_height="wrap_content"
            android:layout_weight="1" android:orientation="vertical" android:gravity="center"
            android:clickable="true" android:focusable="true"
            android:background="?android:attr/selectableItemBackground"
            android:paddingTop="8dp" android:paddingBottom="6dp">
            <View android:id="@+id/navIndEmail" android:layout_width="24dp" android:layout_height="3dp"
                android:background="@drawable/bg_indicator" android:visibility="invisible" />
            <TextView android:id="@+id/navIconEmail" android:layout_width="wrap_content" android:layout_height="wrap_content"
                android:layout_marginTop="8dp" android:text="@string/glyph_mail" android:textSize="17sp"
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
            <View android:id="@+id/navIndInbox" android:layout_width="24dp" android:layout_height="3dp"
                android:background="@drawable/bg_indicator" android:visibility="invisible" />
            <TextView android:id="@+id/navIconInbox" android:layout_width="wrap_content" android:layout_height="wrap_content"
                android:layout_marginTop="8dp" android:text="@string/glyph_inbox" android:textSize="17sp"
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
            <View android:id="@+id/navIndSwitch" android:layout_width="24dp" android:layout_height="3dp"
                android:background="@drawable/bg_indicator" android:visibility="invisible" />
            <TextView android:id="@+id/navIconSwitch" android:layout_width="wrap_content" android:layout_height="wrap_content"
                android:layout_marginTop="8dp" android:text="@string/glyph_switch" android:textSize="17sp"
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
            <View android:id="@+id/navIndMore" android:layout_width="24dp" android:layout_height="3dp"
                android:background="@drawable/bg_indicator" android:visibility="invisible" />
            <TextView android:id="@+id/navIconMore" android:layout_width="wrap_content" android:layout_height="wrap_content"
                android:layout_marginTop="8dp" android:text="@string/glyph_more" android:textSize="17sp"
                android:textColor="?attr/oxTextMute" />
            <TextView android:layout_width="wrap_content" android:layout_height="wrap_content"
                android:layout_marginTop="4dp" android:text="@string/nav_more" android:textSize="10sp"
                android:textColor="?attr/oxTextMute" />
        </LinearLayout>
    </LinearLayout>
</FrameLayout>
"""

# ---------------------------------------------------------------- message item
F["layout/item_message.xml"]="""<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent" android:layout_height="wrap_content"
    android:layout_marginTop="10dp" android:background="@drawable/bg_card"
    android:elevation="2dp" android:orientation="horizontal" android:padding="16dp">

    <TextView android:layout_width="46dp" android:layout_height="46dp"
        android:background="@drawable/bg_avatar" android:gravity="center"
        android:text="@string/glyph_mail" android:textColor="@color/offex_white" android:textSize="18sp" />

    <LinearLayout android:layout_width="0dp" android:layout_height="wrap_content"
        android:layout_weight="1" android:layout_marginStart="14dp" android:orientation="vertical">

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
                android:background="@drawable/bg_chip" android:paddingStart="11dp" android:paddingEnd="11dp"
                android:paddingTop="4dp" android:paddingBottom="4dp"
                android:textColor="?attr/oxChipText" android:textSize="10sp" android:textStyle="bold"
                android:letterSpacing="0.06" android:text="MAIL" />
            <TextView android:id="@+id/mOtp" android:layout_width="wrap_content" android:layout_height="wrap_content"
                android:layout_marginStart="8dp" android:background="@drawable/bg_chip_green"
                android:paddingStart="11dp" android:paddingEnd="11dp" android:paddingTop="4dp" android:paddingBottom="4dp"
                android:textColor="@color/offex_green" android:textSize="12sp" android:textStyle="bold"
                android:visibility="gone" />
        </LinearLayout>
    </LinearLayout>
</LinearLayout>
"""

# ---------------------------------------------------------------- onboarding
F["layout/activity_onboarding.xml"]="""<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent" android:layout_height="match_parent"
    android:orientation="vertical" android:background="@drawable/bg_onboard"
    android:gravity="center" android:padding="32dp">

    <TextView android:layout_width="124dp" android:layout_height="124dp"
        android:background="@drawable/bg_logo" android:gravity="center" android:elevation="14dp"
        android:text="@string/glyph_mail" android:textColor="@color/offex_white" android:textSize="54sp" />

    <TextView android:id="@+id/obTitle" android:layout_width="match_parent"
        android:layout_height="wrap_content" android:layout_marginTop="34dp" android:gravity="center"
        android:textColor="?attr/oxOnHeader" android:textSize="26sp" android:textStyle="bold"
        android:fontFamily="sans-serif-black" />

    <TextView android:id="@+id/obBody" android:layout_width="match_parent"
        android:layout_height="wrap_content" android:layout_marginTop="16dp" android:gravity="center"
        android:textColor="?attr/oxOnHeaderDim" android:textSize="15sp" android:lineSpacingExtra="6dp" />

    <TextView android:id="@+id/obDots" android:layout_width="wrap_content"
        android:layout_height="wrap_content" android:layout_marginTop="30dp"
        android:textColor="@color/offex_purple" android:textSize="15sp" />

    <androidx.appcompat.widget.AppCompatButton android:id="@+id/obNext"
        android:layout_width="match_parent" android:layout_height="56dp"
        android:layout_marginTop="30dp" android:insetTop="0dp" android:insetBottom="0dp"
        android:background="@drawable/bg_btn_primary" android:textColor="@color/offex_white"
        android:textAllCaps="false" android:textSize="16sp" android:textStyle="bold"
        android:fontFamily="sans-serif-medium" />

    <androidx.appcompat.widget.AppCompatButton android:id="@+id/obSkip"
        android:layout_width="wrap_content" android:layout_height="wrap_content"
        android:layout_marginTop="8dp" android:insetTop="0dp" android:insetBottom="0dp"
        android:background="@color/offex_transparent" android:textColor="?attr/oxTextMute"
        android:textAllCaps="false" android:text="@string/ob_skip" />
</LinearLayout>
"""

# ---------------------------------------------------------------- reader
F["layout/activity_reader.xml"]="""<?xml version="1.0" encoding="utf-8"?>
<ScrollView xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent" android:layout_height="match_parent"
    android:background="?attr/oxBg" android:scrollbars="none">
    <LinearLayout android:layout_width="match_parent" android:layout_height="wrap_content"
        android:orientation="vertical" android:padding="18dp">

        <LinearLayout android:layout_width="match_parent" android:layout_height="wrap_content"
            android:orientation="horizontal" android:gravity="center_vertical">
            <TextView android:id="@+id/readerBack" android:layout_width="42dp" android:layout_height="42dp"
                android:background="@drawable/bg_btn_ghost" android:gravity="center"
                android:text="@string/glyph_back" android:textColor="?attr/oxText" android:textSize="18sp"
                android:clickable="true" android:focusable="true" />
            <TextView android:layout_width="wrap_content" android:layout_height="wrap_content"
                android:layout_marginStart="12dp" android:text="@string/message_label"
                android:textColor="?attr/oxTextDim" android:textSize="11sp" android:textStyle="bold"
                android:letterSpacing="0.14" />
        </LinearLayout>

        <LinearLayout android:layout_width="match_parent" android:layout_height="wrap_content"
            android:layout_marginTop="16dp" android:background="@drawable/bg_card" android:elevation="3dp"
            android:orientation="vertical" android:padding="20dp">

            <TextView android:id="@+id/rSubject" android:layout_width="match_parent" android:layout_height="wrap_content"
                android:textColor="?attr/oxText" android:textSize="20sp" android:textStyle="bold"
                android:fontFamily="sans-serif-medium" />

            <LinearLayout android:layout_width="match_parent" android:layout_height="wrap_content"
                android:layout_marginTop="16dp" android:orientation="horizontal" android:gravity="center_vertical">
                <TextView android:id="@+id/rAvatar" android:layout_width="40dp" android:layout_height="40dp"
                    android:background="@drawable/bg_avatar" android:gravity="center"
                    android:textColor="@color/offex_white" android:textSize="16sp" android:textStyle="bold" />
                <TextView android:id="@+id/rFrom" android:layout_width="0dp" android:layout_height="wrap_content"
                    android:layout_weight="1" android:layout_marginStart="12dp" android:maxLines="1"
                    android:ellipsize="end" android:textColor="?attr/oxText" android:textSize="14sp"
                    android:textStyle="bold" />
            </LinearLayout>
        </LinearLayout>

        <LinearLayout android:layout_width="match_parent" android:layout_height="wrap_content"
            android:layout_marginTop="14dp" android:background="@drawable/bg_card" android:elevation="3dp"
            android:orientation="vertical" android:padding="20dp">
            <TextView android:id="@+id/rBody" android:layout_width="match_parent" android:layout_height="wrap_content"
                android:textColor="?attr/oxText" android:textSize="15sp" android:lineSpacingExtra="6dp" />
        </LinearLayout>
    </LinearLayout>
</ScrollView>
"""

# ---------------------------------------------------------------- admin (overwritten by gn_h)
F["layout/activity_admin.xml"]="""<?xml version="1.0" encoding="utf-8"?>
<ScrollView xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent" android:layout_height="match_parent"
    android:background="?attr/oxBg">
    <LinearLayout android:layout_width="match_parent" android:layout_height="wrap_content"
        android:orientation="vertical" android:padding="18dp">
        <TextView android:layout_width="wrap_content" android:layout_height="wrap_content"
            android:text="@string/admin" android:textColor="?attr/oxText" android:textSize="22sp" android:textStyle="bold" />
        <EditText android:id="@+id/codeBox" android:layout_width="match_parent" android:layout_height="54dp"
            android:layout_marginTop="16dp" android:background="@drawable/bg_input" android:hint="@string/admin_hint"
            android:inputType="textPassword" android:paddingStart="18dp" android:paddingEnd="18dp"
            android:textColorHint="?attr/oxTextMute" android:textColor="?attr/oxText" />
        <androidx.appcompat.widget.AppCompatButton android:id="@+id/unlockBtn"
            android:layout_width="match_parent" android:layout_height="54dp"
            android:layout_marginTop="12dp" android:insetTop="0dp" android:insetBottom="0dp"
            android:background="@drawable/bg_btn_primary" android:textColor="@color/offex_white"
            android:textAllCaps="false" android:textSize="16sp" android:text="@string/unlock" />
        <LinearLayout android:id="@+id/panel" android:layout_width="match_parent" android:layout_height="wrap_content"
            android:layout_marginTop="18dp" android:background="@drawable/bg_card" android:elevation="3dp"
            android:orientation="vertical" android:padding="18dp" android:visibility="gone">
            <Switch android:id="@+id/notifySwitch" android:layout_width="match_parent" android:layout_height="wrap_content"
                android:text="@string/notif_on" android:textColor="?attr/oxText" />
            <TextView android:id="@+id/versionText" android:layout_width="match_parent" android:layout_height="wrap_content"
                android:layout_marginTop="14dp" android:textColor="?attr/oxTextDim" android:textSize="13sp" />
        </LinearLayout>
    </LinearLayout>
</ScrollView>
"""

# ---------------------------------------------------------------- skin helper
F["__skin__"]="""package online.mytempmail.app;
import android.app.Activity;
public class Skin {
    public static void apply(Activity a){
        a.setTheme(Prefs.isDark() ? R.style.Theme_Offex_Dark : R.style.Theme_Offex);
    }
}
"""

for rel,c in F.items():
    if rel=="__skin__":
        os.makedirs(JAVA,exist_ok=True)
        open(os.path.join(JAVA,"Skin.java"),"w",encoding="utf-8").write(c)
        continue
    p=os.path.join(RES,rel); os.makedirs(os.path.dirname(p),exist_ok=True)
    open(p,"w",encoding="utf-8").write(c)
print("E light premium:",len(F))
