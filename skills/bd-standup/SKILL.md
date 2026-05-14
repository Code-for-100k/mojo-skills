---
name: bd-standup
description: "Generates Mayank's daily BD stand-up in his canonical Yesterday/Today format from Slack and Notion activity. Use whenever the user says 'standup', 'daily standup', 'BD standup', 'my stand up', 'make my standup', 'write up yesterday', 'what did I do yesterday', 'recap my day', or any phrasing asking for an end-of-day or start-of-day BD update; also trigger on `/standup` and `/bd-standup`. Output is chat-draft only — never auto-post unless the user explicitly says 'post it'. Pulls last working day of Slack (paginated; his messages + thread replies across all channels including #bd-ai-crm SFDC bot) plus Notion meeting notes; excludes automated CBTC briefs, cooldown self-prompts, and bot messages. Not for engineering standups, weekly sales meeting briefs, leadership status reports, or sprint retros."
---

# BD Stand Up — Mayank's daily standup generator

Composes Mayank's daily BD stand-up in the exact format he posts to `#business-development`. Pulls the last working day of Slack activity + recent Notion meeting notes/tasks, filters out automated brief output, and synthesizes a comprehensive Yesterday/Today list. Chat-draft only by default.

## Canonical output format

Match Mayank's pattern exactly — this is what he's posted on Apr 27, Apr 28, Apr 30, May 4, May 7, May 8:

```
Mayank's BD Stand Up

Yesterday (M/D)
• Partner — concise update with key detail :tada: (if win)
   ◦ Optional sub-bullet for context
• Partner — ...

Today (M/D)
• Partner — what shipped + what's open
• Partner — ...
```

Rules:
- Title: `Mayank's BD Stand Up` (sometimes `Standup`, either ok — be consistent within one post)
- Section headers: `Yesterday (M/D)` and `Today (M/D)` — plain text, no bold
- Bullets: `•` for top-level, `◦` for sub-bullets
- Wins use `:tada:` (Closed Won, signatures received, breakthroughs). No other emoji.
- Em-dashes between partner name and the action
- Concise — one line per partner where possible. Sub-bullets only when context is load-bearing
- Comprehensive — list every partner touched. He'd rather see 15 bullets than a tight 6
- "Today" mixes things already done this morning + planned for the rest of the day. Don't split into Done/Doing
- No "Blockers" section — he doesn't use one. If something is genuinely stuck, mention it in-line under the relevant partner bullet
- Internal teammates (Aki, Anna, Kadeem, Gabi, NanoClaw) appear in context, not as their own bullets

Post target when user asks to post: `#business-development` (channel ID `C094Q9TUVUL`). Default is chat-only — wait for explicit "post it" before sending.

## Source priority

1. **Slack — primary.** User's messages + thread replies across all channels in the date window. This is the foundation; everything else is enrichment.
2. **Notion meeting notes + tasks.** Catches calls held yesterday (Fathom-linked notes) and recent decisions/H-tasks that didn't land in Slack.
3. **Skip Gmail by default.** Only pull Gmail if Slack signal is unusually thin (< 5 messages in window).

SFDC activity is captured naturally via Slack — every SFDC move (Closed Won/Lost, stage change, new opp, ownership change) appears as a message in `#bd-ai-crm` (channel ID `C0B05B7NX1S`).

## Step-by-step workflow

### 1. Resolve user + date window

```
slack_read_user_profile()   # no args → current user; returns user_id
```

**Date window:**
- "Yesterday" = the previous working day. If today is **Monday**, yesterday covers **Friday + weekend**. Otherwise = calendar yesterday.
- "Today" = current date.
- Slack search filter: `after:<yesterday>` (inclusive of yesterday onward).

### 2. Pull Slack signal — PAGINATE FULLY

```
slack_search_public_and_private(
  query="from:<@USER_ID> after:<YYYY-MM-DD>",
  sort="timestamp",
  limit=20,
  include_context=false,
  channel_types="public_channel,private_channel,mpim,im"
)
```

