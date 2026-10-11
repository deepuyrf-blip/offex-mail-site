#!/usr/bin/env python3
"""
Build the additional Offex Mail blog guides under public/blog/.

Each guide gets the same head/SEO scaffold as the existing guides (canonical,
OG/Twitter, AdSense snippet, Article + FAQPage JSON-LD) and a hand-written,
topic-specific body so the guides are not near-duplicates of one another.

Run: python tools/make_guides.py
"""
from __future__ import annotations

import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BLOG = ROOT / "public" / "blog"
BASE = "https://mytemp-mail.online"

STYLE = """<style>
:root{--accent:#6d4dff;--ink:#1a1730;--muted:#5b5776;--bg:#f6f4ff;--card:#fff;--line:#e8e4ff}
*{box-sizing:border-box}
body{margin:0;font-family:'Inter',-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;color:var(--ink);background:var(--bg);line-height:1.7;-webkit-font-smoothing:antialiased;overflow-wrap:break-word}
a{color:var(--accent)}
header.site{display:flex;align-items:center;justify-content:space-between;gap:12px;max-width:820px;margin:0 auto;padding:16px}
.brand{font-weight:800;text-decoration:none;color:var(--ink)}
.brand span{color:var(--accent)}
.nav a{color:var(--muted);text-decoration:none;font-size:.9rem;margin-left:14px}
.wrap{max-width:820px;margin:0 auto;padding:8px 16px 56px}
.hero{background:linear-gradient(135deg,#6d4dff,#9b6dff);color:#fff;border-radius:18px;padding:30px 22px;margin-bottom:22px}
.hero h1{margin:0;font-size:1.6rem;line-height:1.3;letter-spacing:-.02em}
.hero .meta{opacity:.9;font-size:.85rem;margin-top:8px}
.card{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:22px;box-shadow:0 6px 24px rgba(80,60,180,.07)}
h2{font-size:1.25rem;margin:1.5em 0 .5em}
h3{font-size:1.05rem;margin:1.2em 0 .35em}
p{margin:.7em 0}
ul,ol{padding-left:1.25em}
li{margin:.4em 0}
figure{margin:1.5em 0;text-align:center}
figure img{width:100%;height:auto;border:1px solid var(--line);border-radius:12px;background:#fff;display:block}
figcaption{color:var(--muted);font-size:.85rem;margin-top:.5em}
.cta{display:inline-block;background:linear-gradient(135deg,#6d4dff,#9b6dff);color:#fff;text-decoration:none;font-weight:700;padding:13px 24px;border-radius:12px;margin:8px 0}
.related{list-style:none;padding:0;display:flex;flex-wrap:wrap;gap:8px;margin:14px 0}
.related a{font-size:.9rem;text-decoration:none;border:1px solid var(--line);border-radius:999px;padding:6px 12px;background:#fff}
footer{max-width:820px;margin:0 auto;padding:20px 16px 44px;color:var(--muted);font-size:.85rem;text-align:center}
footer a{text-decoration:none}
</style>"""

# ---------------------------------------------------------------------------
# guide content.  "body" is a list of raw HTML blocks (all unique per guide).
# ---------------------------------------------------------------------------
GUIDES = []


def guide(slug, title, h1, desc, read, hero, hero_alt, hero_cap, body, faq):
    GUIDES.append(dict(slug=slug, title=title, h1=h1, desc=desc, read=read,
                       hero=hero, hero_alt=hero_alt, hero_cap=hero_cap,
                       body=body, faq=faq))


