---
name: fathom-mcp
description: "Fathom MCP for querying meeting recordings, transcripts, AI summaries, and attendee data. Use this skill whenever the user wants to fetch, search, or analyze meeting notes; pull recaps of recurring team calls (sales, product, L10/Ninety, town hall, marketing, 1:1s); search across meetings for a topic, decision, or quote; find which meetings a specific person attended; compile multi-meeting roll-ups; or extract action items from past calls. Trigger on: Fathom, meeting notes, meeting recap, transcript, recording, what did we discuss, what was decided, action items from [meeting], find the meeting where, summary of [call], notes from last [meeting], recurring team calls, weekly sales/product/marketing/townhall, L10 / Ninety, call with [person], pull meetings, search meetings, list meetings, get transcript, get summary. Prefer this skill over Granola for Fathom-recorded meetings — Granola is a separate MCP and team meetings typically live in Fathom."
---

# Fathom MCP — Meeting Recordings, Transcripts, and Summaries

Fathom records team meetings and external calls, producing AI summaries, full transcripts, and attendee metadata. This skill covers all tools, when to use each, and patterns for common workflows.

## Server prefix and tool list

All tools are prefixed `mcp__9b7377c6-b973-4e6f-a8e0-041a155a9ae4__`. Tools are **deferred** — load schemas via `ToolSearch` before calling them. Bulk-load by prefix:

```
ToolSearch query="select:mcp__9b7377c6-b973-4e6f-a8e0-041a155a9ae4__list_meetings,mcp__9b7377c6-b973-4e6f-a8e0-041a155a9ae4__search_meetings,mcp__9b7377c6-b973-4e6f-a8e0-041a155a9ae4__get_meeting_summary,mcp__9b7377c6-b973-4e6f-a8e0-041a155a9ae4__get_meeting_transcript,mcp__9b7377c6-b973-4e6f-a8e0-041a155a9ae4__find_person,mcp__9b7377c6-b973-4e6f-a8e0-041a155a9ae4__get_identity,mcp__9b7377c6-b973-4e6f-a8e0-041a155a9ae4__get_recording_by_call_id,mcp__9b7377c6-b973-4e6f-a8e0-041a155a9ae4__get_recording_by_url,mcp__9b7377c6-b973-4e6f-a8e0-041a155a9ae4__list_teams"
```

Only load what you actually need — `list_meetings` + `get_meeting_summary` covers most workflows.

| Tool | Purpose | Returns |
|---|---|---|
| `list_meetings` | Filter meetings by date/recorder/team | recording_id, title, url, recorded_by, calendar_invitees |
| `search_meetings` | Keyword search across titles + summaries (AND logic) | matching meetings with summary snippets |
| `get_meeting_summary` | AI summary for a specific meeting | structured summary with timestamped deep links |
| `get_meeting_transcript` | Full verbatim transcript | speaker-segmented transcript with `[MM:SS](url?timestamp=N)` links |
| `find_person` | Find meetings attended by a specific person | meetings filtered by attendee |
| `get_identity` | Current user identity | authenticated user info |
| `get_recording_by_call_id` | Lookup by Fathom call ID | meeting metadata |
| `get_recording_by_url` | Lookup by fathom.video URL | meeting metadata |
| `list_teams` | List Fathom team names | team identifiers for filtering |

## Decision tree — pick the right tool

```
What does the user want?

├─ Notes from a specific recurring meeting (e.g. "last week's sales call")
│  → list_meetings (filter by date window) → match title → get_meeting_summary
│
├─ Find meetings about a TOPIC (e.g. "what did we discuss about pricing?")
│  → search_meetings (query=keywords, recorded_by="anyone")
│
├─ Find meetings with a PERSON (e.g. "calls with Michelle Chong")
│  → find_person → list returned meetings → get_meeting_summary per relevant call
│
├─ Pull EXACT QUOTES or verbatim discussion
│  → get_meeting_transcript (max 3 per query — transcripts are large)
│
├─ Compile multiple meetings into a roll-up
│  → list_meetings (date range) → categorize by title → get_meeting_summary in parallel
│
└─ Lookup by Fathom URL or call ID (e.g. user pastes a link)
   → get_recording_by_url or get_recording_by_call_id
```

## Tool reference

### `list_meetings` — primary lister

Use when you need meetings in a date window or by a specific recorder.

**Key parameters:**
- `created_after`, `created_before` — ISO datetime (e.g. `2026-04-27T00:00:00Z`)
- `recorded_by` — array of emails to filter by recorder. Omit to get all accessible meetings.
- `teams` — filter by team name (call `list_teams` first to get valid names)
- `include_summary` — `true` to embed AI summary per meeting (useful for analytical sweeps)
- `include_action_items` — `true` to embed action items
- `max_pages` — default 1, use 3–5 for "all meetings this month" type queries
- `cursor` — pagination from previous `next_cursor`

**Important:** Each page returns ~10 results. For a 2-week window in an active org, you'll likely need `max_pages: 5+`. Watch for `next_cursor` in the response — if present, more results exist.

