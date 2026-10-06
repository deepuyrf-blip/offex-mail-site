import os, re
# ---------------------------------------------------------------------------
# gn_q.py  (runs LAST in the android.yml pipeline)
#
# This step applies the v3.3 app fixes on top of the project emitted by
# gn_a..gn_p. It is intentionally the final writer of the files it touches:
#
#   1. New-mail notifications now actually fire  (Notifier / MailService /
#      MainActivity trigger logic + separate low-importance service channel).
#   2. Message body renders as clean readable text (style/script/head/comment/
#      img stripping before Html.fromHtml, entity decode, link handling).
#   3. One-tap "Copy code" card for OTPs in the message reader.
#   4. Verification links open in the browser (clickable URLSpan + Linkify).
#   5. UI restyled to the reference screens (red accent, light theme) with a
#      new "Why Offex Mail" features section on the home screen.
#
# API endpoints, JSON field names and the admin-panel-controlled features
# (announcement banner, AdMob banner + rewarded ads, push notifications,
# update prompt) are preserved exactly.
# ---------------------------------------------------------------------------

J   = "android/app/src/main/java/online/mytempmail/app"
RES = "android/app/src/main/res"

def W(p, c):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w", encoding="utf-8").write(c)

def R(p):
    return open(p, encoding="utf-8").read()

# ===========================================================================
# 1 + 2 + 4 : Notifier  (channels + real mail alerts)
# ===========================================================================
NOTIFIER = r'''package online.mytempmail.app;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.content.Context;
import android.content.Intent;
import android.media.AudioAttributes;
import android.media.RingtoneManager;
import android.os.Build;
import androidx.core.app.NotificationCompat;
import androidx.core.app.NotificationManagerCompat;
public class Notifier {
    public static final String CH = "offex_mail";            // new-mail alerts (high importance)
    public static final String CH_SERVICE = "offex_service"; // background sync (low importance)
    private static void channels(Context c){
        if(Build.VERSION.SDK_INT>=Build.VERSION_CODES.O){
            NotificationManager nm=c.getSystemService(NotificationManager.class);
            if(nm==null) return;
            NotificationChannel mail=new NotificationChannel(CH,c.getString(R.string.notif_channel),NotificationManager.IMPORTANCE_HIGH);
            mail.enableVibration(true);
            mail.setSound(RingtoneManager.getDefaultUri(RingtoneManager.TYPE_NOTIFICATION),
                new AudioAttributes.Builder().setUsage(AudioAttributes.USAGE_NOTIFICATION).build());
            nm.createNotificationChannel(mail);
            NotificationChannel svc=new NotificationChannel(CH_SERVICE,c.getString(R.string.notif_service),NotificationManager.IMPORTANCE_LOW);
            svc.setShowBadge(false);
            nm.createNotificationChannel(svc);
        }
    }
    public static void ensure(Context c){ try { channels(c); } catch(Exception e){} }
    public static boolean enabled(Context c){
        try { return NotificationManagerCompat.from(c).areNotificationsEnabled(); } catch(Exception e){ return true; }
    }
    public static void mail(Context c,String from,String subject){
        if(!Prefs.notifyOn()) return;
        try {
            ensure(c);
            if(!enabled(c)) return;
            String title=(from==null||from.trim().isEmpty())?c.getString(R.string.app_name):from.trim();
            String text=(subject==null)?"":subject;
            Intent open=new Intent(c,MainActivity.class);
            open.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK|Intent.FLAG_ACTIVITY_CLEAR_TOP);
            int flags=PendingIntent.FLAG_UPDATE_CURRENT;
            if(Build.VERSION.SDK_INT>=23) flags|=PendingIntent.FLAG_IMMUTABLE;
            PendingIntent content=PendingIntent.getActivity(c,0,open,flags);
            NotificationCompat.Builder b=new NotificationCompat.Builder(c,CH)
                .setSmallIcon(R.mipmap.ic_launcher)
                .setContentTitle(title)
                .setContentText(text)
                .setStyle(new NotificationCompat.BigTextStyle().bigText(text))
                .setContentIntent(content)
                .setAutoCancel(true)
                .setOnlyAlertOnce(false)
                .setDefaults(NotificationCompat.DEFAULT_ALL)
                .setSound(RingtoneManager.getDefaultUri(RingtoneManager.TYPE_NOTIFICATION))
                .setPriority(NotificationCompat.PRIORITY_HIGH)
                .setCategory(NotificationCompat.CATEGORY_MESSAGE);
            int id=(int)(System.currentTimeMillis()%100000)+1001;
            NotificationManagerCompat.from(c).notify(id,b.build());
        } catch(SecurityException e){}
        catch(Exception e){}
    }
}
'''