guide(
 "why-verification-codes-expire",
 "Why Verification Codes Expire (and How to Beat the Clock)",
 "Why verification codes expire — and how to beat the clock",
 "Every verification code has a timer. Here is why sites expire codes so fast, the three clocks you are racing, and how to recover when the code dies before you use it.",
 "7 min read", "inbox-timeline.svg",
 "Timeline of a temporary inbox being created, receiving mail and expiring",
 "Two clocks run at once: the code's timer and your inbox's timer.",
 ["""<p>Few things are more annoying than a code that dies in the seconds between arriving and being typed. It feels arbitrary, but code expiry is a deliberate design choice, and understanding the timers involved turns a frustrating race into a predictable one.</p>""",
  """<h2>What &ldquo;expiry&rdquo; actually means</h2>
<p>A verification code is a short-lived secret. The moment a site generates it, it stores that value next to your pending request, along with a deadline. When the deadline passes, the stored value is discarded and the code becomes worthless &mdash; not because anything went wrong, but because the server decided the window had closed. The same code will simply be rejected on the next attempt.</p>
<p>That deadline exists because a code is a stand-in for proof of identity. The longer it lives, the longer an attacker who glimpses it has to use it. A tight window keeps the proof fresh.</p>""",
  """<h2>Why sites expire codes so quickly</h2>
<ul>
<li><strong>To shrink the attack window.</strong> A code visible on a shoulder-surfed screen or left in a shared inbox is only useful for a few minutes.</li>
<li><strong>To bound the server&rsquo;s work.</strong> Pending verifications are kept in memory or a short-lived store; expiry clears them automatically.</li>
<li><strong>To encourage a fresh request.</strong> A new code means a fresh email, which re-confirms the address is genuinely reachable.</li>
<li><strong>To follow the pattern set by banks.</strong> One-time passwords have always been short-lived, and most services copy that expectation.</li>
</ul>""",
  """<h2>The three clocks you are racing</h2>
<p>When a code &ldquo;expires&rdquo;, one of three separate timers has usually run out, and they are not the same length.</p>
<ol>
<li><strong>The code timer</strong> (often five to fifteen minutes) is the site&rsquo;s own deadline for the value it emailed.</li>
<li><strong>The delivery delay</strong> is the time the message spends in queues between the sender and your inbox. A busy sender can add a minute or two before you ever see the mail.</li>
<li><strong>Your inbox timer</strong> is how long your temporary address stays alive. If the inbox disappears, the code is gone regardless of its own deadline.</li>
</ol>
<p>Most &ldquo;expired code&rdquo; complaints are really delivery-delay problems: the mail arrived late, so by the time it was read only a sliver of the code&rsquo;s window remained.</p>""",
  """<h2>When the clock beats you: a recovery routine</h2>
<p>If a code is rejected as expired, do not keep retrying the same one. Instead:</p>
<ul>
<li>Request a brand-new code from the site &mdash; a fresh value gets a fresh deadline.</li>
<li>Watch the inbox as it arrives rather than switching tabs; the first seconds matter.</li>
<li>Copy the code rather than reading it across, so no digit is mistyped.</li>
<li>Paste it straight into the field and submit before doing anything else.</li>
<li>If codes keep arriving late, the sender&rsquo;s queue is the problem; waiting a minute before requesting again often helps.</li>
</ul>""",
  """<h2>How a temp inbox changes the maths</h2>
<p>A disposable inbox removes one of the three clocks from the equation by keeping the address live and open while you wait. Because the page refreshes itself, you see the message the instant it lands, which leaves the entire code window for you to use. The trade-off is the inbox&rsquo;s own expiry: work within it and the code timer is the only deadline that matters.</p>
<figure><img src="/images/expiry-timer.svg" width="320" height="320" alt="Clock showing a temporary inbox counting down to expiry" loading="lazy" decoding="async"><figcaption>Keep the inbox open; let the code, not the mailbox, be the thing that expires.</figcaption></figure>""",
  """<h2>Making expiry a non-issue</h2>
<p>The practical habit is simple: treat a verification email as something to act on immediately, not to save for later. Open it, take the code, use it, and only then go back to what you were doing. If you are testing a flow repeatedly, generate a new address for each pass so every code has a clean, full window. Expiry stops being a nuisance the moment you stop treating a live code as something you can leave sitting.</p>""",
  """<h2>One exception worth knowing</h2>
<p>Not every &ldquo;expired&rdquo; message is telling the truth about the code. Occasionally a service will reject a perfectly valid code because the address it was sent to does not match the one on the account, or because the request itself timed out on the server side. If a fresh code also fails, the problem is usually the request, not the timer: restart the flow from the beginning so the site generates a new pending verification. When even that fails, the address itself is the likely culprit &mdash; some services quietly refuse disposable domains, and no amount of retrying will change that.</p>"""],
 [("How long do verification codes usually last?",
   "Most services set a window of five to fifteen minutes, though some use as little as two. The exact figure is set by the site, not by your email provider."),
  ("Why did my code expire almost instantly?",
   "Almost always because it arrived late. The message spent time in the sender's queue, so only a few seconds of the code's own window remained when it reached you."),
  ("Can I reuse an old verification code?",
   "No. Once a code passes its deadline the server has discarded it, and the same value will be rejected. Request a new one instead."),
  ("Do temporary inboxes expire too?",
   "Yes. Each Offex Mail inbox stays active for a limited period, so the safest approach is to use the code as soon as it arrives rather than saving the mail for later.")])