**Pagination is mandatory, not optional.** A single page returns ~20 results. On any active BD day Mayank sends 15–40 messages. Check `pagination_info` in the response — if it shows `For the next page of results use cursor ...`, keep paginating until exhausted or you've fetched 5 pages. **Stopping at page 1 silently drops up to 26% of his activity** (Slack docs warn about this).

Run **twice** in parallel:
- (a) `after:<yesterday>` to catch yesterday's full activity
- (b) `after:<today>` to catch today's activity separately (so you can split cleanly into Yesterday vs Today sections)

Sort by timestamp ascending and split locally by date. If both windows are empty after pagination, widen the date by one day before assuming "quiet day" — partner activity is highly variable.

### 3. Expand important threads

For messages with `Reply count: > 0` in partner channels (e.g. `#qcp-bitsafe`, `#gravityteam-bitsafe`, `#bd-ai-crm`), call:

```
slack_read_thread(channel_id=..., message_ts=..., response_format="concise")
```

Don't expand every thread — only the ones where Mayank's reply was a substantive action (offer sent, decision made, intro requested). Skip routine "ok" or "👍" replies.

### 4. Pull Notion (parallel with step 2)

**Meeting notes (Fathom-linked):**

```
notion-query-meeting-notes(filter: {
  operator: "and",
  filters: [
    { property: "created_time", filter: { operator: "date_is_within",
      value: { type: "relative", value: { type: "daterange", direction: "past", unit: "day", count: 3 }}}}
  ]
})
```

If a partner-specific meeting happened yesterday, the Fathom link goes in the standup bullet (e.g. `Silvana — EF call today; Fathom: https://fathom.video/calls/...`).

**Recent decisions / H-tasks:**

```
notion-search(query="<partner names from Slack signal>",
  filters={created_date_range: {start_date: <yesterday>}})
```

Use Notion search sparingly — only when a Slack thread referenced a Notion doc/decision that needs context.

### 5. Categorize Slack messages

Sort into buckets:

| Bucket | Pattern | Output style |
|---|---|---|
| Wins | `Closed Won`, `signed`, partner replied yes | `Partner — [headline] :tada:` |
| Losses | `Closed Lost`, deals killed | `Partner — Closed Lost (reason)` |
| Outbound nudges | Mayank sent a partner DM/message | `Partner — [name] [action] on [topic]` |
| Internal coordination | DMs with Aki / Anna / Kadeem / Gabi / NanoClaw | Fold into relevant partner bullet |
| CRM moves | Messages in `#bd-ai-crm` | Standalone bullets per opp move (Closed Won/Lost) OR bundled "CRM hygiene" bullet (stage changes, new opps, ownership cleanup). Mayank uses "CRM hygiene" terminology in standups, never "SFDC hygiene". |
| Calls held | Notion meeting note exists for yesterday | `Partner — [Person] call held; [outcome]` |
| Calls scheduled | Calendar/calendly mentioned in thread | `Partner — call scheduled for [date]` |
| New channels / opps | `created` keywords | Fold into relevant partner bullet |

### 6. Filter OUT (do not include)

- Automated CBTC follow-up briefs (morning/evening) posted in `#nanoclaw-cowork` — these are bot output, not Mayank's work
- Weekly sales meeting brief — same
- Cooldown re-surface prompts to self (DM channel `D091F8XHR51`)
- Status-only acks like `:thumbsup:`, `ok`, `:eyes:`
- Bot messages (filter `include_bots: false` in search; default is false)
- The standup itself if posted earlier
- **Internal-only DMs that don't advance a partner outcome.** Generic team coordination like "fyi @vinay", "to see temple uptime", context-sharing pings to Aki/Kadeem/Jesse where no partner action follows. If the DM IS partner-relevant (e.g. Vala play to Kadeem), fold it into that partner's bullet instead of listing as standalone "internal coordination".

### 7. Compose draft

- **Yesterday** = state-change items only (wins, losses, MSAs sent, calls held, opps moved, threads progressed)
- **Today** = mix of what's already happened this morning + planned actions for the rest of the day
  - For "planned today" items: pull from this morning's CBTC brief's "Top to act" list if it ran. Cross-check against open items from yesterday that didn't close
  - For "already done today" items: from Slack search with `after:<today>` filter

