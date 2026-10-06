import os
ROOT="android"; RES=ROOT+"/app/src/main/res"
F={}

# ---------------------------------------------------------------- colors
F["values/colors.xml"]="""<?xml version="1.0" encoding="utf-8"?>
<resources>
    <color name="offex_bg">#0B0B12</color>
    <color name="offex_bg2">#12121C</color>
    <color name="offex_card">#1AFFFFFF</color>
    <color name="offex_purple">#6D4DFF</color>
    <color name="offex_purple2">#8B6CFF</color>
    <color name="offex_cyan">#00E5FF</color>
    <color name="offex_purple_dark">#4B2FD6</color>
    <color name="offex_purple_soft">#221C4D</color>
    <color name="offex_line">#22243A</color>
    <color name="offex_text">#F4F5FF</color>
    <color name="offex_text_dim">#9AA0C4</color>
    <color name="offex_text_mute">#6E7396</color>
    <color name="offex_green">#2BD98A</color>
    <color name="offex_green_soft">#0F3324</color>
    <color name="offex_red">#FF5C6C</color>
    <color name="offex_red_soft">#3A1620</color>
    <color name="offex_white">#FFFFFF</color>
    <color name="offex_white_dim">#C9C6FF</color>
    <color name="offex_glass_border">#26FFFFFF</color>
    <color name="offex_nav">#E60D0D16</color>
    <color name="offex_transparent">#00000000</color>
</resources>
"""

# ---------------------------------------------------------------- glyphs
F["values/glyphs.xml"]="""<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="glyph_mail">\u2709</string>
    <string name="glyph_gear">\u2699</string>
    <string name="glyph_inbox">\u2261</string>
    <string name="glyph_switch">\u21C4</string>
    <string name="glyph_more">\u22EF</string>
    <string name="glyph_close">\u2715</string>
</resources>
"""

# ---------------------------------------------------------------- theme
F["values/themes.xml"]="""<?xml version="1.0" encoding="utf-8"?>
<resources xmlns:tools="http://schemas.android.com/tools">
    <style name="Theme.Offex" parent="Theme.MaterialComponents.NoActionBar">
        <item name="colorPrimary">@color/offex_purple</item>
        <item name="colorPrimaryVariant">@color/offex_purple_dark</item>
        <item name="colorOnPrimary">@color/offex_white</item>
        <item name="colorSecondary">@color/offex_cyan</item>
        <item name="colorOnSecondary">@color/offex_bg</item>
        <item name="android:colorBackground">@color/offex_bg</item>
        <item name="android:windowBackground">@color/offex_bg</item>
        <item name="android:textColorPrimary">@color/offex_text</item>
        <item name="android:textColorSecondary">@color/offex_text_dim</item>
        <item name="android:statusBarColor" tools:targetApi="l">@color/offex_bg</item>
        <item name="android:navigationBarColor">@color/offex_bg</item>
        <item name="android:windowLightStatusBar" tools:targetApi="m">false</item>
        <item name="android:windowLightNavigationBar" tools:targetApi="o">false</item>
        <item name="android:windowAnimationStyle">@style/Anim.Futuristic</item>
    </style>

    <style name="Anim.Futuristic" parent="@android:style/Animation.Activity">
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
    <gradient android:type="radial" android:gradientRadius="280dp"
        android:centerX="0.22" android:centerY="0.12"
        android:startColor="#3B2A86" android:centerColor="#181242" android:endColor="#0B0B12" />
    <corners android:bottomLeftRadius="30dp" android:bottomRightRadius="30dp" />
</shape>
"""

F["drawable/bg_card.xml"]="""<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="rectangle">
    <solid android:color="#14FFFFFF" />
    <corners android:radius="22dp" />
    <stroke android:width="1dp" android:color="#26FFFFFF" />
</shape>
"""

F["drawable/bg_input.xml"]="""<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="rectangle">
    <solid android:color="#1A1B2E" />
    <corners android:radius="16dp" />
    <stroke android:width="1dp" android:color="#2A2D45" />
</shape>
"""