# ===========================================================================
# 1 : MailService  (foreground sync + reliable new-mail detection)
# ===========================================================================
MAILSERVICE = r'''package online.mytempmail.app;
import android.app.Notification;
import android.app.Service;
import android.content.Intent;
import android.os.Handler;
import android.os.IBinder;
import android.os.Looper;
import androidx.core.app.NotificationCompat;
import org.json.JSONArray;
import org.json.JSONObject;
public class MailService extends Service {
    private static final long MAIL_MS = 20000L;
    private static final long CONFIG_MS = 180000L;
    private final Handler h=new Handler(Looper.getMainLooper());
    private Runnable task;
    private long lastConfig=0;
    @Override public int onStartCommand(Intent i,int f,int s){
        Notifier.ensure(this);
        Notification n=new NotificationCompat.Builder(this,Notifier.CH_SERVICE)
            .setSmallIcon(R.mipmap.ic_launcher)
            .setContentTitle("Offex Mail")
            .setContentText("Watching your inbox for new mail")
            .setOngoing(true).setPriority(NotificationCompat.PRIORITY_MIN).build();
        try { startForeground(2,n); } catch(Exception e){}
        if(task==null){
            task=new Runnable(){ @Override public void run(){ tick(); h.postDelayed(this,MAIL_MS); } };
            h.postDelayed(task,4000);
        }
        return START_STICKY;
    }
    private void tick(){
        new Thread(()->{
            try {
                long now=System.currentTimeMillis();
                if(now-lastConfig>CONFIG_MS){ lastConfig=now; Config.refresh(); Config.push(this); }
            } catch(Exception e){}
            final String addr=Prefs.address();
            if(addr==null||addr.isEmpty()) return;
            try {
                JSONArray a=new JSONObject(ApiClient.get("/api/inbox/"+addr+"/messages")).optJSONArray("messages");
                if(a==null) return;
                int max=0; JSONObject top=null;
                for(int k=0;k<a.length();k++){ JSONObject o=a.getJSONObject(k); int id=o.optInt("id"); if(id>max){ max=id; top=o; } }
                int last=Prefs.lastMsgId();
                if(last<0){ Prefs.setLastMsgId(max); }                     // first sync: baseline, no alert
                else if(max>last){                                          // a genuinely new message
                    if(top!=null) Notifier.mail(this,top.optString("sender"),top.optString("subject"));
                    Prefs.setLastMsgId(max);
                }
            } catch(Exception e){}
        }).start();
    }
    @Override public IBinder onBind(Intent i){ return null; }
}
'''

