import os
ROOT="android"; RES=ROOT+"/app/src/main/res"
F={}

F["values/colors.xml"]="""<?xml version="1.0" encoding="utf-8"?>
<resources>
    <color name="offex_purple">#6D4DFF</color>
    <color name="offex_purple2">#8B6CFF</color>
    <color name="offex_purple_dark">#4B2FD6</color>
    <color name="offex_purple_soft">#EDE8FF</color>
    <color name="offex_bg">#F6F7FC</color>
    <color name="offex_card">#FFFFFF</color>
    <color name="offex_line">#ECEDF5</color>
    <color name="offex_text">#101227</color>
    <color name="offex_text_dim">#7A7F97</color>
    <color name="offex_green">#12B76A</color>
    <color name="offex_green_soft">#E6F7EF</color>
    <color name="offex_red">#E5484D</color>
    <color name="offex_red_soft">#FDECEC</color>
    <color name="offex_white">#FFFFFF</color>
    <color name="offex_white_dim">#D9D2FF</color>
</resources>
"""

F["values/themes.xml"]="""<?xml version="1.0" encoding="utf-8"?>
<resources xmlns:tools="http://schemas.android.com/tools">
    <style name="Theme.Offex" parent="Theme.MaterialComponents.Light.NoActionBar">
        <item name="colorPrimary">@color/offex_purple</item>
        <item name="colorPrimaryVariant">@color/offex_purple_dark</item>
        <item name="colorOnPrimary">@color/offex_white</item>
        <item name="colorSecondary">@color/offex_purple</item>
        <item name="android:statusBarColor" tools:targetApi="l">@color/offex_purple_dark</item>
        <item name="android:windowBackground">@color/offex_bg</item>
        <item name="android:navigationBarColor">@color/offex_bg</item>
        <item name="android:windowLightNavigationBar" tools:targetApi="o">true</item>
    </style>
</resources>
"""

F["drawable/bg_header.xml"]="""<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="rectangle">
    <gradient android:startColor="#8B6CFF" android:centerColor="#6D4DFF" android:endColor="#4B2FD6" android:angle="315" />
    <corners android:bottomLeftRadius="26dp" android:bottomRightRadius="26dp" />
</shape>
"""

F["drawable/bg_card.xml"]="""<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="rectangle">
    <solid android:color="#FFFFFF" />
    <corners android:radius="18dp" />
</shape>
"""

F["drawable/bg_input.xml"]="""<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="rectangle">
    <solid android:color="#F3F4FB" />
    <corners android:radius="14dp" />
    <stroke android:width="1dp" android:color="#E7E9F4" />
</shape>
"""

F["drawable/bg_chip.xml"]="""<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="rectangle">
    <solid android:color="#EDE8FF" />
    <corners android:radius="999dp" />
</shape>
"""

F["drawable/bg_chip_green.xml"]="""<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="rectangle">
    <solid android:color="#E6F7EF" />
    <corners android:radius="999dp" />
</shape>
"""

F["drawable/bg_logo.xml"]="""<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="oval">
    <solid android:color="#FFFFFF" />
</shape>
"""

F["drawable/bg_avatar.xml"]="""<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="oval">
    <gradient android:startColor="#8B6CFF" android:endColor="#4B2FD6" android:angle="315" />
</shape>
"""

F["drawable/bg_btn_ghost.xml"]="""<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="rectangle">
    <solid android:color="#F3F4FB" />
    <corners android:radius="14dp" />
</shape>
"""

