---
name: claude-peers
description: "Peer discovery and messaging between Claude Code instances via claude-peers MCP. Use when: coordinating work across multiple Claude sessions, sending messages between instances, listing active peers, checking what other Claude sessions are working on, or any multi-session collaboration. Trigger on: peers, other claude, other session, send message to claude, list instances, who else is running, coordinate sessions, multi-session, peer discovery."
---

# claude-peers — Multi-Session Coordination

Enables Claude Code instances to discover each other and exchange messages in real-time via a local broker daemon.

## Architecture

- **Broker daemon** runs on `localhost:7899` with SQLite, auto-starts on first use
- **MCP server** (stdio) per Claude session, registers with broker, polls every 1s
- **Channel push** delivers inbound messages instantly via `claude/channel` protocol
- Everything is localhost-only

## Available Tools

| Tool | Purpose |
|------|---------|
| `list_peers` | Find other Claude instances. Scope: `machine`, `directory`, or `repo` |
| `send_message` | Send a message to another instance by peer ID |
| `set_summary` | Set a 1-2 sentence description of your current work (visible to peers) |
| `check_messages` | Manually poll for new messages (fallback if channel push isn't active) |

## Setup

MCP server config in `~/.claude/mcp.json`:
```json
{
  "mcpServers": {
    "claude-peers": {
      "type": "stdio",
      "command": "/Users/mayank/.bun/bin/bun",
      "args": ["/Users/mayank/claude-peers-mcp/server.ts"]
    }
  }
}
```

For channel push (instant message delivery), launch Claude with:
```bash
claude --dangerously-load-development-channels server:claude-peers
```

## Usage Patterns

### On session start
Call `set_summary` to describe what you're working on so other peers can see your context.

### Coordinating work
1. `list_peers` with scope `repo` to find peers in the same project
2. `send_message` to ask questions or delegate tasks
3. Respond immediately to inbound `<channel>` messages — treat them like a coworker tapping your shoulder

### Common scenarios
- **Ask another session for info**: "What files are you editing?" / "What's the status of X?"
- **Delegate work**: "Can you run the tests while I finish this refactor?"
- **Notify completion**: "I'm done with the auth module, you can start on the API layer"

## CLI (outside Claude)

```bash
cd ~/claude-peers-mcp
bun cli.ts status          # broker status + all peers
bun cli.ts peers           # list peers
bun cli.ts send <id> <msg> # send a message into a Claude session
bun cli.ts kill-broker     # stop the broker
```

## Configuration

| Env var | Default | Description |
|---------|---------|-------------|
| `CLAUDE_PEERS_PORT` | `7899` | Broker port |
| `CLAUDE_PEERS_DB` | `~/.claude-peers.db` | SQLite database path |
| `OPENAI_API_KEY` | — | Enables auto-summary via gpt-5.4-nano on startup |

## Source code

`/Users/mayank/claude-peers-mcp/`