**Does NOT scan content.** For topic search use `search_meetings`. For person-based filtering use `find_person`.

### `search_meetings` — keyword search

Use when looking for a topic, decision, or idea across meetings.

**Required parameters:**
- `query` — keywords (AND logic — all words must appear in title or summary)
- `recorded_by` — `"anyone"` for org-wide search, OR a specific email for that user's recordings only

**When the user says "my meetings about X"** → `recorded_by` = user's email.
**When the user says "any meeting about X" or topic-only** → `recorded_by` = `"anyone"`.
**When ambiguous** → prefer `"anyone"` for broader results.

**Quirk:** For queries like "Rich's idea about pricing" — use the TOPIC keywords as the query, not the person's name. The query matches against the meeting body, and the speaker's name may not literally appear in the summary.

### `get_meeting_summary` — AI summary

Use when the user wants a recap, action items, or decisions from a known meeting. This is the **default** for note retrieval — much smaller than transcripts and includes structured sections (purpose, key takeaways, topics, next steps) with timestamped deep links into the recording.

Required: `recording_id` (from `list_meetings` or `search_meetings`).

### `get_meeting_transcript` — full verbatim

Use ONLY when the user needs exact quotes, specific wording, or wants to review what was literally said.

- Required: `recording_id`
- Optional but recommended: `url` — pass the meeting URL so the transcript includes clickable `[MM:SS](url?timestamp=secs)` deep links per speaker segment
- **Cap: 3 transcripts per query.** They're large and will blow up context. If the user wants notes from 5+ meetings, use summaries, not transcripts.

### `find_person`, `list_teams`, `get_identity`, `get_recording_by_*`

Less common but useful:
- `find_person` — when filtering by attendee (e.g. "all my calls with Michelle Chong this month")
- `list_teams` — call this BEFORE using `teams=[...]` in `list_meetings`, since you need the exact team names
- `get_identity` — fetch the authenticated user's email if you need it for `recorded_by`
- `get_recording_by_url` / `get_recording_by_call_id` — when the user pastes a Fathom link or call ID and you need the recording_id for follow-up calls

## Common patterns

### Pattern 1: Last N days of a recurring meeting

```
1. list_meetings(created_after=<N days ago>, created_before=<now>, max_pages=5)
2. Filter results by title pattern (case-insensitive substring match)
3. For each match: get_meeting_summary(recording_id)
4. Compile into markdown — H2 per meeting type, H3 per instance, chronological
```

Title patterns for BitSafe recurring calls (case-insensitive substring):
- **Weekly Sales** → `sales`, `weekly sales`
- **Weekly Product Review** → `product call`, `product review`, `weekly product`
- **Town Hall** → `town hall`, `townhall`, `all hands`, `all-hands`
- **L10 / Ninety** → `L10`, `ninety`, `leadership`, `level 10`
- **Marketing** → `marketing`

### Pattern 2: Topic search across the org

```
search_meetings(query="<keywords>", recorded_by="anyone", max_pages=5)
```

If too many results, narrow with `created_after`. If too few, simplify the keywords (remember: AND logic — every word must appear).

### Pattern 3: Multi-meeting roll-up (parallelize)

When pulling 5+ summaries, batch them in a single message with multiple `get_meeting_summary` calls in parallel. Don't sequentialize — there's no shared state between calls.

### Pattern 4: Coverage audit for recurring meetings

When the user asks "did we have all our recurring meetings this week?":
1. `list_meetings` over the window
2. Categorize by title patterns
3. Count found vs expected per category
4. Flag categories with 0 hits or specific missing dates

## Pitfalls

- **Don't fetch transcripts in bulk.** Always default to summaries. Transcripts are for verbatim quote retrieval.
- **`recorded_by` must be set on `search_meetings`** — there's no default. Use `"anyone"` for org-wide search.
- **Pagination is opt-in.** A single page is ~10 results. For "all meetings this month" type queries, set `max_pages` 5–10 or follow `next_cursor`.
- **Granola is a separate MCP.** Team meetings recorded by Fathom won't appear in Granola, and vice versa. If a recurring team meeting isn't in Fathom, check Granola (server prefix `mcp__73b8d537-cb0c-4fee-a5c0-bf4dace57bec__`). 1:1s and personal notes often live in Granola, not Fathom.
- **The `find_person` tool is for finding meetings by attendee**, NOT for finding a person's contact info. Don't confuse it with a CRM lookup.
- **Title matching is approximate.** A "Weekly Sales Meeting" might also appear as "Sales sync" or "Weekly sales call" — be tolerant in pattern matching and surface possible matches when uncertain.

## Output conventions

When presenting meeting notes to the user:
- Always include the `https://fathom.video/calls/<id>` URL so they can jump to the recording
- Preserve timestamped deep links from summaries (`[MM:SS](url?timestamp=N)`) — they let the user verify quotes by clicking through
- Newest meetings first when listing chronologically
- Surface attendees, especially for external calls (helps the user remember context)
- When compiling roll-ups, end with a coverage note: "X of Y expected meetings found"