F["drawable/bg_chip.xml"]="""<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="rectangle">
    <solid android:color="#221C4D" />
    <corners android:radius="999dp" />
    <stroke android:width="1dp" android:color="#3A2F7A" />
</shape>
"""

F["drawable/bg_chip_green.xml"]="""<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="rectangle">
    <solid android:color="#0F3324" />
    <corners android:radius="999dp" />
</shape>
"""

F["drawable/bg_chip_red.xml"]="""<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="rectangle">
    <solid android:color="#3A1620" />
    <corners android:radius="999dp" />
</shape>
"""

F["drawable/bg_logo.xml"]="""<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="oval">
    <gradient android:startColor="#6D4DFF" android:centerColor="#7A6BFF" android:endColor="#00E5FF" android:angle="315" />
</shape>
"""

F["drawable/bg_avatar.xml"]="""<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="oval">
    <gradient android:startColor="#6D4DFF" android:centerColor="#7A6BFF" android:endColor="#00E5FF" android:angle="315" />
</shape>
"""

F["drawable/bg_btn_primary.xml"]="""<?xml version="1.0" encoding="utf-8"?>
<ripple xmlns:android="http://schemas.android.com/apk/res/android" android:color="#40FFFFFF">
    <item>
        <shape android:shape="rectangle">
            <gradient android:startColor="#6D4DFF" android:centerColor="#5F6BFF" android:endColor="#00E5FF" android:angle="0" />
            <corners android:radius="999dp" />
        </shape>
    </item>
</ripple>
"""

F["drawable/bg_btn_soft.xml"]="""<?xml version="1.0" encoding="utf-8"?>
<ripple xmlns:android="http://schemas.android.com/apk/res/android" android:color="#33FFFFFF">
    <item>
        <shape android:shape="rectangle">
            <solid android:color="#221C4D" />
            <corners android:radius="999dp" />
            <stroke android:width="1dp" android:color="#3A2F7A" />
        </shape>
    </item>
</ripple>
"""

F["drawable/bg_btn_ghost.xml"]="""<?xml version="1.0" encoding="utf-8"?>
<ripple xmlns:android="http://schemas.android.com/apk/res/android" android:color="#33FFFFFF">
    <item>
        <shape android:shape="rectangle">
            <solid android:color="#1A1B2E" />
            <corners android:radius="999dp" />
            <stroke android:width="1dp" android:color="#2A2D45" />
        </shape>
    </item>
</ripple>
"""

F["drawable/bg_btn_danger.xml"]="""<?xml version="1.0" encoding="utf-8"?>
<ripple xmlns:android="http://schemas.android.com/apk/res/android" android:color="#33FFFFFF">
    <item>
        <shape android:shape="rectangle">
            <solid android:color="#3A1620" />
            <corners android:radius="999dp" />
            <stroke android:width="1dp" android:color="#5A2430" />
        </shape>
    </item>
</ripple>
"""

F["drawable/bg_indicator.xml"]="""<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="rectangle">
    <gradient android:startColor="#6D4DFF" android:endColor="#00E5FF" android:angle="0" />
    <corners android:radius="999dp" />
</shape>
"""

F["drawable/bg_nav.xml"]="""<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="rectangle">
    <solid android:color="#E60D0D16" />
    <corners android:topLeftRadius="26dp" android:topRightRadius="26dp" />
    <stroke android:width="1dp" android:color="#26FFFFFF" />
</shape>
"""

F["drawable/bg_divider.xml"]="""<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="rectangle">
    <solid android:color="#22243A" />
    <corners android:radius="999dp" />
</shape>
"""

