# ============================================================================
#  gn_z.py  -  v4.3  (NEW LAST WRITER, runs after gn_y)
# ============================================================================
#  Two jobs:
#   (B1) A premium UI redesign of the app - richer hero, glass/elevated cards,
#        generous spacing, stronger typography, a remote banner, a nicer inbox
#        list and reader, and a polished bottom nav.
#   (B2) Remote appearance: the app reads the "appearance" object from
#        /api/app-config on launch/resume and applies theme mode, accent
#        colours, corner radius, titles, button labels, section toggles,
#        banner and links LIVE - no new APK, no version change.
#  Plus the 4.2 -> 4.3 version bump.
# ============================================================================
import os, re

ROOT = "android"; APP = ROOT + "/app"
RES = APP + "/src/main/res"
J = APP + "/src/main/java/online/mytempmail/app"
os.makedirs(J, exist_ok=True)
os.makedirs(RES + "/drawable", exist_ok=True)

def W(p, s):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(s)

def R(p):
    with open(p, encoding="utf-8") as f:
        return f.read()

def REP(path, old, new, tag):
    s = R(path)
    if s.count(old) != 1:
        raise SystemExit("gn_z: anchor %s not unique (%d) in %s" % (tag, s.count(old), path))
    W(path, s.replace(old, new, 1))
    print("Z: patched %s (%s)" % (path, tag))