# ===========================================================================
# 1 : MainActivity  (baseline tracking so the first mail still notifies,
#                     permission request, always-on service)
# ===========================================================================
MAIN = r'''package online.mytempmail.app;
import android.app.Activity;
import android.content.ClipData;
import android.content.ClipboardManager;
import android.content.Context;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.graphics.Color;
import android.graphics.Typeface;
import android.os.Build;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.view.Gravity;
import android.view.View;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.Spinner;
import android.widget.TextView;
import android.widget.Toast;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;
import org.json.JSONArray;
import org.json.JSONObject;
import java.util.ArrayList;
import java.util.List;
public class MainActivity extends Activity {
    private final Handler ui=new Handler(Looper.getMainLooper());
    private final Handler poll=new Handler(Looper.getMainLooper());
    private EditText nameBox; private Spinner domainBox; private Button createBtn;
    private LinearLayout activeCard, historyBox; private TextView addrText,countdownText,emptyText,historyEmpty,inboxAddr;
    private ScrollView rootScroll; private RecyclerView msgList;
    private MailAdapter adapter; private final List<Mail> mails=new ArrayList<>();
    private final List<String> domains=new ArrayList<>();
    private Runnable pollTask;
    @Override protected void onCreate(Bundle b){
        super.onCreate(b);
        Skin.apply(this);
        if(!Prefs.onboarded()){ startActivity(new Intent(this,OnboardingActivity.class)); finish(); return; }
        setContentView(R.layout.activity_main);
        Config.apply(this);
        askNotify();
        rootScroll=findViewById(R.id.rootScroll);
        nameBox=findViewById(R.id.nameBox); domainBox=findViewById(R.id.domainBox); createBtn=findViewById(R.id.createBtn);
        activeCard=findViewById(R.id.activeCard); addrText=findViewById(R.id.addrText);
        countdownText=findViewById(R.id.countdownText); emptyText=findViewById(R.id.emptyText);
        historyBox=findViewById(R.id.historyBox); historyEmpty=findViewById(R.id.historyEmpty);
        inboxAddr=findViewById(R.id.inboxAddr);
        msgList=findViewById(R.id.msgList);
        RecyclerView list=msgList;
        list.setLayoutManager(new LinearLayoutManager(this));
        adapter=new MailAdapter(mails,this::openMail);
        list.setAdapter(adapter);
        domains.add("Random (auto)");
        domainBox.setAdapter(new ArrayAdapter<>(this,android.R.layout.simple_spinner_dropdown_item,domains));
        createBtn.setOnClickListener(v->Ads.rewarded(this, ()->createInbox()));
        findViewById(R.id.copyBtn).setOnClickListener(v->copyAddr());
        findViewById(R.id.refreshBtn).setOnClickListener(v->loadMessages());
        findViewById(R.id.deleteBtn).setOnClickListener(v->deleteActive());
        findViewById(R.id.settingsBtn).setOnClickListener(v->Menu.open(this));
        loadDomains();
        renderHistory();
        wireNav();
        if(!Prefs.address().isEmpty()){ activeCard.setVisibility(View.VISIBLE); addrText.setText(Prefs.address()); loadMessages(); startPolling(); startService(); }
    }
    private void askNotify(){
        try {
            if(Build.VERSION.SDK_INT>=33 && checkSelfPermission("android.permission.POST_NOTIFICATIONS")!=PackageManager.PERMISSION_GRANTED){
                requestPermissions(new String[]{"android.permission.POST_NOTIFICATIONS"},77);
            }
        } catch(Exception e){}
    }
    private void wireNav(){
        final View[] items={findViewById(R.id.navEmail),findViewById(R.id.navInbox),findViewById(R.id.navSwitch),findViewById(R.id.navMore)};
        final View[] inds={findViewById(R.id.navIndEmail),findViewById(R.id.navIndInbox),findViewById(R.id.navIndSwitch),findViewById(R.id.navIndMore)};
        final TextView[] icons={findViewById(R.id.navIconEmail),findViewById(R.id.navIconInbox),findViewById(R.id.navIconSwitch),findViewById(R.id.navIconMore)};
        for(int i=0;i<items.length;i++){
            final int idx=i;
            if(items[i]!=null) items[i].setOnClickListener(v->{ selectNav(idx,inds,icons); navAction(idx); });
        }
        selectNav(0,inds,icons);
    }
    private void selectNav(int idx,View[] inds,TextView[] icons){
        for(int i=0;i<inds.length;i++){
            final View ind=inds[i];
            if(ind==null) continue;
            if(i==idx){
                ind.setVisibility(View.VISIBLE); ind.setAlpha(0f);
                ind.animate().alpha(1f).setDuration(220).start();
            } else {
                ind.animate().alpha(0f).setDuration(120).withEndAction(()->ind.setVisibility(View.INVISIBLE)).start();
            }
            if(icons[i]!=null){
                icons[i].setTextColor(i==idx?0xFFE53935:0xFF8A87A0);
                icons[i].animate().scaleX(i==idx?1.12f:1f).scaleY(i==idx?1.12f:1f).setDuration(170).start();
            }
        }
    }
    private void navAction(int idx){
        try {
            if(idx==0){ if(rootScroll!=null) rootScroll.smoothScrollTo(0,0); }
            else if(idx==1){ if(rootScroll!=null&&msgList!=null) rootScroll.smoothScrollTo(0,Math.max(0,msgList.getTop()-24)); }
            else if(idx==2){ if(rootScroll!=null&&historyBox!=null) rootScroll.smoothScrollTo(0,Math.max(0,historyBox.getTop()-24)); }
            else { Menu.open(this); }
        } catch(Exception e){}
    }
    private int resolveText(){
        try { android.util.TypedValue tv=new android.util.TypedValue();
            getTheme().resolveAttribute(R.attr.oxText,tv,true); return tv.data; } catch(Exception e){ return 0xFF1B1730; }
    }
    private void loadDomains(){
        new Thread(()->{
            try {
                JSONArray a=new JSONObject(ApiClient.get("/api/status")).optJSONArray("domains");
                if(a!=null){ for(int i=0;i<a.length();i++) domains.add(a.getString(i));
                    ui.post(()->((ArrayAdapter<String>)domainBox.getAdapter()).notifyDataSetChanged()); }
            } catch(Exception e){}
        }).start();
    }
    private void createInbox(){
        createBtn.setEnabled(false); createBtn.setText(R.string.creating);
        final String nm=nameBox.getText().toString().trim();
        final String dm=domainBox.getSelectedItemPosition()==0?"":String.valueOf(domainBox.getSelectedItem());
        new Thread(()->{
            try {
                JSONObject body=new JSONObject(); body.put("custom",nm); body.put("domain",dm);
                JSONObject j=new JSONObject(ApiClient.post("/api/inbox",body.toString()));
                final String addr=j.getString("address");
                final long exp=j.optLong("expires_at",0L);
                addHistory(addr,exp);
                Prefs.setAddress(addr); Prefs.setExpiresAt(exp); Prefs.setLastMsgId(-1);
                ui.post(()->{
                    createBtn.setEnabled(true); createBtn.setText(R.string.create_inbox);
                    activeCard.setVisibility(View.VISIBLE); addrText.setText(addr); nameBox.setText("");
                    mails.clear(); adapter.notifyDataSetChanged();
                    Toast.makeText(this,"Inbox ready",Toast.LENGTH_SHORT).show();
                    renderHistory(); loadMessages(); startPolling(); startService();
                });
            } catch(final Exception e){
                ui.post(()->{ createBtn.setEnabled(true); createBtn.setText(R.string.create_inbox);
                    Toast.makeText(this,e.getMessage(),Toast.LENGTH_LONG).show(); });
            }
        }).start();
    }
    private void addHistory(String addr,long exp){
        try {
            JSONArray a=new JSONArray(Prefs.history());
            JSONArray out=new JSONArray();
            JSONObject o=new JSONObject(); o.put("a",addr); o.put("e",exp); out.put(o);
            for(int i=0;i<a.length();i++){ JSONObject x=a.getJSONObject(i); if(!addr.equals(x.optString("a"))&&out.length()<20) out.put(x); }
            Prefs.setHistory(out.toString());
        } catch(Exception e){}
    }
    private void removeHistory(String addr){
        try {
            JSONArray a=new JSONArray(Prefs.history()); JSONArray out=new JSONArray();
            for(int i=0;i<a.length();i++){ JSONObject x=a.getJSONObject(i); if(!addr.equals(x.optString("a"))) out.put(x); }
            Prefs.setHistory(out.toString());
        } catch(Exception e){}
    }
    private void renderHistory(){
        historyBox.removeAllViews();
        try {
            JSONArray a=new JSONArray(Prefs.history());
            historyEmpty.setVisibility(a.length()==0?View.VISIBLE:View.GONE);
            String cur=Prefs.address();
            for(int i=0;i<a.length();i++){
                final JSONObject o=a.getJSONObject(i);
                final String addr=o.optString("a");
                LinearLayout row=new LinearLayout(this);
                row.setOrientation(LinearLayout.HORIZONTAL);
                row.setGravity(Gravity.CENTER_VERTICAL);
                row.setBackgroundResource(R.drawable.bg_card);
                row.setElevation(2f);
                LinearLayout.LayoutParams lp=new LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT,LinearLayout.LayoutParams.WRAP_CONTENT);
                lp.topMargin=10; row.setLayoutParams(lp);
                row.setPadding(32,30,32,30);
                TextView t=new TextView(this);
                t.setText(addr+(addr.equals(cur)?"  \u2022 active":""));
                t.setTextSize(14); t.setTextColor(addr.equals(cur)?0xFFE53935:resolveText());
                t.setTypeface(null,Typeface.BOLD);
                LinearLayout.LayoutParams tp=new LinearLayout.LayoutParams(0,LinearLayout.LayoutParams.WRAP_CONTENT,1f);
                t.setLayoutParams(tp);
                TextView del=new TextView(this);
                del.setText("\u2715"); del.setTextSize(16); del.setTextColor(0xFFE5484D);
                del.setPadding(24,0,0,0);
                del.setOnClickListener(v->{ removeHistory(addr); if(addr.equals(Prefs.address())){ Prefs.setAddress(""); Prefs.setLastMsgId(-1); activeCard.setVisibility(View.GONE); mails.clear(); adapter.notifyDataSetChanged(); emptyText.setVisibility(View.VISIBLE); } renderHistory(); });
                row.addView(t); row.addView(del);
                row.setOnClickListener(v->{ Prefs.setAddress(addr); Prefs.setExpiresAt(o.optLong("e",0L)); Prefs.setLastMsgId(-1);
                    activeCard.setVisibility(View.VISIBLE); addrText.setText(addr); mails.clear(); adapter.notifyDataSetChanged();
                    renderHistory(); loadMessages(); startPolling(); startService(); });
                historyBox.addView(row);
            }
        } catch(Exception e){}
    }
    private void loadMessages(){
        final String addr=Prefs.address();
        if(inboxAddr!=null) inboxAddr.setText(addr);
        if(addr.isEmpty()) return;
        new Thread(()->{
            try {
                JSONArray a=new JSONObject(ApiClient.get("/api/inbox/"+addr+"/messages")).optJSONArray("messages");
                final List<Mail> fresh=new ArrayList<>(); int maxId=0; Mail top=null;
                if(a!=null) for(int i=0;i<a.length();i++){
                    JSONObject o=a.getJSONObject(i); Mail m=new Mail();
                    m.id=o.optInt("id"); m.sender=o.optString("sender"); m.subject=o.optString("subject");
                    m.receivedAt=o.optString("received_at"); m.otp=o.optString("otp"); m.service=o.optString("service");
                    fresh.add(m); if(m.id>maxId){ maxId=m.id; top=m; }
                }
                final int nm=maxId; final Mail topMail=top;
                ui.post(()->{
                    mails.clear(); mails.addAll(fresh); adapter.notifyDataSetChanged();
                    emptyText.setVisibility(mails.isEmpty()?View.VISIBLE:View.GONE);
                    int last=Prefs.lastMsgId();
                    if(last<0){ Prefs.setLastMsgId(nm); }                        // first sync: baseline, no alert
                    else if(nm>last){                                             // a genuinely new message
                        if(topMail!=null) Notifier.mail(this,topMail.sender,topMail.subject);
                        Prefs.setLastMsgId(nm);
                    }
                });
            } catch(Exception e){}
        }).start();
    }
    private void deleteActive(){
        final String addr=Prefs.address();
        if(addr.isEmpty()) return;
        new Thread(()->{
            try { ApiClient.delete("/api/inbox/"+addr); } catch(Exception e){}
            removeHistory(addr);
            Prefs.setAddress(""); Prefs.setLastMsgId(-1);
            ui.post(()->{ activeCard.setVisibility(View.GONE); mails.clear(); adapter.notifyDataSetChanged();
                if(inboxAddr!=null) inboxAddr.setText("");
                emptyText.setVisibility(View.VISIBLE); renderHistory(); Toast.makeText(this,"Inbox deleted",Toast.LENGTH_SHORT).show(); });
        }).start();
    }
    private void copyAddr(){
        String a=Prefs.address(); if(a.isEmpty()) return;
        ClipboardManager cm=(ClipboardManager)getSystemService(Context.CLIPBOARD_SERVICE);
        cm.setPrimaryClip(ClipData.newPlainText("address",a));
        Toast.makeText(this,R.string.copied,Toast.LENGTH_SHORT).show();
    }
    private void openMail(Mail m){
        Intent i=new Intent(this,ReaderActivity.class); i.putExtra("id",m.id); startActivity(i);
    }
    private void startService(){
        try { startForegroundService(new Intent(this,MailService.class)); } catch(Exception e){}
    }
    private void startPolling(){
        if(pollTask!=null) return;
        pollTask=new Runnable(){ @Override public void run(){ loadMessages(); tick(); poll.postDelayed(this,20000); } };
        poll.postDelayed(pollTask,10000);
    }
    private void tick(){
        long exp=Prefs.expiresAt();
        if(exp<=0){ countdownText.setText(""); return; }
        long left=exp-System.currentTimeMillis()/1000; if(left<0) left=0;
        countdownText.setText(getString(R.string.expires_in)+"  "+(left/3600)+"h "+((left%3600)/60)+"m "+(left%60)+"s");
    }
    @Override protected void onResume(){
        super.onResume();
        if(activeCard!=null&&activeCard.getVisibility()==View.VISIBLE){ loadMessages(); startPolling(); startService(); }
    }
}
'''