F["layout/activity_main.xml"]="""<?xml version="1.0" encoding="utf-8"?>
<ScrollView xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    android:layout_width="match_parent" android:layout_height="match_parent"
    android:background="@color/offex_bg" android:fillViewport="true">

    <LinearLayout android:layout_width="match_parent" android:layout_height="wrap_content"
        android:orientation="vertical" android:paddingBottom="28dp">

        <LinearLayout android:layout_width="match_parent" android:layout_height="wrap_content"
            android:background="@drawable/bg_header" android:orientation="vertical"
            android:paddingStart="20dp" android:paddingEnd="20dp"
            android:paddingTop="22dp" android:paddingBottom="26dp">

            <LinearLayout android:layout_width="match_parent" android:layout_height="wrap_content"
                android:orientation="horizontal" android:gravity="center_vertical">
                <TextView android:layout_width="42dp" android:layout_height="42dp"
                    android:background="@drawable/bg_logo" android:gravity="center"
                    android:text="\u2709" android:textColor="@color/offex_purple" android:textSize="20sp" />
                <LinearLayout android:layout_width="0dp" android:layout_height="wrap_content"
                    android:layout_weight="1" android:orientation="vertical" android:layout_marginStart="12dp">
                    <TextView android:layout_width="wrap_content" android:layout_height="wrap_content"
                        android:text="@string/app_name" android:textColor="@color/offex_white"
                        android:textSize="19sp" android:textStyle="bold" />
                    <TextView android:layout_width="wrap_content" android:layout_height="wrap_content"
                        android:text="@string/tagline" android:textColor="@color/offex_white_dim" android:textSize="12sp" />
                </LinearLayout>
                <Button android:id="@+id/settingsBtn" android:layout_width="42dp" android:layout_height="42dp"
                    android:insetTop="0dp" android:insetBottom="0dp" android:padding="0dp"
                    android:backgroundTint="#33FFFFFF" android:text="\u2699"
                    android:textColor="@color/offex_white" android:textSize="17sp" app:cornerRadius="999dp" />
            </LinearLayout>

            <TextView android:layout_width="wrap_content" android:layout_height="wrap_content"
                android:layout_marginTop="20dp" android:text="@string/new_inbox"
                android:textColor="@color/offex_white_dim" android:textSize="12sp" />

            <EditText android:id="@+id/nameBox" android:layout_width="match_parent" android:layout_height="52dp"
                android:layout_marginTop="8dp" android:background="@drawable/bg_input"
                android:hint="@string/hint_name" android:inputType="text" android:maxLines="1"
                android:paddingStart="16dp" android:paddingEnd="16dp"
                android:textColorHint="@color/offex_text_dim" android:textColor="@color/offex_text" android:textSize="15sp" />

            <Spinner android:id="@+id/domainBox" android:layout_width="match_parent"
                android:layout_height="52dp" android:layout_marginTop="10dp" android:background="@drawable/bg_input"
                android:paddingStart="10dp" android:paddingEnd="10dp" />

            <Button android:id="@+id/createBtn" android:layout_width="match_parent" android:layout_height="54dp"
                android:layout_marginTop="14dp" android:insetTop="0dp" android:insetBottom="0dp"
                android:backgroundTint="@color/offex_white" android:textColor="@color/offex_purple_dark"
                android:textAllCaps="false" android:textSize="16sp" android:textStyle="bold"
                android:text="@string/create_inbox" app:cornerRadius="16dp" />
        </LinearLayout>

        <LinearLayout android:id="@+id/activeCard" android:layout_width="match_parent"
            android:layout_height="wrap_content" android:layout_marginStart="16dp" android:layout_marginEnd="16dp"
            android:layout_marginTop="-16dp" android:background="@drawable/bg_card" android:elevation="8dp"
            android:orientation="vertical" android:padding="18dp" android:visibility="gone">

            <TextView android:layout_width="wrap_content" android:layout_height="wrap_content"
                android:text="@string/your_address" android:textColor="@color/offex_text_dim" android:textSize="11sp" />

            <TextView android:id="@+id/addrText" android:layout_width="match_parent" android:layout_height="wrap_content"
                android:layout_marginTop="6dp" android:textColor="@color/offex_text"
                android:textSize="19sp" android:textStyle="bold" android:textIsSelectable="true" />

            <TextView android:id="@+id/countdownText" android:layout_width="wrap_content"
                android:layout_height="wrap_content" android:layout_marginTop="10dp"
                android:background="@drawable/bg_chip" android:paddingStart="12dp" android:paddingEnd="12dp"
                android:paddingTop="5dp" android:paddingBottom="5dp"
                android:textColor="@color/offex_purple_dark" android:textSize="12sp" />

            <LinearLayout android:layout_width="match_parent" android:layout_height="wrap_content"
                android:layout_marginTop="14dp" android:orientation="horizontal">
                <Button android:id="@+id/copyBtn" android:layout_width="0dp" android:layout_height="46dp"
                    android:layout_weight="1" android:insetTop="0dp" android:insetBottom="0dp"
                    android:backgroundTint="@color/offex_purple" android:textColor="@color/offex_white"
                    android:textAllCaps="false" android:textSize="14sp" android:text="@string/copy" app:cornerRadius="14dp" />
                <Button android:id="@+id/refreshBtn" android:layout_width="0dp" android:layout_height="46dp"
                    android:layout_weight="1" android:layout_marginStart="10dp" android:insetTop="0dp" android:insetBottom="0dp"
                    android:backgroundTint="@color/offex_purple_soft" android:textColor="@color/offex_purple_dark"
                    android:textAllCaps="false" android:textSize="14sp" android:text="@string/refresh" app:cornerRadius="14dp" />
                <Button android:id="@+id/deleteBtn" android:layout_width="0dp" android:layout_height="46dp"
                    android:layout_weight="1" android:layout_marginStart="10dp" android:insetTop="0dp" android:insetBottom="0dp"
                    android:backgroundTint="@color/offex_red_soft" android:textColor="@color/offex_red"
                    android:textAllCaps="false" android:textSize="14sp" android:text="@string/delete" app:cornerRadius="14dp" />
            </LinearLayout>
        </LinearLayout>

        <TextView android:layout_width="wrap_content" android:layout_height="wrap_content"
            android:layout_marginStart="20dp" android:layout_marginTop="24dp" android:text="@string/messages"
            android:textColor="@color/offex_text" android:textSize="16sp" android:textStyle="bold" />

        <TextView android:id="@+id/emptyText" android:layout_width="match_parent" android:layout_height="wrap_content"
            android:layout_marginStart="20dp" android:layout_marginEnd="20dp" android:layout_marginTop="12dp"
            android:background="@drawable/bg_card" android:padding="18dp"
            android:text="@string/no_messages" android:textColor="@color/offex_text_dim" android:textSize="14sp" android:lineSpacingExtra="3dp" />

        <androidx.recyclerview.widget.RecyclerView android:id="@+id/msgList"
            android:layout_width="match_parent" android:layout_height="wrap_content"
            android:layout_marginStart="16dp" android:layout_marginEnd="16dp"
            android:layout_marginTop="10dp" android:nestedScrollingEnabled="false" />
    </LinearLayout>
</ScrollView>
"""

