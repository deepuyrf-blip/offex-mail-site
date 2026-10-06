import os
J="android/app/src/main/java/online/mytempmail/app"
os.makedirs(J,exist_ok=True)
MENU = """package online.mytempmail.app;
import android.app.Activity;
import android.app.AlertDialog;
import android.content.Intent;
import android.widget.Toast;
public class Menu {
    public static void open(final Activity a){
        final String notif = "Notifications: " + (Prefs.notifyOn() ? "ON" : "OFF");
        final String[] items = {"About Offex Mail", "Contact us", notif};
        new AlertDialog.Builder(a)
            .setTitle("More")
            .setItems(items, (d,w)->{
                try {
                    if(w==0) a.startActivity(new Intent(a, AboutActivity.class));
                    else if(w==1) a.startActivity(new Intent(a, ContactActivity.class));
                    else {
                        Prefs.setNotify(!Prefs.notifyOn());
                        if(Prefs.notifyOn()) Notifier.ensure(a);
                        Toast.makeText(a, "Notifications " + (Prefs.notifyOn() ? "ON" : "OFF"), Toast.LENGTH_SHORT).show();
                    }
                } catch(Exception e){}
            })
            .setNegativeButton("Close", (d,w)->{})
            .show();
    }
}
"""
open(J+"/Menu.java","w",encoding="utf-8").write(MENU)
print("P Menu written (admin removed)", len(MENU))