# ---------------------------------------------------------------- main layout
F["layout/activity_main.xml"]="""<?xml version="1.0" encoding="utf-8"?>
<FrameLayout xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    android:layout_width="match_parent" android:layout_height="match_parent"
    android:background="@color/offex_bg">

    <ScrollView android:id="@+id/rootScroll"
        android:layout_width="match_parent" android:layout_height="match_parent"
        android:fillViewport="true" android:clipToPadding="false"
        android:scrollbars="none">

        <LinearLayout android:layout_width="match_parent" android:layout_height="wrap_content"
            android:orientation="vertical" android:paddingBottom="112dp">

            <LinearLayout android:layout_width="match_parent" android:layout_height="wrap_content"
                android:background="@drawable/bg_header" android:orientation="vertical"
                android:paddingStart="22dp" android:paddingEnd="22dp"
                android:paddingTop="26dp" android:paddingBottom="34dp">

                <LinearLayout android:layout_width="match_parent" android:layout_height="wrap_content"
                    android:orientation="horizontal" android:gravity="center_vertical">
                    <TextView android:layout_width="46dp" android:layout_height="46dp"
                        android:background="@drawable/bg_logo" android:gravity="center"
                        android:text="@string/glyph_mail" android:textColor="@color/offex_white"
                        android:textSize="21sp" android:elevation="6dp" />
                    <LinearLayout android:layout_width="0dp" android:layout_height="wrap_content"
                        android:layout_weight="1" android:orientation="vertical" android:layout_marginStart="14dp">
                        <TextView android:layout_width="wrap_content" android:layout_height="wrap_content"
                            android:text="@string/app_name" android:textColor="@color/offex_white"
                            android:textSize="21sp" android:textStyle="bold"
                            android:fontFamily="sans-serif-black" android:letterSpacing="0.01" />
                        <TextView android:layout_width="wrap_content" android:layout_height="wrap_content"
                            android:layout_marginTop="1dp" android:text="@string/tagline"
                            android:textColor="@color/offex_white_dim" android:textSize="12sp" />
                    </LinearLayout>
                    <androidx.appcompat.widget.AppCompatButton android:id="@+id/settingsBtn"
                        android:layout_width="46dp" android:layout_height="46dp"
                        android:insetTop="0dp" android:insetBottom="0dp" android:padding="0dp"
                        android:background="@drawable/bg_btn_ghost" android:text="@string/glyph_gear"
                        android:textColor="@color/offex_text" android:textSize="18sp" />
                </LinearLayout>

                <TextView android:layout_width="wrap_content" android:layout_height="wrap_content"
                    android:layout_marginTop="26dp" android:text="@string/new_inbox"
                    android:textColor="@color/offex_white_dim" android:textSize="12sp"
                    android:textStyle="bold" android:letterSpacing="0.12" />

                <EditText android:id="@+id/nameBox" android:layout_width="match_parent" android:layout_height="54dp"
                    android:layout_marginTop="10dp" android:background="@drawable/bg_input"
                    android:hint="@string/hint_name" android:inputType="text" android:maxLines="1"
                    android:paddingStart="18dp" android:paddingEnd="18dp"
                    android:textColorHint="@color/offex_text_mute" android:textColor="@color/offex_text"
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

            <LinearLayout android:id="@+id/activeCard" android:layout_width="match_parent"
                android:layout_height="wrap_content" android:layout_marginStart="16dp" android:layout_marginEnd="16dp"
                android:layout_marginTop="-20dp" android:background="@drawable/bg_card" android:elevation="12dp"
                android:orientation="vertical" android:padding="20dp" android:visibility="gone">

                <TextView android:layout_width="wrap_content" android:layout_height="wrap_content"
                    android:text="@string/your_address" android:textColor="@color/offex_text_dim"
                    android:textSize="11sp" android:textStyle="bold" android:letterSpacing="0.1" />

                <TextView android:id="@+id/addrText" android:layout_width="match_parent" android:layout_height="wrap_content"
                    android:layout_marginTop="8dp" android:textColor="@color/offex_text"
                    android:textSize="19sp" android:textStyle="bold" android:fontFamily="sans-serif-medium"
                    android:textIsSelectable="true" />

                <TextView android:id="@+id/countdownText" android:layout_width="wrap_content"
                    android:layout_height="wrap_content" android:layout_marginTop="12dp"
                    android:background="@drawable/bg_chip" android:paddingStart="14dp" android:paddingEnd="14dp"
                    android:paddingTop="6dp" android:paddingBottom="6dp"
                    android:textColor="@color/offex_purple2" android:textSize="12sp" android:textStyle="bold" />

                <LinearLayout android:layout_width="match_parent" android:layout_height="wrap_content"
                    android:layout_marginTop="16dp" android:orientation="horizontal">
                    <androidx.appcompat.widget.AppCompatButton android:id="@+id/copyBtn"
                        android:layout_width="0dp" android:layout_height="48dp" android:layout_weight="1"
                        android:insetTop="0dp" android:insetBottom="0dp"
                        android:background="@drawable/bg_btn_primary" android:textColor="@color/offex_white"
                        android:textAllCaps="false" android:textSize="14sp" android:textStyle="bold"
                        android:text="@string/copy" />
                    <androidx.appcompat.widget.AppCompatButton android:id="@+id/refreshBtn"
                        android:layout_width="0dp" android:layout_height="48dp" android:layout_weight="1"
                        android:layout_marginStart="10dp" android:insetTop="0dp" android:insetBottom="0dp"
                        android:background="@drawable/bg_btn_ghost" android:textColor="@color/offex_text"
                        android:textAllCaps="false" android:textSize="14sp" android:text="@string/refresh" />
                    <androidx.appcompat.widget.AppCompatButton android:id="@+id/deleteBtn"
                        android:layout_width="0dp" android:layout_height="48dp" android:layout_weight="1"
                        android:layout_marginStart="10dp" android:insetTop="0dp" android:insetBottom="0dp"
                        android:background="@drawable/bg_btn_danger" android:textColor="@color/offex_red"
                        android:textAllCaps="false" android:textSize="14sp" android:text="@string/delete" />
                </LinearLayout>
            </LinearLayout>

        <TextView android:layout_width="wrap_content" android:layout_height="wrap_content"
            android:layout_marginStart="20dp" android:layout_marginTop="24dp" android:text="@string/messages"
            android:textColor="@color/offex_text" android:textSize="18sp" android:textStyle="bold"
            android:fontFamily="sans-serif-medium" />

            <TextView android:id="@+id/emptyText" android:layout_width="match_parent" android:layout_height="wrap_content"
                android:layout_marginStart="20dp" android:layout_marginEnd="20dp" android:layout_marginTop="12dp"
                android:background="@drawable/bg_card" android:padding="20dp"
                android:text="@string/no_messages" android:textColor="@color/offex_text_dim"
                android:textSize="14sp" android:lineSpacingExtra="4dp" />

            <androidx.recyclerview.widget.RecyclerView android:id="@+id/msgList"
                android:layout_width="match_parent" android:layout_height="wrap_content"
                android:layout_marginStart="16dp" android:layout_marginEnd="16dp"
                android:layout_marginTop="10dp" android:nestedScrollingEnabled="false" />
        </LinearLayout>
    </ScrollView>

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
                android:textColor="@color/offex_text_mute" />
            <TextView android:layout_width="wrap_content" android:layout_height="wrap_content"
                android:layout_marginTop="4dp" android:text="Email" android:textSize="10sp"
                android:textColor="@color/offex_text_mute" />
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
                android:textColor="@color/offex_text_mute" />
            <TextView android:layout_width="wrap_content" android:layout_height="wrap_content"
                android:layout_marginTop="4dp" android:text="Inbox" android:textSize="10sp"
                android:textColor="@color/offex_text_mute" />
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
                android:textColor="@color/offex_text_mute" />
            <TextView android:layout_width="wrap_content" android:layout_height="wrap_content"
                android:layout_marginTop="4dp" android:text="Switch" android:textSize="10sp"
                android:textColor="@color/offex_text_mute" />
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
                android:textColor="@color/offex_text_mute" />
            <TextView android:layout_width="wrap_content" android:layout_height="wrap_content"
                android:layout_marginTop="4dp" android:text="More" android:textSize="10sp"
                android:textColor="@color/offex_text_mute" />
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
                android:textColor="@color/offex_text" android:textSize="14sp" android:textStyle="bold" />
            <TextView android:id="@+id/mTime" android:layout_width="wrap_content" android:layout_height="wrap_content"
                android:layout_marginStart="8dp" android:textColor="@color/offex_text_mute" android:textSize="11sp" />
        </LinearLayout>

        <TextView android:id="@+id/mSubject" android:layout_width="match_parent" android:layout_height="wrap_content"
            android:layout_marginTop="4dp" android:maxLines="2" android:ellipsize="end"
            android:textColor="@color/offex_text_dim" android:textSize="13sp" />

        <LinearLayout android:layout_width="match_parent" android:layout_height="wrap_content"
            android:layout_marginTop="9dp" android:orientation="horizontal" android:gravity="center_vertical">
            <TextView android:id="@+id/mService" android:layout_width="wrap_content" android:layout_height="wrap_content"
                android:background="@drawable/bg_chip" android:paddingStart="11dp" android:paddingEnd="11dp"
                android:paddingTop="4dp" android:paddingBottom="4dp"
                android:textColor="@color/offex_purple2" android:textSize="10sp" android:textStyle="bold"
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
    android:orientation="vertical" android:background="@drawable/bg_header"
    android:gravity="center" android:padding="32dp">

    <TextView android:layout_width="124dp" android:layout_height="124dp"
        android:background="@drawable/bg_logo" android:gravity="center" android:elevation="14dp"
        android:text="@string/glyph_mail" android:textColor="@color/offex_white" android:textSize="54sp" />

    <TextView android:id="@+id/obTitle" android:layout_width="match_parent"
        android:layout_height="wrap_content" android:layout_marginTop="34dp" android:gravity="center"
        android:textColor="@color/offex_text" android:textSize="26sp" android:textStyle="bold"
        android:fontFamily="sans-serif-black" />

    <TextView android:id="@+id/obBody" android:layout_width="match_parent"
        android:layout_height="wrap_content" android:layout_marginTop="16dp" android:gravity="center"
        android:textColor="@color/offex_text_dim" android:textSize="15sp" android:lineSpacingExtra="6dp" />

    <TextView android:id="@+id/obDots" android:layout_width="wrap_content"
        android:layout_height="wrap_content" android:layout_marginTop="30dp"
        android:textColor="@color/offex_purple2" android:textSize="15sp" />

    <androidx.appcompat.widget.AppCompatButton android:id="@+id/obNext"
        android:layout_width="match_parent" android:layout_height="56dp"
        android:layout_marginTop="30dp" android:insetTop="0dp" android:insetBottom="0dp"
        android:background="@drawable/bg_btn_primary" android:textColor="@color/offex_white"
        android:textAllCaps="false" android:textSize="16sp" android:textStyle="bold"
        android:fontFamily="sans-serif-medium" />

    <androidx.appcompat.widget.AppCompatButton android:id="@+id/obSkip"
        android:layout_width="wrap_content" android:layout_height="wrap_content"
        android:layout_marginTop="8dp" android:insetTop="0dp" android:insetBottom="0dp"
        android:background="@color/offex_transparent" android:textColor="@color/offex_text_mute"
        android:textAllCaps="false" android:text="@string/ob_skip" />
</LinearLayout>
"""