F["layout/item_message.xml"]="""<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent" android:layout_height="wrap_content"
    android:layout_marginTop="10dp" android:background="@drawable/bg_card"
    android:elevation="2dp" android:orientation="horizontal" android:padding="14dp">

    <TextView android:layout_width="44dp" android:layout_height="44dp"
        android:background="@drawable/bg_avatar" android:gravity="center"
        android:text="\u2709" android:textColor="@color/offex_white" android:textSize="18sp" />

    <LinearLayout android:layout_width="0dp" android:layout_height="wrap_content"
        android:layout_weight="1" android:layout_marginStart="12dp" android:orientation="vertical">

        <LinearLayout android:layout_width="match_parent" android:layout_height="wrap_content"
            android:orientation="horizontal" android:gravity="center_vertical">
            <TextView android:id="@+id/mSender" android:layout_width="0dp" android:layout_height="wrap_content"
                android:layout_weight="1" android:maxLines="1" android:ellipsize="end"
                android:textColor="@color/offex_text" android:textSize="14sp" android:textStyle="bold" />
            <TextView android:id="@+id/mTime" android:layout_width="wrap_content" android:layout_height="wrap_content"
                android:layout_marginStart="8dp" android:textColor="@color/offex_text_dim" android:textSize="11sp" />
        </LinearLayout>

        <TextView android:id="@+id/mSubject" android:layout_width="match_parent" android:layout_height="wrap_content"
            android:layout_marginTop="3dp" android:maxLines="2" android:ellipsize="end"
            android:textColor="@color/offex_text_dim" android:textSize="13sp" />

        <LinearLayout android:layout_width="match_parent" android:layout_height="wrap_content"
            android:layout_marginTop="8dp" android:orientation="horizontal" android:gravity="center_vertical">
            <TextView android:id="@+id/mService" android:layout_width="wrap_content" android:layout_height="wrap_content"
                android:background="@drawable/bg_chip" android:paddingStart="10dp" android:paddingEnd="10dp"
                android:paddingTop="3dp" android:paddingBottom="3dp"
                android:textColor="@color/offex_purple_dark" android:textSize="10sp" android:textStyle="bold" android:text="MAIL" />
            <TextView android:id="@+id/mOtp" android:layout_width="wrap_content" android:layout_height="wrap_content"
                android:layout_marginStart="8dp" android:background="@drawable/bg_chip_green"
                android:paddingStart="10dp" android:paddingEnd="10dp" android:paddingTop="3dp" android:paddingBottom="3dp"
                android:textColor="@color/offex_green" android:textSize="12sp" android:textStyle="bold" android:visibility="gone" />
        </LinearLayout>
    </LinearLayout>
</LinearLayout>
"""