guide(
 "temp-mail-for-free-trials",
 "Using a Temporary Email for Free Trials (Without Getting Billed)",
 "Using a temporary email for free trials — without getting billed",
 "A temp address is a good fit for some trials and a trap for others. Here is where it helps, where it fails, and how to try a service without a surprise charge.",
 "8 min read", "comparison-columns.svg",
 "Two columns comparing a throwaway inbox with a permanent second email account",
 "Trials and throwaways overlap, but they are not the same decision.",
 ["""<p>Free trials are one of the most common reasons people reach for a disposable address. The logic is appealing: try the product, decide later, and never let the company keep your real email. That works well in some cases and quietly backfires in others, and the difference comes down to what the trial actually demands.</p>""",
  """<h2>What a free trial actually requires</h2>
<p>Read the sign-up flow before you decide anything. Trials fall into three broad shapes:</p>
<ul>
<li><strong>Email-only trials</strong> ask for an address, send a confirmation link, and open the product. A throwaway address handles these perfectly.</li>
<li><strong>Card-on-file trials</strong> ask for payment details up front and convert to a paid plan automatically unless you cancel.</li>
<li><strong>Verified-identity trials</strong> may ask for a phone number or a work address in addition to an email, precisely to stop throwaways.</li>
</ul>
<p>Only the first shape is a clean fit for a temp inbox. The other two need more than a disposable address.</p>""",
  """<h2>Where a temp address helps &mdash; and where it does not</h2>
<p>A disposable address is excellent at one job: keeping your real inbox out of a company&rsquo;s marketing list while you sample something. It is bad at a different job: acting as the identity behind an account you might keep, cancel or dispute. If you will ever need a receipt, a cancellation confirmation or a password reset, the inbox has to outlive the trial.</p>
<p>The honest rule is that a temp address protects your <em>inbox</em>, not your <em>account</em>. Those are different assets.</p>""",
  """<h2>The billing trap: an inbox expiring is not a cancellation</h2>
<p>This is the mistake that costs money. Letting a disposable inbox expire feels like walking away, but it is not a cancellation. The subscription lives on the company&rsquo;s side, tied to the payment method, not to the email address. When the trial converts, the charge arrives regardless of whether you can still read the confirmation email.</p>
<figure><img src="/images/secure-form.svg" width="640" height="400" alt="A sign-up form filled in under a padlock" loading="lazy" decoding="async"><figcaption>A card on file outlives any inbox; cancel on the company's side, not by closing a tab.</figcaption></figure>
<p>So if a trial asks for a card, treat the temp address as a convenience, not a safety net. The cancellation is a separate task you must actually do.</p>""",
  """<h2>Two receipts worth keeping</h2>
<p>When a trial ends in a decision &mdash; whether you keep the service or leave it &mdash; save two things: the confirmation that you cancelled, and the last invoice or receipt. Screenshot them into a folder you will actually find again. This matters most when you used a disposable address, because once it expires those emails are gone for good. The company keeps its records; you should keep yours, and a two-second screenshot is cheap insurance against a charge you did not expect.</p>""",
  """<h2>A safer routine for trials</h2>
<ol>
<li><strong>Choose the right address for the job.</strong> Email-only trial? Use a temp inbox. Card required? Use an address you will keep for at least a billing cycle.</li>
<li><strong>Note the trial end date the moment you start.</strong> Put it in a calendar with a reminder a day or two before.</li>
<li><strong>Cancel in the product, not in your head.</strong> Follow the company&rsquo;s cancellation flow and keep the confirmation.</li>
<li><strong>Check the plan after cancelling.</strong> Confirm it now shows as cancelled or free before you stop paying attention.</li>
<li><strong>Let the temp inbox go only after that.</strong> Once the account is genuinely closed, there is nothing left for the address to protect.</li>
</ol>""",
  """<h2>If you decide to keep the service</h2>
<p>Sometimes a trial turns into something you use daily. When that happens, switch the account to a permanent address before the temporary one expires. Most products let you change your email in settings; do it while you still control both addresses, because a locked-out password reset on an expired inbox is a support ticket you would rather avoid.</p>""",
  """<h2>Reading the fine print quickly</h2>
<p>You do not need to read every clause. Scan for four things: when the trial ends, what it costs afterwards, how to cancel, and whether a card is required to start. Those four answers tell you whether a disposable address is the right tool or a distraction. Everything else can wait until you actually decide to pay.</p>""",
  """<h2>The habit that outlasts any single trial</h2>
<p>Trials come and go, but the underlying skill is the same every time: decide, before you type anything, whether this account is one you are only sampling or one you might keep. Sampling gets a throwaway address; keeping gets a permanent one. Get that decision right at the form, and the billing surprises, the lost receipts and the locked-out resets mostly never happen. A temp inbox is not a way to avoid thinking about a trial &mdash; it is a way to think about it once, quickly, and then move on.</p>"""],
 [("Can I use a temporary email for a free trial?",
   "Yes, for email-only trials. For trials that require a payment method, a disposable address keeps your real inbox clean but does not protect you from being billed."),
  ("Will the trial cancel itself when my temp inbox expires?",
   "No. Cancellation happens on the company's side and is tied to your account or payment method, not to the email address. You must cancel it yourself."),
  ("Why do some trials ask for a card up front?",
   "To reduce abuse and to make conversion automatic. A card on file means the trial rolls into a paid plan unless you cancel before the deadline."),
  ("What if I want to keep the service after the trial?",
   "Change the account to a permanent email address while you still control the temporary one, so password resets keep working.")])