# ============================================================================
# 1 : PREMIUM LAYOUT  (keeps every id the Java code already uses, adds ids for
#     the remote-driven text + feature icons + banner)
# ============================================================================
LAYOUT_MAIN = '''<?xml version="1.0" encoding="utf-8"?>
<FrameLayout xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    android:layout_width="match_parent" android:layout_height="match_parent"
    android:background="?attr/oxBg">

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

            <!-- ===== HERO ===== -->
            <LinearLayout android:id="@+id/heroBox" android:layout_width="match_parent"
                android:layout_height="wrap_content" android:background="@drawable/bg_hero"
                android:orientation="vertical" android:paddingStart="22dp" android:paddingEnd="22dp"
                android:paddingTop="30dp" android:paddingBottom="34dp">

                <LinearLayout android:layout_width="match_parent" android:layout_height="wrap_content"
                    android:orientation="horizontal" android:gravity="center_vertical">
                    <TextView android:id="@+id/heroLogo" android:layout_width="48dp" android:layout_height="48dp"
                        android:background="@drawable/bg_logo" android:elevation="8dp" android:gravity="center"
                        android:text="@string/glyph_mail" android:textColor="@color/offex_white" android:textSize="22sp" />
                    <LinearLayout android:layout_width="0dp" android:layout_height="wrap_content"
                        android:layout_weight="1" android:layout_marginStart="14dp" android:orientation="vertical">
                        <TextView android:id="@+id/heroTitle" android:layout_width="wrap_content"
                            android:layout_height="wrap_content" android:text="@string/app_name"
                            android:textColor="@color/offex_white" android:textSize="22sp"
                            android:textStyle="bold" android:fontFamily="sans-serif-black"
                            android:letterSpacing="0.01" />
                        <TextView android:id="@+id/heroTagline" android:layout_width="wrap_content"
                            android:layout_height="wrap_content" android:layout_marginTop="2dp"
                            android:text="@string/tagline" android:textColor="#E6FFFFFF"
                            android:textSize="12sp" />
                    </LinearLayout>
                    <androidx.appcompat.widget.AppCompatButton android:id="@+id/settingsBtn"
                        android:layout_width="46dp" android:layout_height="46dp"
                        android:insetTop="0dp" android:insetBottom="0dp" android:padding="0dp"
                        android:background="@drawable/bg_btn_ghost" android:text="@string/glyph_gear"
                        android:textColor="?attr/oxText" android:textSize="18sp" />
                </LinearLayout>

                <TextView android:id="@+id/heroLabel" android:layout_width="wrap_content"
                    android:layout_height="wrap_content" android:layout_marginTop="24dp"
                    android:text="@string/your_address" android:textColor="@color/offex_white"
                    android:textSize="11sp" android:textStyle="bold" android:letterSpacing="0.14" />

                <LinearLayout android:id="@+id/activeCard" android:layout_width="match_parent"
                    android:layout_height="wrap_content" android:layout_marginTop="12dp"
                    android:background="@drawable/bg_card_hero" android:elevation="12dp"
                    android:orientation="vertical" android:padding="20dp" android:visibility="gone">

                    <TextView android:id="@+id/addrText" android:layout_width="match_parent"
                        android:layout_height="wrap_content" android:textColor="?attr/oxText"
                        android:textSize="19sp" android:textStyle="bold"
                        android:fontFamily="sans-serif-medium" android:textIsSelectable="true" />

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
                            android:background="@drawable/bg_btn_ghost" android:textColor="?attr/oxText"
                            android:textAllCaps="false" android:textSize="14sp" android:text="@string/refresh" />
                        <androidx.appcompat.widget.AppCompatButton android:id="@+id/deleteBtn"
                            android:layout_width="0dp" android:layout_height="48dp" android:layout_weight="1"
                            android:layout_marginStart="10dp" android:insetTop="0dp" android:insetBottom="0dp"
                            android:background="@drawable/bg_btn_danger" android:textColor="@color/offex_red"
                            android:textAllCaps="false" android:textSize="14sp" android:text="@string/delete" />
                    </LinearLayout>

                    <TextView android:id="@+id/countdownText" android:layout_width="wrap_content"
                        android:layout_height="wrap_content" android:layout_marginTop="16dp"
                        android:background="@drawable/bg_chip" android:paddingStart="16dp" android:paddingEnd="16dp"
                        android:paddingTop="7dp" android:paddingBottom="7dp"
                        android:textColor="?attr/oxChipText" android:textSize="12sp" android:textStyle="bold" />
                </LinearLayout>

                <TextView android:id="@+id/createLabel" android:layout_width="wrap_content"
                    android:layout_height="wrap_content" android:layout_marginTop="28dp"
                    android:text="@string/create_new_email" android:textColor="@color/offex_white"
                    android:textSize="11sp" android:textStyle="bold" android:letterSpacing="0.14" />

                <EditText android:id="@+id/nameBox" android:layout_width="match_parent" android:layout_height="56dp"
                    android:layout_marginTop="10dp" android:background="@drawable/bg_input"
                    android:hint="@string/hint_name" android:inputType="text" android:maxLines="1"
                    android:paddingStart="18dp" android:paddingEnd="18dp"
                    android:textColorHint="?attr/oxTextMute" android:textColor="?attr/oxText"
                    android:textSize="15sp" />

                <Spinner android:id="@+id/domainBox" android:layout_width="match_parent"
                    android:layout_height="56dp" android:layout_marginTop="12dp"
                    android:background="@drawable/bg_input"
                    android:paddingStart="14dp" android:paddingEnd="14dp" />

                <androidx.appcompat.widget.AppCompatButton android:id="@+id/createBtn"
                    android:layout_width="match_parent" android:layout_height="58dp"
                    android:layout_marginTop="18dp" android:insetTop="0dp" android:insetBottom="0dp"
                    android:background="@drawable/bg_btn_primary" android:textColor="@color/offex_white"
                    android:textAllCaps="false" android:textSize="16sp" android:textStyle="bold"
                    android:fontFamily="sans-serif-medium" android:text="@string/create_inbox" />
            </LinearLayout>

            <!-- ===== INBOX ===== -->
            <TextView android:id="@+id/secInbox" android:layout_width="wrap_content"
                android:layout_height="wrap_content" android:layout_marginStart="22dp" android:layout_marginTop="28dp"
                android:text="@string/inbox_title" android:textColor="?attr/oxText" android:textSize="18sp"
                android:textStyle="bold" android:fontFamily="sans-serif-medium" />

            <TextView android:id="@+id/inboxAddr" android:layout_width="match_parent" android:layout_height="wrap_content"
                android:layout_marginStart="22dp" android:layout_marginEnd="22dp" android:layout_marginTop="3dp"
                android:textColor="?attr/oxTextDim" android:textSize="13sp" />

            <TextView android:id="@+id/emptyText" android:layout_width="match_parent" android:layout_height="wrap_content"
                android:layout_marginStart="18dp" android:layout_marginEnd="18dp" android:layout_marginTop="14dp"
                android:background="@drawable/bg_card" android:elevation="3dp" android:padding="22dp"
                android:text="@string/no_messages" android:textColor="?attr/oxTextDim"
                android:textSize="14sp" android:lineSpacingExtra="5dp" />

            <androidx.recyclerview.widget.RecyclerView android:id="@+id/msgList"
                android:layout_width="match_parent" android:layout_height="wrap_content"
                android:layout_marginStart="16dp" android:layout_marginEnd="16dp"
                android:layout_marginTop="6dp" android:nestedScrollingEnabled="false" />

            <!-- ===== SWITCH EMAIL ===== -->
            <TextView android:id="@+id/secSwitch" android:layout_width="wrap_content"
                android:layout_height="wrap_content" android:layout_marginStart="22dp" android:layout_marginTop="28dp"
                android:text="@string/switch_title" android:textColor="?attr/oxText" android:textSize="18sp"
                android:textStyle="bold" android:fontFamily="sans-serif-medium" />

            <TextView android:id="@+id/secChoose" android:layout_width="match_parent" android:layout_height="wrap_content"
                android:layout_marginStart="22dp" android:layout_marginEnd="22dp" android:layout_marginTop="3dp"
                android:text="@string/choose_email" android:textColor="?attr/oxTextDim" android:textSize="13sp" />

            <TextView android:id="@+id/historyEmpty" android:layout_width="match_parent"
                android:layout_height="wrap_content" android:layout_marginStart="18dp" android:layout_marginEnd="18dp"
                android:layout_marginTop="14dp" android:background="@drawable/bg_card" android:elevation="3dp"
                android:padding="20dp" android:text="@string/history_empty"
                android:textColor="?attr/oxTextDim" android:textSize="14sp" />

            <LinearLayout android:id="@+id/historyBox" android:layout_width="match_parent"
                android:layout_height="wrap_content" android:layout_marginStart="16dp"
                android:layout_marginEnd="16dp" android:orientation="vertical" />

            <!-- ===== NATIVE AD ===== -->
            <LinearLayout android:id="@+id/nativeAdBox" android:layout_width="match_parent"
                android:layout_height="wrap_content" android:layout_marginStart="16dp"
                android:layout_marginEnd="16dp" android:layout_marginTop="16dp"
                android:orientation="vertical" android:visibility="gone" />

            <!-- ===== FEATURES ===== -->
            <TextView android:id="@+id/secFeatures" android:layout_width="wrap_content"
                android:layout_height="wrap_content" android:layout_marginStart="22dp" android:layout_marginTop="28dp"
                android:text="@string/features_title" android:textColor="?attr/oxText" android:textSize="18sp"
                android:textStyle="bold" android:fontFamily="sans-serif-medium" />
            <TextView android:id="@+id/secFeaturesSub" android:layout_width="match_parent"
                android:layout_height="wrap_content" android:layout_marginStart="22dp" android:layout_marginEnd="22dp"
                android:layout_marginTop="3dp" android:text="@string/features_sub"
                android:textColor="?attr/oxTextDim" android:textSize="13sp" />

            <LinearLayout android:id="@+id/featuresBox" android:layout_width="match_parent"
                android:layout_height="wrap_content" android:layout_marginStart="16dp"
                android:layout_marginEnd="16dp" android:orientation="vertical">
                <LinearLayout android:layout_width="match_parent" android:layout_height="wrap_content"
                    android:layout_marginTop="12dp" android:background="@drawable/bg_card" android:elevation="3dp"
                    android:orientation="horizontal" android:gravity="center_vertical" android:padding="16dp">
                    <TextView android:id="@+id/fi1" android:layout_width="46dp" android:layout_height="46dp"
                        android:background="@drawable/bg_logo" android:gravity="center"
                        android:text="&#9889;" android:textColor="@color/offex_white" android:textSize="20sp" />
                    <LinearLayout android:layout_width="0dp" android:layout_height="wrap_content"
                        android:layout_weight="1" android:layout_marginStart="15dp" android:orientation="vertical">
                        <TextView android:layout_width="match_parent" android:layout_height="wrap_content"
                            android:text="@string/feat1_t" android:textColor="?attr/oxText"
                            android:textSize="14sp" android:textStyle="bold" />
                        <TextView android:layout_width="match_parent" android:layout_height="wrap_content"
                            android:layout_marginTop="2dp" android:text="@string/feat1_d"
                            android:textColor="?attr/oxTextDim" android:textSize="12.5sp" android:lineSpacingExtra="3dp" />
                    </LinearLayout>
                </LinearLayout>
                <LinearLayout android:layout_width="match_parent" android:layout_height="wrap_content"
                    android:layout_marginTop="10dp" android:background="@drawable/bg_card" android:elevation="3dp"
                    android:orientation="horizontal" android:gravity="center_vertical" android:padding="16dp">
                    <TextView android:id="@+id/fi2" android:layout_width="46dp" android:layout_height="46dp"
                        android:background="@drawable/bg_logo" android:gravity="center"
                        android:text="&#128273;" android:textColor="@color/offex_white" android:textSize="20sp" />
                    <LinearLayout android:layout_width="0dp" android:layout_height="wrap_content"
                        android:layout_weight="1" android:layout_marginStart="15dp" android:orientation="vertical">
                        <TextView android:layout_width="match_parent" android:layout_height="wrap_content"
                            android:text="@string/feat2_t" android:textColor="?attr/oxText"
                            android:textSize="14sp" android:textStyle="bold" />
                        <TextView android:layout_width="match_parent" android:layout_height="wrap_content"
                            android:layout_marginTop="2dp" android:text="@string/feat2_d"
                            android:textColor="?attr/oxTextDim" android:textSize="12.5sp" android:lineSpacingExtra="3dp" />
                    </LinearLayout>
                </LinearLayout>
                <LinearLayout android:layout_width="match_parent" android:layout_height="wrap_content"
                    android:layout_marginTop="10dp" android:background="@drawable/bg_card" android:elevation="3dp"
                    android:orientation="horizontal" android:gravity="center_vertical" android:padding="16dp">
                    <TextView android:id="@+id/fi3" android:layout_width="46dp" android:layout_height="46dp"
                        android:background="@drawable/bg_logo" android:gravity="center"
                        android:text="&#128279;" android:textColor="@color/offex_white" android:textSize="20sp" />
                    <LinearLayout android:layout_width="0dp" android:layout_height="wrap_content"
                        android:layout_weight="1" android:layout_marginStart="15dp" android:orientation="vertical">
                        <TextView android:layout_width="match_parent" android:layout_height="wrap_content"
                            android:text="@string/feat3_t" android:textColor="?attr/oxText"
                            android:textSize="14sp" android:textStyle="bold" />
                        <TextView android:layout_width="match_parent" android:layout_height="wrap_content"
                            android:layout_marginTop="2dp" android:text="@string/feat3_d"
                            android:textColor="?attr/oxTextDim" android:textSize="12.5sp" android:lineSpacingExtra="3dp" />
                    </LinearLayout>
                </LinearLayout>
                <LinearLayout android:layout_width="match_parent" android:layout_height="wrap_content"
                    android:layout_marginTop="10dp" android:background="@drawable/bg_card" android:elevation="3dp"
                    android:orientation="horizontal" android:gravity="center_vertical" android:padding="16dp">
                    <TextView android:id="@+id/fi4" android:layout_width="46dp" android:layout_height="46dp"
                        android:background="@drawable/bg_logo" android:gravity="center"
                        android:text="&#128276;" android:textColor="@color/offex_white" android:textSize="20sp" />
                    <LinearLayout android:layout_width="0dp" android:layout_height="wrap_content"
                        android:layout_weight="1" android:layout_marginStart="15dp" android:orientation="vertical">
                        <TextView android:layout_width="match_parent" android:layout_height="wrap_content"
                            android:text="@string/feat4_t" android:textColor="?attr/oxText"
                            android:textSize="14sp" android:textStyle="bold" />
                        <TextView android:layout_width="match_parent" android:layout_height="wrap_content"
                            android:layout_marginTop="2dp" android:text="@string/feat4_d"
                            android:textColor="?attr/oxTextDim" android:textSize="12.5sp" android:lineSpacingExtra="3dp" />
                    </LinearLayout>
                </LinearLayout>
                <LinearLayout android:layout_width="match_parent" android:layout_height="wrap_content"
                    android:layout_marginTop="10dp" android:background="@drawable/bg_card" android:elevation="3dp"
                    android:orientation="horizontal" android:gravity="center_vertical" android:padding="16dp">
                    <TextView android:id="@+id/fi5" android:layout_width="46dp" android:layout_height="46dp"
                        android:background="@drawable/bg_logo" android:gravity="center"
                        android:text="&#127760;" android:textColor="@color/offex_white" android:textSize="20sp" />
                    <LinearLayout android:layout_width="0dp" android:layout_height="wrap_content"
                        android:layout_weight="1" android:layout_marginStart="15dp" android:orientation="vertical">
                        <TextView android:layout_width="match_parent" android:layout_height="wrap_content"
                            android:text="@string/feat5_t" android:textColor="?attr/oxText"
                            android:textSize="14sp" android:textStyle="bold" />
                        <TextView android:layout_width="match_parent" android:layout_height="wrap_content"
                            android:layout_marginTop="2dp" android:text="@string/feat5_d"
                            android:textColor="?attr/oxTextDim" android:textSize="12.5sp" android:lineSpacingExtra="3dp" />
                    </LinearLayout>
                </LinearLayout>
                <LinearLayout android:layout_width="match_parent" android:layout_height="wrap_content"
                    android:layout_marginTop="10dp" android:background="@drawable/bg_card" android:elevation="3dp"
                    android:orientation="horizontal" android:gravity="center_vertical" android:padding="16dp">
                    <TextView android:id="@+id/fi6" android:layout_width="46dp" android:layout_height="46dp"
                        android:background="@drawable/bg_logo" android:gravity="center"
                        android:text="&#9203;" android:textColor="@color/offex_white" android:textSize="20sp" />
                    <LinearLayout android:layout_width="0dp" android:layout_height="wrap_content"
                        android:layout_weight="1" android:layout_marginStart="15dp" android:orientation="vertical">
                        <TextView android:layout_width="match_parent" android:layout_height="wrap_content"
                            android:text="@string/feat6_t" android:textColor="?attr/oxText"
                            android:textSize="14sp" android:textStyle="bold" />
                        <TextView android:layout_width="match_parent" android:layout_height="wrap_content"
                            android:layout_marginTop="2dp" android:text="@string/feat6_d"
                            android:textColor="?attr/oxTextDim" android:textSize="12.5sp" android:lineSpacingExtra="3dp" />
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
'''
W(RES + "/layout/activity_main.xml", LAYOUT_MAIN)
print("Z: activity_main.xml (premium) written")