# ===========================================================================
# 2 + 3 + 4 : ReaderActivity  (clean render, OTP copy, browser links)
# ===========================================================================
READER = r'''package online.mytempmail.app;
import android.app.Activity;
import android.content.ClipData;
import android.content.ClipboardManager;
import android.content.Context;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.text.Html;
import android.text.Spanned;
import android.text.method.LinkMovementMethod;
import android.text.util.Linkify;
import android.view.View;
import android.widget.TextView;
import android.widget.Toast;
import org.json.JSONObject;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
public class ReaderActivity extends Activity {
    private static final Pattern OTP=Pattern.compile("(?<!\\d)(\\d{4,8})(?!\\d)");
    @Override protected void onCreate(Bundle b){
        super.onCreate(b);
        Skin.apply(this);
        setContentView(R.layout.activity_reader);
        findViewById(R.id.readerBack).setOnClickListener(v->finish());
        final int id=getIntent().getIntExtra("id",0);
        final TextView subject=findViewById(R.id.rSubject), from=findViewById(R.id.rFrom), bodyBox=findViewById(R.id.rBody);
        final TextView avatar=findViewById(R.id.rAvatar);
        final View otpCard=findViewById(R.id.otpCard);
        final TextView otpValue=findViewById(R.id.otpValue);
        final TextView copyCode=findViewById(R.id.copyCodeBtn);
        final Handler ui=new Handler(Looper.getMainLooper());
        new Thread(()->{
            try {
                JSONObject j=new JSONObject(ApiClient.get("/api/message/"+id));
                final String s=j.optString("subject"), f=j.optString("sender"), html=j.optString("html"), txt=j.optString("body");
                final String apiOtp=j.optString("otp","");
                final CharSequence body=render(html,txt);
                String found=!apiOtp.trim().isEmpty()?apiOtp.trim():findOtp(html,txt);
                final String otp=found;
                ui.post(()->{
                    subject.setText(s);
                    from.setText(f);
                    if(avatar!=null&&f!=null&&!f.isEmpty()) avatar.setText(f.substring(0,1).toUpperCase());
                    bodyBox.setText(body);
                    bodyBox.setMovementMethod(LinkMovementMethod.getInstance());
                    bodyBox.setLinksClickable(true);
                    try { Linkify.addLinks(bodyBox,Linkify.WEB_URLS); } catch(Exception e){}
                    if(otp!=null&&!otp.isEmpty()&&otpCard!=null){
                        otpValue.setText(otp);
                        otpCard.setVisibility(View.VISIBLE);
                        copyCode.setOnClickListener(v->copyCode(otp));
                    }
                });
            } catch(final Exception e){
                ui.post(()->Toast.makeText(this,e.getMessage(),Toast.LENGTH_LONG).show());
            }
        }).start();
    }
    private void copyCode(String code){
        try {
            ClipboardManager cm=(ClipboardManager)getSystemService(Context.CLIPBOARD_SERVICE);
            cm.setPrimaryClip(ClipData.newPlainText("code",code));
            Toast.makeText(this,R.string.code_copied,Toast.LENGTH_SHORT).show();
        } catch(Exception e){}
    }
    private static String findOtp(String html,String txt){
        try {
            String plain=strip(html==null?"":html);
            String src=(plain!=null&&!plain.trim().isEmpty())?plain:(txt==null?"":txt);
            Matcher m=OTP.matcher(src);
            String first=null;
            while(m.find()){
                String c=m.group(1);
                if(first==null) first=c;
                int st=Math.max(0,m.start()-40);
                String ctx=src.substring(st,m.start()).toLowerCase();
                if(ctx.contains("code")||ctx.contains("otp")||ctx.contains("pin")||ctx.contains("verif")) return c;
            }
            return first;
        } catch(Exception e){ return null; }
    }
    private static String strip(String h){
        if(h==null) return "";
        String s=h;
        s=s.replaceAll("(?is)<script[^>]*>.*?</script>"," ");
        s=s.replaceAll("(?is)<style[^>]*>.*?</style>"," ");
        s=s.replaceAll("(?is)<head[^>]*>.*?</head>"," ");
        s=s.replaceAll("(?is)<title[^>]*>.*?</title>"," ");
        s=s.replaceAll("(?is)<!--.*?-->"," ");
        s=s.replaceAll("(?is)<br\\s*/?>","\n");
        s=s.replaceAll("(?is)</(p|div|tr|li|h[1-6]|table|section|article)>","\n");
        s=s.replaceAll("(?is)<[^>]+>"," ");
        s=s.replace("&nbsp;"," ").replace("&amp;","&").replace("&lt;","<").replace("&gt;",">").replace("&quot;","\"").replace("&#39;","'");
        s=s.replaceAll("[ \\t\\x0B\\f\\r]+"," ");
        s=s.replaceAll("\\n\\s*\\n\\s*\\n+","\n\n");
        s=s.replaceAll("(?m)^[ \\t]+","");
        return s.trim();
    }
    private static CharSequence render(String html,String txt){
        try {
            String h=html==null?"":html;
            if(!h.trim().isEmpty()){
                String cleaned=h;
                cleaned=cleaned.replaceAll("(?is)<script[^>]*>.*?</script>"," ");
                cleaned=cleaned.replaceAll("(?is)<style[^>]*>.*?</style>"," ");
                cleaned=cleaned.replaceAll("(?is)<head[^>]*>.*?</head>"," ");
                cleaned=cleaned.replaceAll("(?is)<title[^>]*>.*?</title>"," ");
                cleaned=cleaned.replaceAll("(?is)<!--.*?-->"," ");
                cleaned=cleaned.replaceAll("(?is)<(link|meta|svg|img|iframe|object|embed|video|audio|source|base)[^>]*>"," ");
                Spanned sp=Html.fromHtml(cleaned,Html.FROM_HTML_MODE_LEGACY);
                String plain=sp.toString().replaceAll("\\n\\s*\\n\\s*\\n+","\n\n").trim();
                if(!plain.isEmpty()) return sp;
            }
            return strip(txt==null?"":txt);
        } catch(Exception e){
            try { return strip(html!=null?html:txt); } catch(Exception e2){ return ""; }
        }
    }
}
'''