Order within each section: highest-impact partners (L-tier per registry: QCP, Silvana, Tokka, Gravity, Excellar, Console, Bron, AngelHack) first, then M-tier, then admin/SFDC hygiene at the bottom.

### 8. Present in chat — DO NOT POST

Show the draft inline. Append:

> Want me to trim, adjust, or post to `#business-development`?

Wait for explicit instruction before calling `slack_send_message`. Never auto-post.

## Date logic

**Rule:** "Yesterday" = the previous *business day*, not the previous calendar day.

- **Mon → Yesterday spans Fri + weekend.** Use `after:<previous_friday>`. Three days of partner activity, not one. Failing to widen here is the #1 source of "thin standup" output on Mondays.
- **Day after a US/UK/IN holiday → extend window backward** to cover the holiday(s). E.g. day after Memorial Day → `after:<previous_friday>`.
- **Otherwise** → Yesterday = calendar yesterday.

**Worked examples:**
- Today is Tue May 14 → Yesterday = Mon May 13. Query: `after:2026-05-13`
- Today is Mon May 14 → Yesterday = Fri May 11 (covers Fri + weekend). Query: `after:2026-05-11`
- Today is Tue May 26 (day after Memorial Day) → Yesterday = Fri May 22. Query: `after:2026-05-22`
- Today is Wed Dec 25 → Yesterday = Tue Dec 24. Standard.