# --- inbox row : richer, taller, more spacing ---
ITEM_MSG = '''<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent" android:layout_height="wrap_content"
    android:layout_marginTop="10dp" android:background="@drawable/bg_card"
    android:elevation="3dp" android:orientation="horizontal" android:padding="16dp">

    <TextView android:layout_width="46dp" android:layout_height="46dp"
        android:background="@drawable/bg_avatar" android:gravity="center"
        android:text="@string/glyph_mail" android:textColor="@color/offex_white" android:textSize="18sp" />

    <LinearLayout android:layout_width="0dp" android:layout_height="wrap_content"
        android:layout_weight="1" android:layout_marginStart="15dp" android:orientation="vertical">

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
            android:layout_marginTop="10dp" android:orientation="horizontal" android:gravity="center_vertical">
            <TextView android:id="@+id/mService" android:layout_width="wrap_content" android:layout_height="wrap_content"
                android:background="@drawable/bg_chip" android:paddingStart="11dp" android:paddingEnd="11dp"
                android:paddingTop="4dp" android:paddingBottom="4dp"
                android:textColor="?attr/oxChipText" android:textSize="10sp" android:textStyle="bold"
                android:letterSpacing="0.06" android:text="@string/item_mail_label" />
            <TextView android:id="@+id/mOtp" android:layout_width="wrap_content" android:layout_height="wrap_content"
                android:layout_marginStart="8dp" android:background="@drawable/bg_chip_green"
                android:paddingStart="11dp" android:paddingEnd="11dp" android:paddingTop="4dp" android:paddingBottom="4dp"
                android:textColor="@color/offex_green" android:textSize="12sp" android:textStyle="bold"
                android:visibility="gone" />
        </LinearLayout>
    </LinearLayout>
</LinearLayout>
'''
W(RES + "/layout/item_message.xml", ITEM_MSG)
print("Z: item_message.xml (premium) written")