# ===========================================================================
# 5 : Menu  (More sheet matched to the reference: adds Rate / Privacy / Terms)
# ===========================================================================
MENU = r'''package online.mytempmail.app;
import android.app.Activity;
import android.app.AlertDialog;
import android.content.Intent;
import android.net.Uri;
import android.widget.Toast;
public class Menu {
    public static void open(final Activity a){
        final String notif = "Notifications: " + (Prefs.notifyOn() ? "ON" : "OFF");
        final String theme = "Theme: " + (Prefs.isDark() ? "Dark" : "Light");
        final String[] items = {"About Offex Mail", "Rate us", "Privacy Policy", "Terms of Use", "Contact us", theme, notif};
        new AlertDialog.Builder(a)
            .setTitle("More")
            .setItems(items, (d,w)->{
                try {
                    if(w==0) a.startActivity(new Intent(a, AboutActivity.class));
                    else if(w==1) openUrl(a,"https://play.google.com/store/apps/details?id=online.mytempmail.app");
                    else if(w==2) openUrl(a,"https://mytemp-mail.online/privacy");
                    else if(w==3) openUrl(a,"https://mytemp-mail.online/terms");
                    else if(w==4) a.startActivity(new Intent(a, ContactActivity.class));
                    else if(w==5) { Prefs.setThemeMode(Prefs.isDark() ? "light" : "dark"); a.recreate(); }
                    else {
                        Prefs.setNotify(!Prefs.notifyOn());
                        if(Prefs.notifyOn()) Notifier.ensure(a);
                        Toast.makeText(a, "Notifications " + (Prefs.notifyOn() ? "ON" : "OFF"), Toast.LENGTH_SHORT).show();
                    }
                } catch(Exception e){}
            })
            .show();
    }
    private static void openUrl(Activity a,String url){
        try { a.startActivity(new Intent(Intent.ACTION_VIEW, Uri.parse(url))); } catch(Exception e){}
    }
}
'''