guide(
 "how-to-spot-phishing-email",
 "How to Spot a Phishing Email in Any Inbox",
 "How to spot a phishing email in any inbox",
 "Phishing does not need a virus, only your click. Here are the four tells that matter, why a throwaway inbox sees more of it, and the one rule that defeats almost every attempt.",
 "7 min read", "phishing-alert.svg",
 "Warning triangle over a suspicious verification email",
 "The sender, the link and the urgency are where phishing gives itself away.",
 ["""<p>Phishing is the most common way accounts are stolen, and it rarely involves clever software. It involves a convincing email and a moment of haste. The good news is that phishing is also one of the most pattern-heavy crimes there is: once you know the tells, most attempts look obvious.</p>""",
  """<h2>The four tells that matter most</h2>
<ol>
<li><strong>The sender does not match the claim.</strong> A message that says it is from a bank but comes from an unrelated address is a red flag, no matter how polished the design.</li>
<li><strong>The link goes somewhere unexpected.</strong> The visible text may read like a familiar domain, but the actual destination can differ. Check before you click.</li>
<li><strong>The message creates urgency.</strong> &ldquo;Your account will be closed in 24 hours&rdquo; is engineered to stop you thinking. Legitimate services rarely threaten you into a same-day click.</li>
<li><strong>It asks for something no real service asks for by email.</strong> Passwords, full card numbers and one-time codes are things a genuine sender does not request by reply.</li>
</ol>""",
  """<h2>Why a temp inbox sees more phishing</h2>
<p>Disposable addresses are collected aggressively, precisely because they are cheap and abundant. That means a fresh temp inbox can start receiving junk within minutes, and some of it will be phishing aimed at whatever the sender thinks the address is worth. Seeing it is not a problem; the problem is only clicking it.</p>
<p>In fact, a throwaway inbox is a good place to <em>learn</em> what phishing looks like, because the stakes are low. Nothing valuable is tied to the address.</p>""",
  """<h2>Reading the sender, not the display name</h2>
<p>The name shown in a mail client is just a label the sender chose; it proves nothing. The real identity is the address and, behind it, the domain. A message claiming to be from a well-known brand should come from that brand&rsquo;s own domain, not from a lookalike with an extra hyphen or a different ending. When a verification email arrives right after you signed up somewhere, compare the sender against what you expect &mdash; a mismatch is your cue to slow down.</p>""",
  """<h2>What to do when you are unsure</h2>
<ul>
<li><strong>Do not click.</strong> Open a new tab and go to the service by typing its address yourself.</li>
<li><strong>Hover, do not tap.</strong> On desktop, rest the cursor on a link to preview its destination before committing.</li>
<li><strong>Check the request against reality.</strong> If you did not request a password reset or a new sign-in, treat the mail as suspect by default.</li>
<li><strong>Never reply with a code.</strong> A one-time code is the one thing an attacker most wants, and no legitimate support agent needs it.</li>
</ul>
<figure><img src="/images/spam-filter.svg" width="460" height="320" alt="Funnel filtering unwanted mail before it reaches the inbox" loading="lazy" decoding="async"><figcaption>Filtering helps, but recognising the pattern yourself is what actually stops the click.</figcaption></figure>""",
  """<h2>The one rule that defeats almost every phishing email</h2>
<p>If you remember nothing else: <strong>never act on a link or a code from an email you did not expect.</strong> Go to the site directly and do whatever the message claims to need there. That single habit removes the attacker&rsquo;s entire method, because phishing depends on you arriving at their page through their link, not through the real site.</p>
<p>Used with a disposable inbox, that rule makes the low-stakes sign-ups you do all week genuinely safe: you get the confirmation you need, and everything else in the inbox is just noise you are free to ignore.</p>""",
  """<h2>Why &ldquo;I have nothing to lose&rdquo; is a trap</h2>
<p>People often assume a throwaway inbox makes them safe from phishing, and that is only half true. The inbox is disposable; the device you open it on is not, and the passwords you type anywhere are not. A phishing page does not care which inbox you came from &mdash; it cares what you type into it. So the discipline travels with you: the same caution you would apply to your real mail applies to a burner inbox, because the target is you, not the mailbox.</p>""",
  """<h2>A quick habit for the whole week</h2>
<p>You do not need to become a security expert. A single default covers most situations: whenever a form asks for an email and you did not go looking for the service, treat the address as untrusted and reach any follow-up directly rather than through the message. That one habit, applied without effort, neutralises the vast majority of phishing because it removes the click the attacker depends on. Everything else in this guide is refinement.</p>"""],
 [("Are phishing emails common in temporary inboxes?",
   "Yes. Disposable addresses are collected aggressively, so a fresh inbox can receive junk and phishing quickly. Because nothing valuable is tied to the address, they are low-risk to observe and easy to ignore."),
  ("Can clicking a phishing link be dangerous even in a throwaway inbox?",
   "The inbox is disposable but your device and your real accounts are not. A phishing page can still try to install something or harvest credentials you type, so never click links you did not expect."),
  ("How do I check a link before clicking it?",
   "On a computer, hover over the link and read the real destination. On a phone, long-press to preview it. If the destination does not match the sender's real domain, do not open it."),
  ("Does Offex Mail filter phishing for me?",
   "Treat every inbox as unfiltered and apply your own judgement. The safe habit is to reach sites directly rather than through links in unexpected mail.")])