# ============================================================================
# 2 : PREMIUM DRAWABLES
# ============================================================================
W(RES + "/drawable/bg_hero.xml", '''<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="rectangle">
    <gradient android:type="linear" android:angle="270"
        android:startColor="#E53935" android:centerColor="#FF6F60" android:endColor="#FF8A80" />
    <corners android:bottomLeftRadius="34dp" android:bottomRightRadius="34dp" />
</shape>
''')
W(RES + "/drawable/bg_banner.xml", '''<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="rectangle">
    <solid android:color="?attr/oxChipBg" />
    <corners android:radius="16dp" />
    <stroke android:width="1dp" android:color="?attr/oxChipBorder" />
</shape>
''')
W(RES + "/drawable/bg_icon.xml", '''<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="oval">
    <gradient android:startColor="#E53935" android:centerColor="#EF5350" android:endColor="#FF8A80"
        android:angle="315" />
</shape>
''')
print("Z: premium drawables written")

# ============================================================================
# 3 : Ui.java  -  applies the remote appearance config LIVE
# ============================================================================
UI = '''package online.mytempmail.app;
import android.app.Activity;
import android.content.Intent;
import android.graphics.Color;
import android.graphics.drawable.GradientDrawable;
import android.net.Uri;
import android.view.View;
import android.widget.TextView;
import org.json.JSONObject;

/**
 * v4.3 - the whole app look is driven by the "appearance" object that the
 * admin panel pushes to /api/app-config. Ui.apply() reads it and applies the
 * theme mode, accent colours, corner radius, titles, button labels, section
 * toggles, banner and links to the already-inflated screen - so the look can
 * change WITHOUT a new APK and without a version bump.
 */
public class Ui {
    private static boolean heroShown = false;

    private static int dp(Activity a, int v){
        try { return (int)(a.getResources().getDisplayMetrics().density * v); } catch(Exception e){ return v; }
    }
    private static int col(String hex, int def){
        try { String s = hex == null ? "" : hex.trim(); if(s.isEmpty()) return def; return Color.parseColor(s); }
        catch(Exception e){ return def; }
    }
    public static int accent(){
        try { return col(Config.appearance().optString("accent", ""), 0xFFE53935); }
        catch(Exception e){ return 0xFFE53935; }
    }
    public static int navIdle(){ return Prefs.isDark() ? 0xFF6E7390 : 0xFF9A96AD; }

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
            t.setText(title + "\\n\\n" + body);
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
            int accent  = col(ap.optString("accent", ""), 0xFFE53935);
            int accent2 = col(ap.optString("accent2", ""), 0xFFFF6F60);
            int gs = col(ap.optString("gradient_start", ""), accent);
            int ge = col(ap.optString("gradient_end", ""), accent2);
            int radius = ap.optInt("radius", 20);
            if(radius < 0) radius = 0;
            float r = dp(a, radius > 0 ? radius : 20);
            float pill = dp(a, 999);
            boolean dark = Prefs.isDark();
            int card = dark ? 0xFF1A1C27 : 0xFFFFFFFF;
            int cardBorder = dark ? 0xFF2A2D3D : 0xFFEDEAF7;
            int text = dark ? 0xFFF2F3F8 : 0xFF1B1730;
            int textDim = dark ? 0xFFA6ABC0 : 0xFF5C5875;
            int ghost = dark ? 0xFF23273A : 0xFFFFFFFF;
            int chipBg = dark ? 0xFF3B2320 : 0xFFFDECEA;
            int chipBorder = dark ? 0xFF5A3733 : 0xFFF6CFCB;
            int chipText = dark ? 0xFFFFCDD2 : 0xFFC62828;
            int dangerBg = dark ? 0xFF3B2320 : 0xFFFDE9EB;
            int dangerBorder = dark ? 0xFF5A3733 : 0xFFF6CDD2;

            setBg(a, R.id.heroBox, gradRadii(gs, ge, new float[]{0,0,0,0,r,r,r,r}));
            setColor(a, R.id.heroTitle, 0xFFFFFFFF);
            setColor(a, R.id.heroTagline, 0xE6FFFFFF);
            setColor(a, R.id.heroLabel, 0xE6FFFFFF);
            setBg(a, R.id.heroLogo, grad(gs, ge, dp(a, 999)));

            setBg(a, R.id.activeCard, solid(card, r, cardBorder, dp(a,1)));
            setColor(a, R.id.addrText, text);

            setBg(a, R.id.createBtn, grad(gs, ge, pill));
            setBg(a, R.id.copyBtn, grad(accent, accent2, pill));
            setBg(a, R.id.refreshBtn, solid(ghost, pill, cardBorder, dp(a,1)));
            setBg(a, R.id.deleteBtn, solid(dangerBg, pill, dangerBorder, dp(a,1)));
            setBg(a, R.id.settingsBtn, solid(0x33FFFFFF, pill, 0x33FFFFFF, dp(a,1)));

            setBg(a, R.id.countdownText, solid(chipBg, pill, chipBorder, dp(a,1)));
            setColor(a, R.id.countdownText, chipText);

            setBg(a, R.id.nameBox, solid(dark ? 0xFF1A1C27 : 0xFFF3F1FB, dp(a,16), cardBorder, dp(a,1)));
            setBg(a, R.id.domainBox, solid(dark ? 0xFF1A1C27 : 0xFFF3F1FB, dp(a,16), cardBorder, dp(a,1)));

            setBg(a, R.id.emptyText, solid(card, r, cardBorder, dp(a,1)));
            setBg(a, R.id.historyEmpty, solid(card, r, cardBorder, dp(a,1)));
            setColor(a, R.id.emptyText, textDim);
            setColor(a, R.id.historyEmpty, textDim);

            setBg(a, R.id.navBar, solidRadii(dark ? 0xFF14161F : 0xFFFFFFFF,
                    new float[]{r, r, r, r, 0, 0, 0, 0}, cardBorder, dp(a,1)));

            setColor(a, R.id.secInbox, text);
            setColor(a, R.id.secSwitch, text);
            setColor(a, R.id.secFeatures, text);
            setColor(a, R.id.secChoose, textDim);
            setColor(a, R.id.secFeaturesSub, textDim);
            setColor(a, R.id.inboxAddr, textDim);

            int[] fi = {R.id.fi1, R.id.fi2, R.id.fi3, R.id.fi4, R.id.fi5, R.id.fi6};
            for(int id : fi) setBg(a, id, grad(gs, ge, dp(a, 999)));

            setText(a, R.id.heroTitle, Config.appStr("hero_title", a.getString(R.string.app_name)));
            setText(a, R.id.heroTagline, Config.appStr("hero_tagline", a.getString(R.string.tagline)));
            setText(a, R.id.heroLabel, Config.appStr("hero_label", a.getString(R.string.your_address)));
            setText(a, R.id.createBtn, Config.appStr("create_label", a.getString(R.string.create_inbox)));
            setText(a, R.id.copyBtn, Config.appStr("copy_label", a.getString(R.string.copy)));
            setText(a, R.id.refreshBtn, Config.appStr("refresh_label", a.getString(R.string.refresh)));
            setText(a, R.id.deleteBtn, Config.appStr("delete_label", a.getString(R.string.delete)));
            setText(a, R.id.secInbox, Config.appStr("inbox_title", a.getString(R.string.inbox_title)));
            setText(a, R.id.secSwitch, Config.appStr("switch_title", a.getString(R.string.switch_title)));
            setText(a, R.id.secChoose, Config.appStr("switch_sub", a.getString(R.string.choose_email)));
            setText(a, R.id.secFeatures, Config.appStr("features_title", a.getString(R.string.features_title)));
            setText(a, R.id.secFeaturesSub, Config.appStr("features_sub", a.getString(R.string.features_sub)));
            setEmptyText(a);

            boolean showHero = Config.flag("show_hero", true);
            vis(a, R.id.heroBox, showHero);
            boolean showSwitch = Config.flag("show_switch", true);
            vis(a, R.id.secSwitch, showSwitch);
            vis(a, R.id.secChoose, showSwitch);
            if(!showSwitch) vis(a, R.id.historyBox, false);
            vis(a, R.id.historyEmpty, showSwitch);

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
W(J + "/Ui.java", UI)
print("Z: Ui.java written")

# ============================================================================
# 4 : Config.java  -  parse + persist the "appearance" object, apply live
# ============================================================================
REP(J + "/Config.java",
'''    public static void refresh(){
        try { j = new JSONObject(ApiClient.get("/api/app-config")); } catch(Exception e){}
    }''',
'''    public static void refresh(){
        try { j = new JSONObject(ApiClient.get("/api/app-config")); persistAppearance(); } catch(Exception e){}
    }

    private static final String AP_KEY = "appearance_json";

    // Keep a copy of the pushed appearance locally, so the look survives an
    // offline launch and can be compared to detect a change.
    private static void persistAppearance(){
        try { if(ctx != null){ JSONObject ap = j.optJSONObject("appearance");
              if(ap != null) sp(ctx).edit().putString(AP_KEY, ap.toString()).apply(); } } catch(Exception e){}
    }

    /** The remote "appearance" object (live if fetched, else last saved copy). */
    public static JSONObject appearance(){
        try {
            JSONObject ap = j.optJSONObject("appearance");
            if(ap != null) return ap;
            if(ctx != null){
                String s = sp(ctx).getString(AP_KEY, "");
                if(s != null && !s.isEmpty()) return new JSONObject(s);
            }
        } catch(Exception e){}
        return new JSONObject();
    }
    public static String appStr(String key, String def){
        try { String v = appearance().optString(key, ""); if(v != null && !v.isEmpty()) return v; } catch(Exception e){}
        return def;
    }
    public static int appInt(String key, int def){
        try { return appearance().optInt(key, def); } catch(Exception e){ return def; }
    }
    public static boolean appFlag(String key, boolean def){
        try { JSONObject ap = appearance(); if(ap.has(key)) return ap.optBoolean(key, def); } catch(Exception e){}
        return def;
    }''', "refresh+appearance")

REP(J + "/Config.java",
'''    public static boolean flag(String key, boolean def){
        try {
            if(ctx == null) return def;
            JSONObject o = new JSONObject(sp(ctx).getString("feat_flags", "{}"));
            if(o.has(key)) return o.optBoolean(key, def);
        } catch(Exception e){}
        return def;
    }''',
'''    public static boolean flag(String key, boolean def){
        try {
            if(ctx != null){
                JSONObject o = new JSONObject(sp(ctx).getString("feat_flags", "{}"));
                if(o.has(key)) return o.optBoolean(key, def);
            }
        } catch(Exception e){}
        // section toggles can also come from the remote "appearance" object
        if("show_features".equals(key))  return appFlag("show_features", def);
        if("show_otp_card".equals(key))  return appFlag("show_otp_card", def);
        if("show_history".equals(key))   return appFlag("show_history", def);
        if("show_switch".equals(key))    return appFlag("show_switch", def);
        if("show_hero".equals(key))      return appFlag("show_hero", def);
        return def;
    }''', "flag+appearance")

REP(J + "/Config.java",
'''                        try { applyFeature(a, null); } catch(Exception e){}
                    });''',
'''                        try { applyFeature(a, null); } catch(Exception e){}
                        try { Ui.apply(a); } catch(Exception e){}
                    });''', "apply->Ui")

REP(J + "/Config.java",
'''        if(afterUI != null){ try { a.runOnUiThread(afterUI); } catch(Exception e){} }''',
'''        try { Ui.apply(a); } catch(Exception e){}
        if(afterUI != null){ try { a.runOnUiThread(afterUI); } catch(Exception e){} }''', "applyFeature->Ui")

REP(J + "/Config.java", 'if(latest.equals("4.2")) return;', 'if(latest.equals("4.3")) return;', "update-check 4.3")

# ============================================================================
# 5 : Prefs.java  -  remember whether the user chose a theme themselves
# ============================================================================
REP(J + "/Prefs.java",
'    public static void setNotifSound(int i){ sp.edit().putInt("notif_sound",i).apply(); }\n}',
'''    public static void setNotifSound(int i){ sp.edit().putInt("notif_sound",i).apply(); }
    public static boolean themeChosen(){ return sp.getBoolean("theme_chosen",false); }
    public static void setThemeChosen(boolean v){ sp.edit().putBoolean("theme_chosen",v).apply(); }
}''', "themeChosen")

# ============================================================================
# 6 : Menu.java  -  a manual theme pick overrides the remote default
# ============================================================================
REP(J + "/Menu.java",
'Prefs.setThemeMode(Prefs.isDark() ? "light" : "dark"); a.recreate();',
'Prefs.setThemeMode(Prefs.isDark() ? "light" : "dark"); Prefs.setThemeChosen(true); a.recreate();',
"themeChosen on manual pick")

# ============================================================================
# 7 : MainActivity.java  -  apply the appearance on create + resume, use the
#     remote accent for the nav, and keep the remote create-button label
# ============================================================================
REP(J + "/MainActivity.java",
'        Config.applyFeature(this, this::applyFeatureUI);\n',
'        Config.applyFeature(this, this::applyFeatureUI);\n        Ui.apply(this);\n',
"Ui.apply onCreate")

REP(J + "/MainActivity.java",
'        Config.refreshFeature(this,this::applyFeatureUI);\n        applyFeatureUI();\n',
'        Config.refreshFeature(this,this::applyFeatureUI);\n        applyFeatureUI();\n        Ui.apply(this);\n',
"Ui.apply onResume")

REP(J + "/MainActivity.java",
'                icons[i].setTextColor(i==idx?0xFFE53935:0xFF8A87A0);',
'                icons[i].setTextColor(i==idx?Ui.accent():Ui.navIdle());',
"nav accent")

REP(J + "/MainActivity.java",
'                t.setTextSize(14); t.setTextColor(addr.equals(cur)?0xFFE53935:resolveText());',
'                t.setTextSize(14); t.setTextColor(addr.equals(cur)?Ui.accent():resolveText());',
"history accent")

REP(J + "/MainActivity.java",
'            createBtn.setText(R.string.create_inbox);',
'            createBtn.setText(Config.appStr("create_label", getString(R.string.create_inbox)));',
"create label after loading")

REP(J + "/MainActivity.java",
'            if(emptyText!=null) emptyText.setText(Config.str("inbox_empty",getString(R.string.no_messages)));',
'''            View sw=findViewById(R.id.secSwitch); boolean showSwitch=Config.flag("show_switch",true);
            if(sw!=null) sw.setVisibility(showSwitch?View.VISIBLE:View.GONE);
            View cs=findViewById(R.id.secChoose); if(cs!=null) cs.setVisibility(showSwitch?View.VISIBLE:View.GONE);
            View hb=findViewById(R.id.historyEmpty); if(hb!=null) hb.setVisibility(showSwitch?View.VISIBLE:View.GONE);
            View hero=findViewById(R.id.heroBox); if(hero!=null) hero.setVisibility(Config.flag("show_hero",true)?View.VISIBLE:View.GONE);
            if(emptyText!=null) Ui.setEmptyText(this);''',
"applyFeatureUI toggles")

# ============================================================================
# 8 : VERSION 4.2 -> 4.3
# ============================================================================
REP(J + "/SupportActivity.java", 'public static final String VERSION = "4.2";',
    'public static final String VERSION = "4.3";', "SupportActivity version")

def bump(xml, key):
    a = xml.find('<string name="' + key + '">')
    if a < 0:
        return xml
    b = xml.find("</string>", a)
    return xml[:a] + xml[a:b].replace("4.2", "4.3") + xml[b:]

for loc in ["values", "values-hi", "values-es", "values-pt", "values-ar", "values-ru", "values-in"]:
    p = RES + "/" + loc + "/strings.xml"
    if not os.path.exists(p):
        continue
    t = R(p)
    t = bump(t, "about_version")
    t = bump(t, "admin_latest_hint")
    W(p, t)
    print("Z: %s/strings.xml -> 4.3" % loc)

print("Z: applied v4.3 (premium UI + remote appearance config; version 4.2 -> 4.3)")
