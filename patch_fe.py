p = "public/index.html"
s = open(p, encoding="utf-8").read()

# A) suffix span -> select
old_a = '<span class="suffix" id="domainSuffix">@offexmail.online</span>'
new_a = '<select class="suffix" id="domainSuffix" title="Mail domain" aria-label="Mail domain"><option value="offexmail.online">@offexmail.online</option></select>'
assert old_a in s, "A not found"
s = s.replace(old_a, new_a, 1)

# B) CSS for select.suffix
old_b = "  .prefix .suffix{padding:13px 12px;color:var(--muted);font-family:'JetBrains Mono',monospace;font-size:12.5px;\n    border-inline-start:1px solid var(--border);white-space:nowrap}"
new_b = old_b + "\n  .prefix select.suffix{background:transparent;border:none;outline:none;cursor:pointer;appearance:auto}"
assert old_b in s, "B not found"
s = s.replace(old_b, new_b, 1)

# C) populate options from /status domains
old_c = 'api("/status").then(function(s){ if(s && s.domain) $("domainSuffix").textContent = "@" + s.domain; }).catch(function(){});'
new_c = 'api("/status").then(function(s){ var sel=$("domainSuffix"); if(sel && s && s.domains && s.domains.length){ sel.innerHTML = s.domains.map(function(d){ return \'<option value="\'+esc(d)+\'">@\'+esc(d)+\'</option>\'; }).join(""); } }).catch(function(){});'
assert old_c in s, "C not found"
s = s.replace(old_c, new_c, 1)

# D) send chosen domain on create
old_d = '    api("/inbox", { method:"POST", body: JSON.stringify(custom ? { custom: custom } : {}) })'
new_d = '    var dom = ($("domainSuffix") && $("domainSuffix").value) || "";\n    var payload = {}; if(custom) payload.custom = custom; if(dom) payload.domain = dom;\n    api("/inbox", { method:"POST", body: JSON.stringify(payload) })'
assert old_d in s, "D not found"
s = s.replace(old_d, new_d, 1)

open(p, "w", encoding="utf-8").write(s)
print("frontend patched OK")