guide(
 "data-brokers-and-your-email",
 "What Data Brokers Know About Your Email Address",
 "What data brokers know about your email address",
 "Your address is a product before it is a problem. Here is how it becomes a data point, why deletion rarely finishes the job, and the preventive move that actually works.",
 "8 min read", "data-broker.svg",
 "A throwaway address keeping a real inbox out of data-broker lists",
 "By the time the spam arrives, the address has usually been sold several times.",
 ["""<p>Most people meet data brokers through their consequences: a sudden wave of mail addressed to a slightly wrong version of their name, or calls about a service they barely remember signing up for. The address was not stolen in a dramatic breach. It was collected, packaged and sold, and the sign-up you half-forgot was the handshake.</p>""",
  """<h2>How an address becomes a data point</h2>
<p>On its own, an email address is a key. What makes it valuable is everything that can be attached to it: a name, a rough location, shopping habits, which services you use, how often you open mail. Brokers do not need your permission to build that picture; they need only for your address to appear in enough places that the puzzle pieces can be matched together.</p>
<p>Newsletter platforms, loyalty schemes, competition entries and free downloads are all places an address surfaces. Individually harmless, collectively a profile.</p>""",
  """<h2>The sign-up is the handshake</h2>
<p>When you hand over your real address, you are rarely dealing with one company. Behind the form sit marketing tools, analytics pipelines and partner integrations, and any of them can be the point where your address leaves the circle you intended. The wording in the privacy policy &mdash; &ldquo;we may share with trusted partners&rdquo; &mdash; is often exactly this.</p>
<p>You cannot audit all of that. You can, however, choose what you hand over.</p>""",
  """<h2>Why deletion requests rarely finish the job</h2>
<p>Asking a broker to remove your data is worth doing, and in some regions it is a legal right. But a deletion request works on the copies a broker admits to holding. It does not reach the list that was already sold, the cached version, or the partner who received your address two years ago. Deletion reduces exposure; it does not undo it.</p>
<figure><img src="/images/digital-footprint.svg" width="640" height="400" alt="A shrinking digital footprint when sign-ups use a disposable address" loading="lazy" decoding="async"><figcaption>Prevention shrinks the footprint; deletion only trims the copies you can see.</figcaption></figure>""",
  """<h2>The preventive move</h2>
<p>The one action that reliably keeps your real address out of broker lists is to stop handing it to services that have not earned it. A disposable inbox makes that practical: you get the confirmation, the download or the trial, and the address that reaches the company&rsquo;s systems is one that expires before it is worth reselling. When the list is later traded, the buyer gets a dead address.</p>""",
  """<h2>A two-address strategy that actually works</h2>
<p>Two addresses, clearly divided, solve most of the problem before it starts:</p>
<ul>
<li><strong>A primary address</strong> for people, work, finance and anything you must be able to recover. Guard it fiercely and give it to almost no one.</li>
<li><strong>A disposable address</strong> for every sign-up you are only trying, every gated download and every one-off trial.</li>
</ul>
<p>If you want a third, a permanent &ldquo;shopping&rdquo; address sits between them for services you genuinely keep. The point is not to be paranoid; it is to make the decision once, in advance, instead of improvising at every form.</p>
<p>Seen this way, a temp inbox is not a trick to dodge marketing. It is the front door you use for anything that has not yet earned the back door.</p>""",
  """<h2>Aliases: a middle ground worth knowing</h2>
<p>If you want the privacy of disposable addresses with the durability of a permanent one, aliases are the middle path. An alias is a forwarding address that hides your real inbox and can be switched off individually, so you can hand a different one to every service and see instantly who leaked or sold it. Many mail providers offer this natively. The trade-off is that an alias still belongs to an account you maintain, whereas a throwaway address asks nothing of you at all. For the sign-ups you truly do not care about, disposable still wins; for the ones you keep but do not trust, an alias is the sharper tool.</p>"""],
 [("What is a data broker?",
   "A company that collects contact and behavioural data from many sources, combines it into profiles, and sells or licenses those profiles to marketers and others."),
  ("Can I get my email removed from broker lists?",
   "In many regions you can request deletion, and it is worth doing. But it only reaches copies a broker acknowledges, not lists already sold or cached, so it reduces exposure rather than erasing it."),
  ("Does a disposable address stop data brokers?",
   "It stops your real address from entering their lists in the first place. The broker may still hold the throwaway address, but it expires before it is worth much and reveals nothing about you."),
  ("Is my real address already out there?",
   "If you have used it for sign-ups, competitions or downloads, it very likely has been collected. That is a reason to protect it going forward, not a reason to give up on the habit.")])

guide(
 "temp-mail-for-newsletters-and-downloads",
 "Using a Temp Inbox for Newsletters and Gated Downloads",
 "Using a temp inbox for newsletters and gated downloads",
 "A gated download and a newsletter you actually want look identical at the form. Here is how to tell them apart and where a throwaway address is exactly right.",
 "7 min read", "spam-sources.svg",
 "One email address branching out to many sites that may resell or leak it",
 "The same form hides two very different intentions.",
 ["""<p>Half the internet seems to want your email before it will give you a PDF. Some of those exchanges are a fair trade and some are a trap, and at the moment you are staring at the form they look the same. The skill is telling them apart quickly and using the right address for each.</p>""",
  """<h2>The two situations that look the same but are not</h2>
<p>Case one: you want the file, and you will never think about the sender again. A checklist, a cheat-sheet, a template. Case two: you want the ongoing relationship &mdash; a newsletter whose next issue you genuinely look forward to. Both start with a form, but only one deserves a permanent address.</p>""",
  """<h2>When a throwaway is exactly right</h2>
<p>If you are there for the file and not the follow-up, a disposable address is the correct tool. It gets you the download, satisfies the gate, and absorbs whatever drip campaign follows. When the inbox expires, the thread is cut and your real address was never involved.</p>
<ul>
<li>One-off PDFs, templates and cheat-sheets.</li>
<li>Webinar recordings you will watch once.</li>
<li>Contests and giveaways you enter casually.</li>
<li>Coupon codes for a single purchase.</li>
</ul>""",
  """<h2>When you actually want the mail</h2>
<p>If the newsletter is something you look forward to, do the opposite: subscribe with an address you will keep. A temp inbox is the wrong choice for a subscription you intend to read, because it will expire and you will lose the very thing you wanted. The test is honest and quick: would you be annoyed to miss the next issue? If yes, use a permanent address.</p>""",
  """<h2>A middle path: alias now, decide later</h2>
<p>Uncertain? Start with a disposable address and see whether the first two issues earn your attention. If they do, resubscribe with a real address and unsubscribe the throwaway. If they do not, do nothing &mdash; the inbox expires and the decision is made for you. This &ldquo;try before you subscribe&rdquo; approach is one of the most practical uses of a temp inbox.</p>
<figure><img src="/images/comparison-columns.svg" width="640" height="400" alt="Two columns comparing a throwaway inbox with a permanent account" loading="lazy" decoding="async"><figcaption>File-only: throwaway. Relationship: permanent. Everything else: try, then decide.</figcaption></figure>""",
  """<h2>Downloading the file before the inbox goes</h2>
<p>A small practical point: some gates email you the download link rather than opening the file directly. Grab the file the moment it arrives rather than saving the email for later, because both the link and the inbox have their own expiry. If a link has already died, requesting it again usually works, as long as the inbox is still alive.</p>
<p>Handled this way, gated downloads stop being a tax on your real inbox. You keep the file, the sender keeps their list, and the only thing that expires is the address you never cared about.</p>""",
  """<h2>Newsletters that fight back: double opt-in</h2>
<p>Many reputable senders use double opt-in: the first form submission triggers a confirmation email, and you are only subscribed once you click the link inside it. A temp inbox handles this fine, but it changes the timing. Click the confirmation promptly, while the inbox is still alive, or the subscription never completes and the sender may treat the address as dead. If you are unsure whether you want the newsletter, the confirmation step is actually a useful pause &mdash; it is the moment you can still walk away without being subscribed at all.</p>""",
  """<h2>Organising the mail you decide to keep</h2>
<p>If you do subscribe with a permanent address, a little structure goes a long way. Route newsletters into their own folder so they never compete with messages from people, and unsubscribe from anything you have not opened in a month. The point of using a disposable address for the throwaway cases is precisely so that the mail you keep is the mail you chose &mdash; and a clean folder makes that choice visible.</p>"""],
 [("Is it okay to use a temp mail for a gated download?",
   "Yes. If you want the file and not the ongoing relationship, a disposable address is exactly the right tool: it clears the gate and keeps your real inbox out of the follow-up campaign."),
  ("Will the download link stop working?",
   "Links can expire just like codes and inboxes. Download the file as soon as the email arrives rather than saving the message for later."),
  ("What if the newsletter turns out to be genuinely useful?",
   "Resubscribe with a permanent address you will keep, and let the throwaway one go. Trying before you commit is a sensible use of a temp inbox."),
  ("Can I forward mail from a temp inbox?",
   "Offex Mail is built for receiving, which is what downloads and confirmations need. For anything you want to keep or forward, use a permanent address instead.")])