W(J + "/Notifier.java", NOTIFIER)
W(J + "/MailService.java", MAILSERVICE)
W(J + "/MainActivity.java", MAIN)
W(J + "/ReaderActivity.java", READER)
W(J + "/Menu.java", MENU)

# ===========================================================================
# strings : append the new copy (never removing existing keys)
# ===========================================================================
STRINGS = [
    ("notif_service", "Background sync"),
    ("features_title", "Why Offex Mail"),
    ("features_sub", "Everything you need from a temporary inbox"),
    ("feat1_t", "Instant inbox"),
    ("feat1_d", "One tap for a private address - no signup, no password."),
    ("feat2_t", "OTP auto-detect"),
    ("feat2_d", "We spot the verification code and copy it in a single tap."),
    ("feat3_t", "Verification links"),
    ("feat3_d", "Links open straight in your browser so you can confirm fast."),
    ("feat4_t", "New-mail alerts"),
    ("feat4_d", "Get notified the moment mail lands, even in the background."),
    ("feat5_t", "Custom domains"),
    ("feat5_d", "Pick a name and choose the domain you like before you start."),
    ("feat6_t", "Auto-expiry"),
    ("feat6_d", "Inboxes clear themselves - nothing is kept forever."),
    ("otp_found", "VERIFICATION CODE"),
    ("copy_code", "Copy code"),
    ("code_copied", "Code copied"),
]
sp = RES + "/values/strings.xml"
s = R(sp)
block = "".join('    <string name="%s">%s</string>\n' % (k, v) for k, v in STRINGS)
s = s.replace("</resources>", block + "</resources>")
W(sp, s)

