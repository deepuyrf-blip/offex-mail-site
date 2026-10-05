import os
R="android/app/src/main/res/layout"
os.makedirs(R,exist_ok=True)
F={}
F["activity_onboarding.xml"]="""<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent" android:layout_height="match_parent"
    android:orientation="vertical" android:background="@color/offex_bg"
    android:gravity="center" android:padding="28dp">
    <TextView android:layout_width="110dp" android:layout_height="110dp"
        android:background="@color/offex_purple" android:gravity="center"
        android:text="\u2709" android:textColor="@color/offex_white" android:textSize="48sp" />
    <TextView android:id="@+id/obTitle" android:layout_width="match_parent"
        android:layout_height="wrap_content" android:layout_marginTop="26dp" android:gravity="center"
        android:textColor="@color/offex_text" android:textSize="23sp" android:textStyle="bold" />
    <TextView android:id="@+id/obBody" android:layout_width="match_parent"
        android:layout_height="wrap_content" android:layout_marginTop="12dp" android:gravity="center"
        android:textColor="@color/offex_text_dim" android:textSize="15sp" android:lineSpacingExtra="4dp" />
    <TextView android:id="@+id/obDots" android:layout_width="wrap_content"
        android:layout_height="wrap_content" android:layout_marginTop="22dp"
        android:textColor="@color/offex_purple" android:textSize="16sp" />
    <Button android:id="@+id/obNext" android:layout_width="match_parent" android:layout_height="52dp"
        android:layout_marginTop="24dp" android:backgroundTint="@color/offex_purple"
        android:textColor="@color/offex_white" android:textAllCaps="false" android:textSize="16sp" />
    <Button android:id="@+id/obSkip" android:layout_width="wrap_content" android:layout_height="wrap_content"
        android:layout_marginTop="6dp" android:background="@android:color/transparent"
        android:textColor="@color/offex_text_dim" android:textAllCaps="false" android:text="@string/ob_skip" />
</LinearLayout>
"""
F["activity_main.xml"]="""<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent" android:layout_height="match_parent"
    android:orientation="vertical" android:background="@color/offex_bg">
    <LinearLayout android:layout_width="match_parent" android:layout_height="wrap_content"
        android:background="@color/offex_purple" android:orientation="horizontal"
        android:gravity="center_vertical" android:padding="16dp">
        <TextView android:layout_width="0dp" android:layout_height="wrap_content" android:layout_weight="1"
            android:text="@string/app_name" android:textColor="@color/offex_white"
            android:textSize="20sp" android:textStyle="bold" />
        <Button android:id="@+id/settingsBtn" android:layout_width="wrap_content" android:layout_height="40dp"
            android:background="@android:color/transparent" android:text="\u2699"
            android:textColor="@color/offex_white" android:textSize="18sp" />
    </LinearLayout>
    <ScrollView android:layout_width="match_parent" android:layout_height="match_parent">
        <LinearLayout android:layout_width="match_parent" android:layout_height="wrap_content"
            android:orientation="vertical" android:padding="16dp">
            <TextView android:layout_width="wrap_content" android:layout_height="wrap_content"
                android:text="@string/new_inbox" android:textColor="@color/offex_text"
                android:textSize="15sp" android:textStyle="bold" />
            <EditText android:id="@+id/nameBox" android:layout_width="match_parent" android:layout_height="50dp"
                android:layout_marginTop="8dp" android:background="@color/offex_card"
                android:hint="@string/hint_name" android:inputType="text"
                android:paddingStart="14dp" android:paddingEnd="14dp"
                android:textColorHint="@color/offex_text_dim" android:textColor="@color/offex_text" />
            <Spinner android:id="@+id/domainBox" android:layout_width="match_parent"
                android:layout_height="50dp" android:layout_marginTop="8dp" android:background="@color/offex_card" />
            <Button android:id="@+id/createBtn" android:layout_width="match_parent" android:layout_height="52dp"
                android:layout_marginTop="10dp" android:backgroundTint="@color/offex_purple"
                android:textColor="@color/offex_white" android:textAllCaps="false"
                android:textSize="16sp" android:text="@string/create_inbox" />
            <LinearLayout android:id="@+id/activeCard" android:layout_width="match_parent"
                android:layout_height="wrap_content" android:layout_marginTop="16dp"
                android:background="@color/offex_card" android:orientation="vertical"
                android:padding="16dp" android:visibility="gone">
                <TextView android:layout_width="wrap_content" android:layout_height="wrap_content"
                    android:text="@string/your_address" android:textColor="@color/offex_text_dim" android:textSize="12sp" />
                <TextView android:id="@+id/addrText" android:layout_width="match_parent" android:layout_height="wrap_content"
                    android:layout_marginTop="4dp" android:textColor="@color/offex_text"
                    android:textSize="18sp" android:textStyle="bold" android:textIsSelectable="true" />
                <TextView android:id="@+id/countdownText" android:layout_width="match_parent"
                    android:layout_height="wrap_content" android:layout_marginTop="4dp"
                    android:textColor="@color/offex_text_dim" android:textSize="12sp" />
                <LinearLayout android:layout_width="match_parent" android:layout_height="wrap_content"
                    android:layout_marginTop="10dp" android:orientation="horizontal">
                    <Button android:id="@+id/copyBtn" android:layout_width="0dp" android:layout_height="44dp"
                        android:layout_weight="1" android:backgroundTint="@color/offex_purple"
                        android:textColor="@color/offex_white" android:textAllCaps="false" android:text="@string/copy" />
                    <Button android:id="@+id/refreshBtn" android:layout_width="0dp" android:layout_height="44dp"
                        android:layout_weight="1" android:layout_marginStart="8dp"
                        android:backgroundTint="@color/offex_purple_dark" android:textColor="@color/offex_white"
                        android:textAllCaps="false" android:text="@string/refresh" />
                    <Button android:id="@+id/deleteBtn" android:layout_width="0dp" android:layout_height="44dp"
                        android:layout_weight="1" android:layout_marginStart="8dp"
                        android:backgroundTint="@color/offex_red" android:textColor="@color/offex_white"
                        android:textAllCaps="false" android:text="@string/delete" />
                </LinearLayout>
            </LinearLayout>
            <TextView android:layout_width="wrap_content" android:layout_height="wrap_content"
                android:layout_marginTop="20dp" android:text="@string/messages"
                android:textColor="@color/offex_text" android:textSize="15sp" android:textStyle="bold" />
            <TextView android:id="@+id/emptyText" android:layout_width="match_parent" android:layout_height="wrap_content"
                android:layout_marginTop="10dp" android:text="@string/no_messages"
                android:textColor="@color/offex_text_dim" android:textSize="14sp" />
            <androidx.recyclerview.widget.RecyclerView android:id="@+id/msgList"
                android:layout_width="match_parent" android:layout_height="wrap_content"
                android:layout_marginTop="6dp" android:nestedScrollingEnabled="false" />
        </LinearLayout>
    </ScrollView>
</LinearLayout>
"""
F["item_message.xml"]="""<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent" android:layout_height="wrap_content"
    android:layout_marginTop="8dp" android:background="@color/offex_card"
    android:orientation="vertical" android:padding="14dp">
    <LinearLayout android:layout_width="match_parent" android:layout_height="wrap_content"
        android:orientation="horizontal" android:gravity="center_vertical">
        <TextView android:id="@+id/mService" android:layout_width="wrap_content" android:layout_height="wrap_content"
            android:background="@color/offex_purple" android:paddingStart="8dp" android:paddingEnd="8dp"
            android:paddingTop="2dp" android:paddingBottom="2dp" android:textColor="@color/offex_white"
            android:textSize="10sp" android:textStyle="bold" android:text="MAIL" />
        <TextView android:id="@+id/mTime" android:layout_width="0dp" android:layout_height="wrap_content"
            android:layout_weight="1" android:gravity="end" android:textColor="@color/offex_text_dim" android:textSize="11sp" />
    </LinearLayout>
    <TextView android:id="@+id/mSender" android:layout_width="match_parent" android:layout_height="wrap_content"
        android:layout_marginTop="6dp" android:textColor="@color/offex_text" android:textSize="14sp" android:textStyle="bold" />
    <TextView android:id="@+id/mSubject" android:layout_width="match_parent" android:layout_height="wrap_content"
        android:layout_marginTop="2dp" android:textColor="@color/offex_text_dim" android:textSize="13sp" />
    <TextView android:id="@+id/mOtp" android:layout_width="wrap_content" android:layout_height="wrap_content"
        android:layout_marginTop="8dp" android:background="@color/offex_green" android:paddingStart="12dp"
        android:paddingEnd="12dp" android:paddingTop="4dp" android:paddingBottom="4dp"
        android:textColor="@color/offex_white" android:textSize="16sp" android:textStyle="bold" android:visibility="gone" />
</LinearLayout>
"""
F["activity_reader.xml"]="""<?xml version="1.0" encoding="utf-8"?>
<ScrollView xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent" android:layout_height="match_parent" android:background="@color/offex_bg">
    <LinearLayout android:layout_width="match_parent" android:layout_height="wrap_content"
        android:orientation="vertical" android:padding="18dp">
        <TextView android:id="@+id/rSubject" android:layout_width="match_parent" android:layout_height="wrap_content"
            android:textColor="@color/offex_text" android:textSize="20sp" android:textStyle="bold" />
        <TextView android:id="@+id/rFrom" android:layout_width="match_parent" android:layout_height="wrap_content"
            android:layout_marginTop="6dp" android:textColor="@color/offex_text_dim" android:textSize="13sp" />
        <View android:layout_width="match_parent" android:layout_height="1dp"
            android:layout_marginTop="12dp" android:background="#E3E5EF" />
        <TextView android:id="@+id/rBody" android:layout_width="match_parent" android:layout_height="wrap_content"
            android:layout_marginTop="12dp" android:textColor="@color/offex_text"
            android:textSize="15sp" android:lineSpacingExtra="4dp" />
    </LinearLayout>
</ScrollView>
"""
F["activity_admin.xml"]="""<?xml version="1.0" encoding="utf-8"?>
<ScrollView xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent" android:layout_height="match_parent" android:background="@color/offex_bg">
    <LinearLayout android:layout_width="match_parent" android:layout_height="wrap_content"
        android:orientation="vertical" android:padding="18dp">
        <TextView android:layout_width="wrap_content" android:layout_height="wrap_content"
            android:text="@string/admin" android:textColor="@color/offex_text" android:textSize="20sp" android:textStyle="bold" />
        <EditText android:id="@+id/codeBox" android:layout_width="match_parent" android:layout_height="50dp"
            android:layout_marginTop="12dp" android:background="@color/offex_card" android:hint="@string/admin_hint"
            android:inputType="textPassword" android:paddingStart="14dp" android:paddingEnd="14dp"
            android:textColorHint="@color/offex_text_dim" android:textColor="@color/offex_text" />
        <Button android:id="@+id/unlockBtn" android:layout_width="match_parent" android:layout_height="50dp"
            android:layout_marginTop="10dp" android:backgroundTint="@color/offex_purple"
            android:textColor="@color/offex_white" android:textAllCaps="false" android:text="@string/unlock" />
        <LinearLayout android:id="@+id/panel" android:layout_width="match_parent" android:layout_height="wrap_content"
            android:layout_marginTop="18dp" android:background="@color/offex_card" android:orientation="vertical"
            android:padding="16dp" android:visibility="gone">
            <Switch android:id="@+id/notifySwitch" android:layout_width="match_parent" android:layout_height="wrap_content"
                android:text="@string/notif_on" android:textColor="@color/offex_text" />
            <TextView android:id="@+id/versionText" android:layout_width="match_parent" android:layout_height="wrap_content"
                android:layout_marginTop="12dp" android:textColor="@color/offex_text_dim" android:textSize="13sp" />
        </LinearLayout>
    </LinearLayout>
</ScrollView>
"""
for n,c in F.items(): open(R+"/"+n,"w",encoding="utf-8").write(c)
print("D layouts:",len(F))