guide(
 "what-not-to-use-temp-mail-for",
 "What Not to Use a Temp Mail For",
 "What not to use a temp mail for",
 "A disposable inbox is a great tool with a sharp edge. Here is the simple test that tells you when a throwaway address is the wrong choice — before it costs you an account.",
 "7 min read", "cleanup-checklist.svg",
 "A checklist of habits that keep a real inbox free of spam",
 "The right address is the one you can still open when it matters.",
 ["""<p>Disposable email is a tool, and like any tool it has a correct and an incorrect use. Most of the advice around temp mail is about where to use it; this guide is about the opposite, because the mistakes here are the ones that actually hurt.</p>""",
  """<h2>The simple test: will you need this later?</h2>
<p>Before you type a disposable address into a form, ask one question: could I ever need to come back to this account? If the honest answer is yes &mdash; to reset a password, prove a purchase, receive a statement, recover access &mdash; then a throwaway address is the wrong choice. A temp inbox is designed to disappear, and an account that needs an inbox that lasts is a mismatch.</p>""",
  """<h2>Banking and payments</h2>
<p>Never use a disposable address for a bank, a card, a wallet or a payment service. These accounts depend on a reachable address for fraud alerts, statements and recovery, and they often treat an unreachable address as a security problem in its own right. The risk is not spam; it is losing access to money.</p>""",
  """<h2>Government and identity services</h2>
<p>Tax portals, licence renewals, benefit accounts and anything tied to your legal identity all belong on a permanent address. These systems are slow, they are unforgiving about email changes, and a failed verification can mean a trip you did not plan for. Use your real address and keep it secure.</p>""",
  """<h2>Accounts you will pay for</h2>
<p>If money will change hands, the inbox has to outlive the transaction. Receipts, invoices, renewal notices and cancellation confirmations all arrive by email, and all of them matter. A trial might start on a throwaway address, but the moment you decide to pay, switch to a permanent one.</p>
<figure><img src="/images/domain-reputation.svg" width="640" height="400" alt="A real domain that is accepted beside a throwaway domain that is rejected" loading="lazy" decoding="async"><figcaption>Some services refuse throwaway domains outright — a hint that they expect a lasting relationship.</figcaption></figure>""",
  """<h2>Anything you might need to recover</h2>
<p>Password resets are the clearest case. If you forget the password to an account tied to an expired inbox, the reset link has nowhere to go, and you may have no other way back in. The same applies to two-factor codes sent by email, or to proving ownership of an account you have had for years. Recovery is the single strongest reason to keep a permanent address on anything that matters.</p>""",
  """<h2>The upgrade path</h2>
<p>Using a disposable address to try something is fine; the mistake is forgetting to upgrade. When a throwaway account becomes one you rely on, move it to a permanent address promptly:</p>
<ul>
<li>Open the account settings while you still control both addresses.</li>
<li>Change the email to a permanent one you will keep.</li>
<li>Confirm the change from the new address, not the old.</li>
<li>Add a recovery method so a lost password is not a lost account.</li>
</ul>
<p>Done early, the upgrade is a two-minute task. Done late &mdash; after the inbox has expired &mdash; it can be impossible. A disposable inbox is a front door, not a foundation; keep the things you care about on solid ground.</p>""",
  """<h2>The grey area: social and marketplace accounts</h2>
<p>Between the obvious &ldquo;never&rdquo; cases and the obvious &ldquo;always&rdquo; cases sits a wide grey zone. A social profile you post from occasionally, a marketplace account used for one purchase, a forum login you barely remember: these are judgement calls. The test from the top of this guide still applies, but the stakes are lower. Ask what you would lose if you could never get back in. If the answer is &ldquo;a few posts I would not miss&rdquo;, a throwaway address is defensible. If the answer involves friends, followers, purchase history or messages you would want to keep, it is not.</p>
<p>A useful middle habit is to keep a single permanent &ldquo;secondary&rdquo; address for exactly this zone &mdash; the accounts that matter a little but not a lot. It is not anonymous, but it is recoverable, and it keeps your primary inbox reserved for the accounts that matter most. Three tiers &mdash; primary, secondary and throwaway &mdash; cover almost every sign-up you will meet.</p>"""],
 [("Can I use a temp mail for a bank account?",
   "No. Banks and payment services need a reachable address for alerts, statements and recovery, and an unreachable address can be treated as a security problem. Use a permanent address you control."),
  ("Why is temp mail bad for password resets?",
   "Because the reset link goes to an inbox that expires. If you forget the password after that, there may be no other way back into the account."),
  ("What about social media accounts I keep?",
   "If you rely on the account, use a permanent address. A throwaway address is fine only for a profile you would not mind losing."),
  ("How do I switch an account from a temp address to a real one?",
   "Open the account settings while both addresses still work, change the email to a permanent one, and confirm the change from the new address.")])