# ===========================================================================
# layout : features section on the home screen
# ===========================================================================
def feature(icon, title, desc):
    return ('            <LinearLayout android:layout_width="match_parent" android:layout_height="wrap_content"\n'
            '                android:layout_marginTop="10dp" android:background="@drawable/bg_card"\n'
            '                android:elevation="2dp" android:orientation="horizontal"\n'
            '                android:gravity="center_vertical" android:padding="16dp">\n'
            '                <TextView android:layout_width="44dp" android:layout_height="44dp"\n'
            '                    android:background="@drawable/bg_logo" android:gravity="center"\n'
            '                    android:text="%s" android:textColor="@color/offex_white" android:textSize="20sp" />\n'
            '                <LinearLayout android:layout_width="0dp" android:layout_height="wrap_content"\n'
            '                    android:layout_weight="1" android:layout_marginStart="14dp" android:orientation="vertical">\n'
            '                    <TextView android:layout_width="match_parent" android:layout_height="wrap_content"\n'
            '                        android:text="@string/%s" android:textColor="?attr/oxText"\n'
            '                        android:textSize="14sp" android:textStyle="bold" />\n'
            '                    <TextView android:layout_width="match_parent" android:layout_height="wrap_content"\n'
            '                        android:layout_marginTop="2dp" android:text="@string/%s"\n'
            '                        android:textColor="?attr/oxTextDim" android:textSize="12.5sp"\n'
            '                        android:lineSpacingExtra="3dp" />\n'
            '                </LinearLayout>\n'
            '            </LinearLayout>\n' % (icon, title, desc))

FEATURES = (
    '\n            <!-- ============ FEATURES ============ -->\n'
    '            <TextView android:layout_width="wrap_content" android:layout_height="wrap_content"\n'
    '                android:layout_marginStart="20dp" android:layout_marginTop="26dp" android:text="@string/features_title"\n'
    '                android:textColor="?attr/oxText" android:textSize="18sp" android:textStyle="bold"\n'
    '                android:fontFamily="sans-serif-medium" />\n'
    '            <TextView android:layout_width="match_parent" android:layout_height="wrap_content"\n'
    '                android:layout_marginStart="20dp" android:layout_marginEnd="20dp" android:layout_marginTop="3dp"\n'
    '                android:text="@string/features_sub" android:textColor="?attr/oxTextDim" android:textSize="13sp" />\n'
    '            <LinearLayout android:id="@+id/featuresBox" android:layout_width="match_parent"\n'
    '                android:layout_height="wrap_content" android:layout_marginStart="16dp"\n'
    '                android:layout_marginEnd="16dp" android:orientation="vertical">\n'
    + feature("\u26A1", "feat1_t", "feat1_d")
    + feature("\U0001F511", "feat2_t", "feat2_d")
    + feature("\U0001F517", "feat3_t", "feat3_d")
    + feature("\U0001F514", "feat4_t", "feat4_d")
    + feature("\U0001F310", "feat5_t", "feat5_d")
    + feature("\u231B", "feat6_t", "feat6_d")
    + '            </LinearLayout>\n\n'
)

