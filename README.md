# mojo-skills

Personal Claude Code skills collection. Clone and install on any device to get all skills.

## Quick Install

```bash
git clone git@github.com:mayank/mojo-skills.git
cd mojo-skills
./install.sh
```

Restart Claude Code after installing.

## Skills

| Skill | What it does |
|-------|-------------|
| **vibe-check** | Structured idea evaluation — research, cost-benefit, milestones with exit gates, security review |
| **cbtc-dashboard** | CBTC Activity Tracker API for reward dashboards and transfer analytics |
| **ccview-api** | CC View Canton block explorer API for on-chain data queries |
| **claude-peers** | Peer discovery and messaging between Claude Code instances |
| **codebase-to-course** | Turn any codebase into an interactive HTML course |
| **loop-sgk-sdk** | Loop Wallet SDK and Splice Wallet Kernel for Canton dApp development |
| **promptfoo-evals** | Create and manage promptfoo evaluation suites |
| **ps-control** | PS5 DualSense controller button mapping for ControllerKeys app |
| **temple-canton-sdk** | Temple Canton JS SDK for institutional trading on Canton Network |
| **zoro-wallet-api** | Zoro Wallet API for Canton on-chain wallet operations |
| **agentic-gateway** | Alchemy blockchain APIs with multiple auth methods |
| **alchemy-api** | Alchemy blockchain APIs using API key |
| **fathom-mcp** | Query Fathom meeting recordings, transcripts, AI summaries, and attendees |
| **bd-standup** | Generate Mayank's daily BD stand-up in his canonical Yesterday/Today format from Slack + Notion |

## Scheduled Tasks

| Task | What it does |
|------|-------------|
| **cnews-content-writer** | Research and publish Canton Network news articles |
| **cnews-context-feed** | Weekly Canton ecosystem context injection |
| **cnews-seo-biweekly** | Biweekly SEO analytics review |
| **cnews-seo-weekly** | Weekly SEO audit for cnews.dev |

## How It Works

`install.sh` creates symlinks from this repo into `~/.claude/skills/` and `~/.claude/scheduled-tasks/`. Changes you make in the repo are automatically picked up.

To update on any device: `git pull` — symlinks mean changes propagate immediately.

## Uninstall

Remove the symlinks (not the repo):
```bash
cd ~/.claude/skills && find . -maxdepth 1 -type l -delete
cd ~/.claude/scheduled-tasks && find . -maxdepth 1 -type l -delete
```