guide(
 "custom-domain-vs-temp-mail",
 "Custom Domain Email vs Temp Mail for Side Projects",
 "Custom domain email vs temp mail for side projects",
 "Both keep your personal inbox clean, but they solve different problems. Here is how a custom domain and a disposable inbox differ, and how to split the work between them.",
 "8 min read", "dev-testing.svg",
 "A developer console running automated sign-up and verification tests",
 "One is an identity you own; the other is a door you throw away.",
 ["""<p>If you run a side project, you have probably faced the same choice twice: what address should the project use, and what address should you use to sign up for other people&rsquo;s tools? The two answers are usually different, and reaching for the same tool for both is where people get into trouble.</p>""",
  """<h2>Two different jobs</h2>
<p>A custom domain address is an <em>identity</em>: something you own, keep and can move between providers. A disposable inbox is a <em>door</em>: something you use once and discard. Confusing the two leads either to paying for infrastructure you do not need, or to losing access to accounts you do.</p>""",
  """<h2>What a custom domain gives you</h2>
<ul>
<li><strong>Ownership.</strong> The address belongs to a domain you control, so it survives changing email providers.</li>
<li><strong>Consistency.</strong> Every message your project sends comes from the same recognisable domain, which builds trust.</li>
<li><strong>Deliverability.</strong> A clean, purpose-built domain is less likely to be filtered than a free address.</li>
<li><strong>Unlimited aliases.</strong> You can give each service its own address on your domain and route them as you like.</li>
</ul>
<p>What it does not give you is anonymity, and it is not free &mdash; you pay for the domain, and usually for hosting or forwarding.</p>""",
  """<h2>What a temp inbox gives you</h2>
<p>A disposable address gives you the opposite trade. It costs nothing, needs no setup, asks nothing about you, and disappears on its own. That makes it perfect for sampling tools, testing flows and clearing one-off gates &mdash; and useless for anything you must keep. You cannot build an identity on an address that is designed to expire.</p>
<figure><img src="/images/comparison-columns.svg" width="640" height="400" alt="A throwaway inbox beside a permanent second email account" loading="lazy" decoding="async"><figcaption>Own the address you send from; throw away the address you sign up with.</figcaption></figure>""",
  """<h2>The cost and maintenance of a custom domain</h2>
<p>A domain is cheap but not free, and it comes with upkeep: renewals, DNS records, and deliverability settings if you send mail from it. For a project that emails users, that upkeep is worth it. For a weekend experiment, it is overhead you will resent. The question is not &ldquo;which is better&rdquo; but &ldquo;does this project send mail people rely on?&rdquo;</p>""",
  """<h2>A sensible split for a solo project</h2>
<p>A workable pattern for one person running a few things:</p>
<ol>
<li><strong>Send from a custom domain.</strong> Your project&rsquo;s outbound mail &mdash; confirmations, notifications &mdash; should come from a domain you own, so it is trustworthy and portable.</li>
<li><strong>Sign up with disposable addresses.</strong> Every third-party tool you try gets a throwaway, so your project domain stays out of their marketing lists.</li>
<li><strong>Keep one permanent personal address</strong> for accounts you pay for or must recover.</li>
<li><strong>Add a project alias</strong> on your domain for the handful of services you keep long-term.</li>
</ol>
<p>Run that way, each address does the job it is good at. The domain carries your identity outward; the disposable inbox absorbs everything you are only sampling; and your personal address stays reserved for what matters. The mistake to avoid is trying to make one address do all three &mdash; that is how people end up either paying for anonymity they do not need or losing a project login they cannot recover.</p>""",
  """<h2>A note on sending mail from a temp address</h2>
<p>One limitation is easy to overlook: a disposable inbox is built for receiving, which is what sign-ups and confirmations need. It is not the tool you send from. If your project needs to reply to users, send notifications or handle support, that mail has to come from an address you own and can keep. This is the clearest dividing line between the two tools. Receiving is a door you can throw away; sending is a voice that has to belong to someone permanent. Decide which one the task needs before you pick an address, and the choice is usually obvious.</p>"""],
 [("Should I use a custom domain or temp mail for a project?",
   "Use a custom domain for anything your project sends or that you must keep, and a disposable inbox for the third-party tools you are only trying."),
  ("Is a custom domain worth the cost?",
   "If your project emails users and you want a trustworthy, portable identity, yes. For a short experiment, a disposable address is enough."),
  ("Can I mix both?",
   "Yes, and you probably should: a custom domain for identity, disposable inboxes for sampling tools, and one permanent address for accounts you pay for."),
  ("Do I need a custom domain to look professional?",
   "For anything user-facing, a domain you own reads as more trustworthy and travels better than a free address. For internal testing, it is unnecessary.")])