F["layout/activity_onboarding.xml"]="""<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent" android:layout_height="match_parent"
    android:orientation="vertical" android:background="@color/offex_bg"
    android:gravity="center" android:padding="30dp">

    <TextView android:layout_width="118dp" android:layout_height="118dp"
        android:background="@drawable/bg_avatar" android:gravity="center" android:elevation="8dp"
        android:text="\u2709" android:textColor="@color/offex_white" android:textSize="52sp" />

    <TextView android:id="@+id/obTitle" android:layout_width="match_parent"
        android:layout_height="wrap_content" android:layout_marginTop="32dp" android:gravity="center"
        android:textColor="@color/offex_text" android:textSize="25sp" android:textStyle="bold" />

    <TextView android:id="@+id/obBody" android:layout_width="match_parent"
        android:layout_height="wrap_content" android:layout_marginTop="14dp" android:gravity="center"
        android:textColor="@color/offex_text_dim" android:textSize="15sp" android:lineSpacingExtra="5dp" />

    <TextView android:id="@+id/obDots" android:layout_width="wrap_content"
        android:layout_height="wrap_content" android:layout_marginTop="28dp"
        android:textColor="@color/offex_purple" android:textSize="15sp" />

    <Button android:id="@+id/obNext" android:layout_width="match_parent" android:layout_height="54dp"
        android:layout_marginTop="28dp" android:insetTop="0dp" android:insetBottom="0dp"
        android:backgroundTint="@color/offex_purple" android:textColor="@color/offex_white"
        android:textAllCaps="false" android:textSize="16sp" android:textStyle="bold" />

    <Button android:id="@+id/obSkip" android:layout_width="wrap_content" android:layout_height="wrap_content"
        android:layout_marginTop="6dp" android:background="@android:color/transparent"
        android:textColor="@color/offex_text_dim" android:textAllCaps="false" android:text="@string/ob_skip" />
</LinearLayout>
"""

F["layout/activity_reader.xml"]="""<?xml version="1.0" encoding="utf-8"?>
<ScrollView xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent" android:layout_height="match_parent" android:background="@color/offex_bg">
    <LinearLayout android:layout_width="match_parent" android:layout_height="wrap_content"
        android:orientation="vertical" android:padding="18dp">
        <LinearLayout android:layout_width="match_parent" android:layout_height="wrap_content"
            android:background="@drawable/bg_card" android:elevation="3dp"
            android:orientation="vertical" android:padding="18dp">
            <TextView android:id="@+id/rSubject" android:layout_width="match_parent" android:layout_height="wrap_content"
                android:textColor="@color/offex_text" android:textSize="19sp" android:textStyle="bold" />
            <TextView android:id="@+id/rFrom" android:layout_width="match_parent" android:layout_height="wrap_content"
                android:layout_marginTop="8dp" android:background="@drawable/bg_chip"
                android:paddingStart="12dp" android:paddingEnd="12dp" android:paddingTop="5dp" android:paddingBottom="5dp"
                android:textColor="@color/offex_purple_dark" android:textSize="12sp" />
        </LinearLayout>
        <LinearLayout android:layout_width="match_parent" android:layout_height="wrap_content"
            android:layout_marginTop="14dp" android:background="@drawable/bg_card" android:elevation="3dp"
            android:orientation="vertical" android:padding="18dp">
            <TextView android:id="@+id/rBody" android:layout_width="match_parent" android:layout_height="wrap_content"
                android:textColor="@color/offex_text" android:textSize="15sp" android:lineSpacingExtra="5dp" />
        </LinearLayout>
    </LinearLayout>
</ScrollView>
"""

F["layout/activity_admin.xml"]="""<?xml version="1.0" encoding="utf-8"?>
<ScrollView xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent" android:layout_height="match_parent" android:background="@color/offex_bg">
    <LinearLayout android:layout_width="match_parent" android:layout_height="wrap_content"
        android:orientation="vertical" android:padding="18dp">
        <TextView android:layout_width="wrap_content" android:layout_height="wrap_content"
            android:text="@string/admin" android:textColor="@color/offex_text" android:textSize="22sp" android:textStyle="bold" />
        <EditText android:id="@+id/codeBox" android:layout_width="match_parent" android:layout_height="52dp"
            android:layout_marginTop="16dp" android:background="@drawable/bg_input" android:hint="@string/admin_hint"
            android:inputType="textPassword" android:paddingStart="16dp" android:paddingEnd="16dp"
            android:textColorHint="@color/offex_text_dim" android:textColor="@color/offex_text" />
        <Button android:id="@+id/unlockBtn" android:layout_width="match_parent" android:layout_height="52dp"
            android:layout_marginTop="12dp" android:insetTop="0dp" android:insetBottom="0dp"
            android:backgroundTint="@color/offex_purple" android:textColor="@color/offex_white"
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
print("E premium:",len(F))