# ---------------------------------------------------------------- reader
F["layout/activity_reader.xml"]="""<?xml version="1.0" encoding="utf-8"?>
<ScrollView xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent" android:layout_height="match_parent"
    android:background="@color/offex_bg" android:scrollbars="none">
    <LinearLayout android:layout_width="match_parent" android:layout_height="wrap_content"
        android:orientation="vertical" android:padding="18dp">

        <LinearLayout android:layout_width="match_parent" android:layout_height="wrap_content"
            android:background="@drawable/bg_header" android:orientation="vertical"
            android:paddingStart="20dp" android:paddingEnd="20dp"
            android:paddingTop="22dp" android:paddingBottom="22dp">

            <TextView android:layout_width="wrap_content" android:layout_height="wrap_content"
                android:text="MESSAGE" android:textColor="@color/offex_white_dim" android:textSize="11sp"
                android:textStyle="bold" android:letterSpacing="0.14" />

            <TextView android:id="@+id/rSubject" android:layout_width="match_parent" android:layout_height="wrap_content"
                android:layout_marginTop="8dp" android:textColor="@color/offex_white"
                android:textSize="20sp" android:textStyle="bold" android:fontFamily="sans-serif-medium" />

            <TextView android:id="@+id/rFrom" android:layout_width="wrap_content" android:layout_height="wrap_content"
                android:layout_marginTop="12dp" android:background="@drawable/bg_chip"
                android:paddingStart="13dp" android:paddingEnd="13dp" android:paddingTop="6dp" android:paddingBottom="6dp"
                android:textColor="@color/offex_purple2" android:textSize="12sp" />
        </LinearLayout>

        <LinearLayout android:layout_width="match_parent" android:layout_height="wrap_content"
            android:layout_marginTop="16dp" android:background="@drawable/bg_card" android:elevation="3dp"
            android:orientation="vertical" android:padding="20dp">
            <TextView android:id="@+id/rBody" android:layout_width="match_parent" android:layout_height="wrap_content"
                android:textColor="@color/offex_text" android:textSize="15sp" android:lineSpacingExtra="6dp" />
        </LinearLayout>
    </LinearLayout>
</ScrollView>
"""