lp = RES + "/layout/activity_main.xml"
s = R(lp)
anchor = "            <!-- ============ INBOX ============ -->"
if anchor in s:
    s = s.replace(anchor, FEATURES + anchor)
else:
    print("Q: WARN inbox anchor not found in activity_main.xml")
W(lp, s)

# ===========================================================================
# layout : OTP copy card in the reader
# ===========================================================================
OTP_CARD = (
    '        <LinearLayout android:id="@+id/otpCard" android:layout_width="match_parent"\n'
    '            android:layout_height="wrap_content" android:layout_marginTop="14dp"\n'
    '            android:background="@drawable/bg_card" android:elevation="3dp"\n'
    '            android:orientation="vertical" android:padding="18dp" android:visibility="gone">\n'
    '            <TextView android:layout_width="wrap_content" android:layout_height="wrap_content"\n'
    '                android:text="@string/otp_found" android:textColor="@color/offex_green"\n'
    '                android:textSize="11sp" android:textStyle="bold" android:letterSpacing="0.12" />\n'
    '            <LinearLayout android:layout_width="match_parent" android:layout_height="wrap_content"\n'
    '                android:layout_marginTop="8dp" android:orientation="horizontal" android:gravity="center_vertical">\n'
    '                <TextView android:id="@+id/otpValue" android:layout_width="0dp" android:layout_height="wrap_content"\n'
    '                    android:layout_weight="1" android:textColor="?attr/oxText" android:textSize="26sp"\n'
    '                    android:textStyle="bold" android:letterSpacing="0.08" android:textIsSelectable="true" />\n'
    '                <TextView android:id="@+id/copyCodeBtn" android:layout_width="wrap_content"\n'
    '                    android:layout_height="44dp" android:gravity="center" android:clickable="true"\n'
    '                    android:focusable="true" android:paddingStart="18dp" android:paddingEnd="18dp"\n'
    '                    android:background="@drawable/bg_btn_primary" android:text="@string/copy_code"\n'
    '                    android:textColor="@color/offex_white" android:textSize="14sp" android:textStyle="bold" />\n'
    '            </LinearLayout>\n'
    '        </LinearLayout>\n\n'
)
rp = RES + "/layout/activity_reader.xml"
s = R(rp)
ranchor = ('        <LinearLayout android:layout_width="match_parent" android:layout_height="wrap_content"\n'
           '            android:layout_marginTop="14dp" android:background="@drawable/bg_card" android:elevation="3dp"\n'
           '            android:orientation="vertical" android:padding="20dp">\n'
           '            <TextView android:id="@+id/rBody"')
if ranchor in s:
    s = s.replace(ranchor, OTP_CARD + ranchor)
else:
    print("Q: WARN reader anchor not found in activity_reader.xml")
W(rp, s)

# ===========================================================================
# versions : 3.2 -> 3.3
# ===========================================================================
bp = "android/app/build.gradle"
s = R(bp)
s = re.sub(r'versionCode \d+', 'versionCode 23', s)
s = re.sub(r'versionName "[^"]*"', 'versionName "3.3"', s)
W(bp, s)

cp = J + "/Config.java"
s = R(cp)
s = s.replace("__VER__", "3.3")                 # update-check self version
s = s.replace('latest.equals("3.2")', 'latest.equals("3.3")')
W(cp, s)

ap = RES + "/layout/activity_about.xml"
s = R(ap)
s = s.replace("Version 3.1", "Version 3.3")
W(ap, s)

# ===========================================================================
# palette : shift the brand accent from purple to the reference red
# ===========================================================================
COLORS = [
    ("6D4DFF", "E53935"),
    ("5F51FF", "D32F2F"),
    ("8B6CFF", "FF6F60"),
    ("7E5BFF", "EF5350"),
    ("9B6DFF", "FF8A80"),
    ("4B2FD6", "C62828"),
    ("EFEAFF", "FDECEA"),
    ("EDE8FF", "FDECEA"),
    ("DED4FF", "F6CFCB"),
    ("B9A8FF", "FFCDD2"),
    ("241E4D", "3B2320"),
    ("3A3178", "5A3733"),
    ("241A55", "3A1F1F"),
]
changed = 0
for root, _, files in os.walk("android/app/src/main"):
    for fn in files:
        if not (fn.endswith(".xml") or fn.endswith(".java")):
            continue
        p = os.path.join(root, fn)
        s = R(p)
        o = s
        for a, b in COLORS:
            s = s.replace(a, b)
        if s != o:
            W(p, s); changed += 1

print("Q: applied v3.3 fixes; files recoloured:", changed)