# ---------------------------------------------------------------------------
def build(g):
    faq_json = json.dumps({
        "@context": "https://schema.org", "@type": "FAQPage",
        "mainEntity": [{"@type": "Question", "name": q,
                        "acceptedAnswer": {"@type": "Answer", "text": a}}
                       for q, a in g["faq"]],
    }, ensure_ascii=False)
    art_json = json.dumps({
        "@context": "https://schema.org", "@type": "Article",
        "headline": g["h1"], "description": g["desc"],
        "image": f"{BASE}/images/{g['hero']}",
        "author": {"@type": "Person", "name": "Deepu"},
        "publisher": {"@type": "Organization", "name": "Offex Mail",
                      "logo": {"@type": "ImageObject", "url": f"{BASE}/icon-512.png"}},
        "datePublished": "2026-10-11", "dateModified": "2026-10-11",
        "mainEntityOfPage": {"@type": "WebPage", "@id": f"{BASE}/blog/{g['slug']}"},
        "inLanguage": "en",
    }, ensure_ascii=False)
    body = "\n".join(g["body"])
    faq_html = "\n".join(
        f'<h3>{html.escape(q)}</h3><p>{html.escape(a)}</p>' for q, a in g["faq"])
    head = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(g['title'])} | Offex Mail</title>
<meta name="description" content="{html.escape(g['desc'])}">
<meta name="robots" content="index,follow">
<link rel="canonical" href="{BASE}/blog/{g['slug']}">
<link rel="icon" href="/favicon.ico" sizes="any">
<meta property="og:type" content="article">
<meta property="og:site_name" content="Offex Mail">
<meta property="og:title" content="{html.escape(g['title'])}">
<meta property="og:description" content="{html.escape(g['desc'])}">
<meta property="og:url" content="{BASE}/blog/{g['slug']}">
<meta property="og:image" content="{BASE}/images/{g['hero']}">
<meta property="og:image:alt" content="{html.escape(g['hero_alt'])}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{html.escape(g['title'])}">
<meta name="twitter:description" content="{html.escape(g['desc'])}">
<meta name="twitter:image" content="{BASE}/images/{g['hero']}">
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-9424904813990636" crossorigin="anonymous"></script>
{STYLE}
<script type="application/ld+json">{art_json}</script>
<script type="application/ld+json">{faq_json}</script>
</head>
<body>
<header class="site"><a class="brand" href="/">Offex <span>Mail</span></a><nav class="nav"><a href="/blog/">Guides</a><a href="/">Open tool</a></nav></header>
<main class="wrap">
  <section class="hero"><h1>{html.escape(g['h1'])}</h1><div class="meta">Updated for 2026 &middot; {g['read']}</div></section>
  <article class="card">
<figure><img src="/images/{g['hero']}" width="640" height="400" alt="{html.escape(g['hero_alt'])}" loading="lazy" decoding="async"><figcaption>{html.escape(g['hero_cap'])}</figcaption></figure>
{body}
<h2>Frequently asked questions</h2>
{faq_html}
    <p style="text-align:center;margin-top:22px"><a class="cta" href="/">Create a free inbox &rarr;</a></p>
  </article>
  <section class="card" style="margin-top:18px"><h2>More guides</h2><ul class="related">{RELATED}</ul></section>
</main>
<footer><p>Offex Mail &mdash; free temporary email &amp; disposable inbox. <a href="/">mytemp-mail.online</a></p><p><a href="/about">About</a> &middot; <a href="/privacy">Privacy</a> &middot; <a href="/terms">Terms</a> &middot; <a href="/contact">Contact</a></p></footer>
<script src="/app-promo.js" defer></script>
</body>
</html>
"""
    return head


RELATED = ""


def main():
    global RELATED
    # cross-link every guide to five others plus the index (deterministic)
    slugs = [g["slug"] for g in GUIDES]
    for i, g in enumerate(GUIDES):
        picks = [slugs[(i + k + 1) % len(slugs)] for k in range(5)]
        titles = {x["slug"]: x["title"] for x in GUIDES}
        RELATED = "".join(
            f'<li><a href="/blog/{s}">{html.escape(titles[s])}</a></li>' for s in picks)
        RELATED += '<li><a href="/blog/">All guides</a></li>'
        (BLOG / f"{g['slug']}.html").write_text(build(g), encoding="utf-8")
        print("wrote", g["slug"])
    print(f"{len(GUIDES)} guides")


if __name__ == "__main__":
    main()