# ---------------------------------------------------------------- admin (overwritten by gn_h)
F["layout/activity_admin.xml"]="""<?xml version="1.0" encoding="utf-8"?>
<ScrollView xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent" android:layout_height="match_parent"
    android:background="@color/offex_bg">
    <LinearLayout android:layout_width="match_parent" android:layout_height="wrap_content"
        android:orientation="vertical" android:padding="18dp">
        <TextView android:layout_width="wrap_content" android:layout_height="wrap_content"
            android:text="@string/admin" android:textColor="@color/offex_text" android:textSize="22sp" android:textStyle="bold" />
        <EditText android:id="@+id/codeBox" android:layout_width="match_parent" android:layout_height="54dp"
            android:layout_marginTop="16dp" android:background="@drawable/bg_input" android:hint="@string/admin_hint"
            android:inputType="textPassword" android:paddingStart="18dp" android:paddingEnd="18dp"
            android:textColorHint="@color/offex_text_mute" android:textColor="@color/offex_text" />
        <androidx.appcompat.widget.AppCompatButton android:id="@+id/unlockBtn"
            android:layout_width="match_parent" android:layout_height="54dp"
            android:layout_marginTop="12dp" android:insetTop="0dp" android:insetBottom="0dp"
            android:background="@drawable/bg_btn_primary" android:textColor="@color/offex_white"
            android:textAllCaps="false" android:textSize="16sp" android:text="@string/unlock" />
        <LinearLayout android:id="@+id/panel" android:layout_width="match_parent" android:layout_height="wrap_content"
            android:layout_marginTop="18dp" android:background="@drawable/bg_card" android:elevation="3dp"
            android:orientation="vertical" android:padding="18dp" android:visibility="gone">
            <Switch android:id="@+id/notifySwitch" android:layout_width="match_parent" android:layout_height="wrap_content"
                android:text="@string/notif_on" android:textColor="@color/offex_text" />
            <TextView android:id="@+id/versionText" android:layout_width="match_parent" android:layout_height="wrap_content"
                android:layout_marginTop="14dp" android:textColor="@color/offex_text_dim" android:textSize="13sp" />
        </LinearLayout>
    </LinearLayout>
</ScrollView>
"""

for rel,c in F.items():
    p=os.path.join(RES,rel); os.makedirs(os.path.dirname(p),exist_ok=True)
    open(p,"w",encoding="utf-8").write(c)
print("E futuristic premium:",len(F))
