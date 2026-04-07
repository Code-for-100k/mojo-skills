---
name: cnews-context-feed
description: Weekly Canton ecosystem context injection from Slack/Notion to Andy's VPS
---

You are updating Andy's context feed for CNews (cnews.dev). Andy is a NanoClaw agent on a VPS that runs the CNews Canton Network news site.

Your job:
1. Search Slack for Canton ecosystem news from the past week using slack_search_public with queries like "canton network", "canton coin", "CC price", "CBTC", "canton ecosystem", "canton validator", "canton defi"
2. Search Notion for any Canton-related pages updated in the past week
3. Filter out internal BitSafe business stuff (MSA terms, internal metrics, partner deals). Only include publicly relevant ecosystem news.
4. Write a summary to the VPS at /home/deploy/cnews-cc/.claude/context-feed.md

Format the file as:
```
# Context Feed
*Updated: [date] by Claude Code*

## This Week's Canton Ecosystem Intel

### News & Announcements
- [bullet points of notable announcements, launches, partnerships]

### Market & Data
- [CC price movements, volume trends, TVL changes]

### Ecosystem Updates  
- [new apps, validators, governance proposals]

### Article Opportunities
- [topics Andy should consider writing about based on this intel]
```

Push the file via SSH:
ssh -i ~/.ssh/nanoclaw-cnews deploy@159.69.36.53

Write the content to /home/deploy/cnews-cc/.claude/context-feed.md