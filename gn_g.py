import os

RES = "android/app/src/main/res"
MAN = "android/app/src/main/AndroidManifest.xml"
LAY = RES + "/layout/activity_main.xml"
STR = RES + "/values/strings.xml"

s = open(LAY, encoding="utf-8").read()
anchor = ('<TextView android:layout_width="wrap_content" android:layout_height="wrap_content"\n'
          '            android:layout_marginStart="20dp" android:layout_marginTop="24dp" android:text="@string/messages"')
if s.count(anchor) != 1:
    raise SystemExit("layout anchor fail: %d" % s.count(anchor))

hist = ('<TextView android:layout_width="wrap_content" android:layout_height="wrap_content"\n'
        '            android:layout_marginStart="20dp" android:layout_marginTop="24dp" android:text="@string/history"\n'
        '            android:textColor="@color/offex_text" android:textSize="16sp" android:textStyle="bold" />\n\n'
        '        <TextView android:id="@+id/historyEmpty" android:layout_width="match_parent" android:layout_height="wrap_content"\n'
        '            android:layout_marginStart="20dp" android:layout_marginEnd="20dp" android:layout_marginTop="12dp"\n'
        '            android:background="@drawable/bg_card" android:padding="18dp"\n'
        '            android:text="@string/history_empty" android:textColor="@color/offex_text_dim" android:textSize="14sp" />\n\n'
        '        <LinearLayout android:id="@+id/historyBox" android:layout_width="match_parent"\n'
        '            android:layout_height="wrap_content" android:layout_marginStart="16dp" android:layout_marginEnd="16dp"\n'
        '            android:orientation="vertical" />\n\n'
        '        ') + anchor
s = s.replace(anchor, hist, 1)
open(LAY, "w", encoding="utf-8").write(s)
print("layout ok")

t = open(STR, encoding="utf-8").read()
a2 = '<string name="messages">Messages</string>'
if t.count(a2) != 1:
    raise SystemExit("strings anchor fail: %d" % t.count(a2))
t = t.replace(a2, a2 + '\n    <string name="history">History</string>\n    <string name="history_empty">Your past inboxes will appear here. Tap one to switch back to it.</string>', 1)
open(STR, "w", encoding="utf-8").write(t)
print("strings ok")

m = open(MAN, encoding="utf-8").read()
p1 = '<uses-permission android:name="android.permission.POST_NOTIFICATIONS" />'
if m.count(p1) != 1:
    raise SystemExit("manifest perm anchor fail: %d" % m.count(p1))
m = m.replace(p1, p1 + '\n    <uses-permission android:name="android.permission.FOREGROUND_SERVICE" />\n    <uses-permission android:name="android.permission.FOREGROUND_SERVICE_DATA_SYNC" />', 1)
p2 = '    </application>'
if m.count(p2) != 1:
    raise SystemExit("manifest app anchor fail: %d" % m.count(p2))
m = m.replace(p2, '        <service android:name=".MailService" android:exported="false" android:foregroundServiceType="dataSync" />\n' + p2, 1)
open(MAN, "w", encoding="utf-8").write(m)
print("manifest ok")