Resolve "today" via the host clock in IST (Mayank's timezone). Don't rely on Slack's UTC timestamps for the window math — compute in IST, then convert to date string for the search filter.

## Verification checklist — copy this into your working notes before composing

Treat each box as a hard gate. If any is unchecked, do the missing work before drafting.

```
[ ] Date window is correct for today's day-of-week (Mon → covers Fri+weekend; post-holiday → extended)
[ ] Slack search paginated until pagination_info shows no more pages (or 5 pages exhausted)
[ ] Thread replies fetched for every partner-channel message with reply_count > 0
[ ] Automated CBTC briefs from #nanoclaw-cowork excluded
[ ] Cooldown re-surface DMs (channel D091F8XHR51) excluded
[ ] Every :tada: win traces to a Slack permalink (SFDC move, signature receipt, or partner reply)
[ ] Every "MSA sent" bullet names the target person + channel
[ ] Today section: at least one item from this morning's CBTC brief OR an explicit note that no morning brief ran
[ ] Partner names match registry conventions (SciFeCap, MeteorWallet, OpenVector, AngelHack — not lowercased or space-split)
[ ] No partner name appears that wasn't found in the actual Slack/Notion pull (anti-fabrication)
[ ] Date headers use M/D format (e.g. "Yesterday (5/13)")
[ ] Bullet count per section: 8–15 ideal. <5 → re-widen window. >20 → bundle side-quests
```

If you can't tick a box, say so in the response — don't silently skip and pad the output.

## Channel reference

| Channel | ID | Purpose |
|---|---|---|
| `#business-development` | `C094Q9TUVUL` | **Post target** for the standup |
| `#bd-ai-crm` | `C0B05B7NX1S` | SFDC bot — every opp move appears here |
| `#nanoclaw-cowork` | `C0AU6LA5F7S` | Automated CBTC briefs land here — exclude from standup |
| `#qcp-bitsafe` | `C0A4BHJEAR2` | QCP partner channel |
| `#gravityteam-bitsafe` | `C09FD4NL70B` | Gravity partner channel |
| `#tokka-labs-bitsafe` | (lookup) | Tokka partner channel |
| `#angelhack-bitsafe` | (lookup) | AngelHack partner channel |
| `#bitsafe-silvana` | (lookup) | Silvana partner channel |

Use `slack_search_channels` to resolve any partner channel ID not listed.

## Partner naming reference (most common)

- **L-tier (always lead bullets):** QCP, Silvana, Tokka Labs, Gravity Team, Excellar / SciFeCap, Console, Bron, AngelHack, Auros Global, Garden, Rho Labs (when active)
- **M-tier:** Zoro / OpenVector, MeteorWallet, Cantor8 / DigiK, BitLeo, Vala Wallet, Nightly Wallet, SatsTerminal / OneSwap, Tenkai / Cansai, InfraSingularity, Send Wallet, PoolParty, Squid Router, Palladium
- **Internal teammates (don't bullet, fold into partner context):** Aki Balogh, Anna Matusova, Kadeem Clarke, Gabi Tuinaite, NanoClaw, Mitch, Jesse Eisenberg, Max, Isabella Henderson

## Contact → partner mapping (prevents mis-attribution)

When a DM appears in the Slack pull, resolve the contact to their partner before writing the bullet. Don't assume — check this table:

| Contact | Partner | Notes |
|---|---|---|
| Michelle Chong, Jovin Ong | QCP | Michelle = primary deal contact; Jovin = May 4 new hire on the cap negotiation |
| Ralph Idio | Gravity Team | calendly: `calendly.com/ralph-idio-gravityteam/30min` |
| Alexei Dulub | Console / PixelPlex | |
| Dmitry Tokarev, Asen Kostadinov, Natalia Maximova | Bron | Asen + Natalia are the escalation cc list |
| Shikhar (OpenVector), Rohan, Shivam Kumar | Zoro / OpenVector | Shivam Kumar is the new BD contact (joined ~May 13). Do NOT mis-attribute to Garden. |
| Kenneth T., Bryan Foo | AngelHack | |
| Michael K (mk@silvana.one) | Silvana | |
| Tim Freed, Andrew | Efficient Frontier | Connected to Silvana via intro |
| Kylie Chee, Maxence | Tokka Labs | Maxence = their trader |
| Amit Kaushik | Excellar / SciFeCap | Same person, two workstreams (xlTokens FA + LP MSA) |
| Susruth, Pankaj | Garden | Garden does significant work on Telegram — Slack-only view is incomplete |
| Edward Chew | MeteorWallet | |
| Alex Legkodumov, Alexander | Rho Labs | |
| David | BitLeo | |
| Philip N Kaddaj | Cantor8 / DigiK | |
| Amy Wu | Cantor8 (separate from Philip) | |
| Vitesh, Jitin Jain | InfraSingularity | |
| Fig | Squid Router | fig@squidrouter.com |
| Stan, Viraj, Barbra | SatsTerminal / OneSwap | |
| Kadeem (handling Finoa side) | Vala Wallet | Finoa is the Vala parent |
| Seher, Ferhat, Umut | CC Bot Wallet | |
| Ivan Reif | Tenkai / Cansai | Mitch handover risk per registry |

If a contact appears in the pull who isn't on this list, search their domain or recent thread context before guessing the partner — and add them to this table when you're confident.

## Pitfalls

- **Anti-fabrication rule (most important).** If a partner name does not appear in the Slack/Notion pull for the date window, do not include them. Don't reach into memory, prior standups, or the partner registry for filler. An accurate 6-bullet section beats a fabricated 15-bullet one — Mayank will catch invented activity instantly and lose trust in the skill.
- **Don't bundle wins.** A Closed Won deserves its own bullet with `:tada:`. Don't fold MSA signatures into "CRM hygiene" — that buries the news.
- **Don't restate the morning brief verbatim.** The standup is Mayank's voice, not the brief's. Re-frame "QCP — score 65, ping Michelle EOD" as "QCP — copy delivered to Michelle AM IST; pinging EOD if no countersign motion".
- **Don't include cooldown prompts** — they're auto-generated to self, not real partner work.
- **Don't post directly.** Always show the draft and wait for "post it" before calling `slack_send_message`. He edits before posting more often than not.
- **Don't add a Blockers section.** He doesn't use one. If something's stuck, it goes inline under the partner.
- **Don't over-bundle.** Better to have a 15-bullet Today than a 6-bullet one that hides nudges he's owing. The standup is for accountability.
- **SciFeCap vs Excellar.** These can refer to the same partner via different workstreams. SciFeCap = the LP MSA entity; Excellar = the broader product/xlTokens conversation. Don't conflate them in a single bullet.
- **Don't pad "Today" with planned-but-unstarted items (strict rule).** Only include a Today bullet if the action is either (a) already done this morning, or (b) actively in flight with a concrete next step (e.g. waiting on a specific person who has already responded). Items from the morning brief that Mayank has NOT touched and has no concrete plan to start today get cut, even if they're long-overdue nudges. Observed pattern: Mayank routinely deletes 6+ "planned nudge" bullets from drafts because he won't actually send them today. Better to ship a 10-bullet Today that's all real than a 16-bullet Today that pretends.
- **No standalone internal-coordination bullets.** Team-only DMs that don't advance a partner outcome (e.g. "fyi @vinay", "check temple uptime", generic context-sharing with Aki/Kadeem/Jesse) do not belong in the standup. If an internal DM is load-bearing, fold it into the relevant partner bullet (e.g. Vala DM to Kadeem → goes inside the Vala bullet, not a separate "Internal coordination" line).
- **Check for completion before phrasing as pending.** Before writing a Today bullet like "Anna to send X" or "Bryan to do Y", re-scan Slack (the partner channel + the assignee's DM) for a same-day completion signal. If the action happened, phrase as past tense ("Anna sent X") instead. Stale pending framing makes the standup look like agent-padding rather than ground truth.
- **Multi-channel partners — Slack isn't the whole picture.** Some partners do significant work off Slack: Garden (Susruth) lives partially on Telegram + Notion drafts; legal-heavy deals move via Gmail + Google Docs. The skill can't see those signals. Before finalizing the draft, ask Mayank explicitly: "Anything on Telegram, email, or Notion drafts I should add?" Especially flag Garden, QCP (frequent Google Docs activity), and any partner where a Notion meeting note exists without a corresponding Slack thread.

## Output conventions

When presenting in chat:
- Wrap the full standup in a code block so Mayank can copy-paste cleanly
- Below the code block, list sources used (e.g. "12 Slack messages from May 13–14, 3 Notion meeting notes, this morning's CBTC brief")
- End with: "Want me to trim, adjust, or post to #business-development?"
- If sources felt thin (<5 Slack hits), say so and offer to widen the window or pull Gmail

## Future improvements (deferred — open these if the skill outgrows a single file)

Patterns proven in jackchuka/skills, ryanb/dotfiles, and anthropics/skills/internal-comms that would make this skill more robust but add files/state to manage:

1. **`references/agent-gather-slack.md` + `references/agent-gather-notion.md`** — externalize each data source into its own subagent-dispatchable reference file with exact MCP query syntax. Enables parallel fan-out and keeps SKILL.md lean. Adopt when SKILL.md exceeds ~400 lines.
2. **`examples/mayank-standup.md`** — ship two real worked examples (e.g. Apr 28 + May 8 posts) alongside the voice rules from `feedback_writing_style_mayank.md`. Anchors output style and prevents drift.
3. **`~/.claude/bd-standup.json` side-car config** — `partner_aliases` (e.g. `{"SciFeCap":["Scifecap","scifecap","sci fe cap"]}`), `channel_allowlist`, `channel_excluded`, `notion_databases`. Lets the user tweak filters without forking the skill.
4. **`~/.claude/bd-standup-last-timestamp` cursor file** — write on every successful run; read on next invocation as the "since" cursor. Solves the Monday-duplicate-emission problem cleanly and lets `/standup` be invoked on demand without re-emitting prior content.
5. **10-query trigger eval** — 5 should-trigger phrasings + 5 near-miss should-not-triggers (engineering standup, weekly sales brief, "what should I work on"). Run via `anthropic-skills:skill-creator` evals to auto-tune the description field.

References:
- [jackchuka/skills p-daily-standup](https://github.com/jackchuka/skills/tree/main/p-daily-standup) — multi-source agent-gather pattern
- [ryanb/dotfiles standup](https://github.com/ryanb/dotfiles/tree/main/claude/skills/standup) — side-car config + last-timestamp cursor
- [anthropics/skills internal-comms](https://github.com/anthropics/skills/tree/main/skills/internal-comms) — examples/ directory pattern
- [obra/superpowers writing-skills](https://github.com/obra/superpowers/blob/main/skills/writing-skills/SKILL.md) — description-field anti-patterns
