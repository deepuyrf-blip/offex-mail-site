import os
import sys

RID = "factblink514/Compiled"


def load():
    local = os.environ.get("LOCAL_MAIN")
    if local:
        return open(local, encoding="utf-8").read()
    from huggingface_hub import hf_hub_download
    p = hf_hub_download(repo_id=RID, filename="main.py", repo_type="space")
    return open(p, encoding="utf-8").read()


src = load()
orig = src
applied = []


def rep(old, new, n=1, tag=""):
    global src
    c = src.count(old)
    if c != n:
        print("ANCHOR FAIL [%s] count=%d expected=%d :: %r" % (tag, c, n, old[:90]))
        sys.exit(2)
    src = src.replace(old, new)
    applied.append(tag)


rep(
    "DOMAIN = DOMAINS[0]\n",
    "DOMAIN = DOMAINS[0]\n"
    "# Permanent inboxes that never expire (used for the support address).\n"
    "PERMANENT_INBOXES = [d.strip().lower() for d in os.getenv(\"PERMANENT_INBOXES\", \"support@offexmail.online\").split(\",\") if d.strip()]\n"
    "PERMANENT_EXPIRES = 4102444800  # 2100-01-01 -> effectively \"never\"\n",
    1, "A-config",
)

rep(
    "    c.commit()\n    c.close()\n\n\ndef log_activity(event, detail=\"\", ip=\"\"):",
    "    c.commit()\n    c.close()\n\n\n"
    "def ensure_permanent_inboxes():\n"
    "    \"\"\"Make sure the permanent support inbox(es) always exist and never expire.\"\"\"\n"
    "    now = int(time.time())\n"
    "    try:\n"
    "        with db_lock:\n"
    "            c = db()\n"
    "            for addr in PERMANENT_INBOXES:\n"
    "                row = c.execute(\n"
    "                    \"SELECT id, expires_at, alias_deleted FROM inboxes WHERE address=?\", (addr,)\n"
    "                ).fetchone()\n"
    "                if row:\n"
    "                    if int(row[\"expires_at\"]) < PERMANENT_EXPIRES or int(row[\"alias_deleted\"] or 0) != 0:\n"
    "                        c.execute(\n"
    "                            \"UPDATE inboxes SET expires_at=?, alias_deleted=0 WHERE id=?\",\n"
    "                            (PERMANENT_EXPIRES, row[\"id\"]),\n"
    "                        )\n"
    "                else:\n"
    "                    c.execute(\n"
    "                        \"INSERT INTO inboxes(address, alias_id, created_at, expires_at, alias_deleted, owner_ip) \"\n"
    "                        \"VALUES(?,?,?,?,0,?)\",\n"
    "                        (addr, None, now, PERMANENT_EXPIRES, \"system\"),\n"
    "                    )\n"
    "            c.commit()\n"
    "            c.close()\n"
    "    except Exception:\n"
    "        logger.exception(\"ensure_permanent_inboxes failed\")\n\n\n"
    "ensure_permanent_inboxes()\n\n\n"
    "def log_activity(event, detail=\"\", ip=\"\"):",
    1, "B-ensure",
)

rep(
    "    wipes the inbox + its messages from our DB. Irreversible.\"\"\"\n    address = address.lower().strip()",
    "    wipes the inbox + its messages from our DB. Irreversible.\"\"\"\n"
    "    address = address.lower().strip()\n"
    "    if address in PERMANENT_INBOXES:\n"
    "        return json_error(\"Ye permanent support inbox hai \u2014 delete nahi ho sakta.\", 403)",
    1, "C-protect",
)

rep(
    "        if taken:\n            return json_error(f\"{address} is already in use right now. Try another name.\", 409)",
    "        if taken:\n"
    "            if address in PERMANENT_INBOXES:\n"
    "                with db_lock:\n"
    "                    c = db()\n"
    "                    row = c.execute(\n"
    "                        \"SELECT created_at, expires_at FROM inboxes WHERE address=?\", (address,)\n"
    "                    ).fetchone()\n"
    "                    c.close()\n"
    "                return {\n"
    "                    \"address\": address,\n"
    "                    \"created_at\": row[\"created_at\"],\n"
    "                    \"expires_at\": row[\"expires_at\"],\n"
    "                    \"permanent\": True,\n"
    "                }\n"
    "            return json_error(f\"{address} is already in use right now. Try another name.\", 409)",
    1, "D-resume",
)

rep(
    "        \"domain\": DOMAIN,\n        \"domains\": DOMAINS,\n",
    "        \"domain\": DOMAIN,\n        \"domains\": DOMAINS,\n        \"permanent_inboxes\": PERMANENT_INBOXES,\n",
    2, "E-status",
)

rep(
    "      <div class=\"online-badge\" id=\"onlineBadge\"><span class=\"dot2\"></span><span id=\"onlineText\">checking\u2026</span></div>\n"
    "      <button class=\"pill-btn\" onclick=\"checkStatus(true)\">\u2699\ufe0f</button>",
    "      <div class=\"online-badge\" id=\"onlineBadge\"><span class=\"dot2\"></span><span id=\"onlineText\">checking\u2026</span></div>\n"
    "      <button class=\"pill-btn\" id=\"supportPill\" title=\"Support inbox (permanent)\" onclick=\"openSupport()\">\U0001f4ee</button>\n"
    "      <button class=\"pill-btn\" onclick=\"checkStatus(true)\">\u2699\ufe0f</button>",
    1, "F-pill",
)

rep(
    "      <button class=\"cta\" id=\"createBtn\" onclick=\"createInbox()\">+ New Inbox</button>",
    "      <button class=\"cta\" id=\"createBtn\" onclick=\"createInbox()\">+ New Inbox</button>\n"
    "      <button class=\"cta\" style=\"margin-top:10px;background:linear-gradient(135deg,#3ddc97,#2bb37a)\" onclick=\"openSupport()\">\U0001f4ee Support inbox (permanent)</button>",
    1, "G-emptybtn",
)

rep(
    "function setActive(address){",
    "const SUPPORT_ADDR = \"support@offexmail.online\";\n"
    "function openSupport(){ setActive(SUPPORT_ADDR); }\n\n"
    "function setActive(address){",
    1, "H-js",
)

rep(
    "function updateStatusUI(expired, expiresAt){\n"
    "  const dot = document.getElementById('statusDot');\n"
    "  const text = document.getElementById('statusText');\n"
    "  if(expired){",
    "function updateStatusUI(expired, expiresAt){\n"
    "  const dot = document.getElementById('statusDot');\n"
    "  const text = document.getElementById('statusText');\n"
    "  if(currentAddress === SUPPORT_ADDR){\n"
    "    dot.classList.remove('expired');\n"
    "    text.textContent = 'permanent support inbox';\n"
    "    if(countdownTimer) clearInterval(countdownTimer);\n"
    "    document.getElementById('countdown').textContent = '\u221e';\n"
    "    return;\n"
    "  }\n"
    "  if(expired){",
    1, "I-status",
)

print("ALL EDITS OK:", applied)
print("changed:", src != orig, "size:", len(src))

if os.environ.get("UPLOAD") == "1":
    out = "/tmp/main_new.py"
    open(out, "w", encoding="utf-8").write(src)
    from huggingface_hub import HfApi
    import time
    api = HfApi(token=os.environ["HF_TOKEN"])
    api.upload_file(path_or_fileobj=out, path_in_repo="main.py", repo_id=RID, repo_type="space")
    print("UPLOADED main.py")
    time.sleep(5)
    api.restart_space(RID)
    print("RESTARTED")
